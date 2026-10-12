-- New, isolated STAGING database only. No production data or migration.
create schema if not exists extensions;
create extension if not exists pgcrypto with schema extensions;
create schema if not exists mamba_private;

create table public.multiplayer_rooms (
  code text primary key check (code ~ '^[A-Z0-9]{6}$'),
  host_name text not null,
  guest_name text,
  version bigint not null default 1,
  status text not null default 'waiting' check (status in ('waiting','playing','finished')),
  game_state jsonb not null default '{}',
  expires_at timestamptz not null default (now() + interval '2 hours')
);
alter table public.multiplayer_rooms enable row level security;
-- Public state only; capability tokens never enter this table or realtime.
create policy staging_room_read on public.multiplayer_rooms for select to anon, authenticated using (expires_at > now());
grant select on public.multiplayer_rooms to anon, authenticated;
revoke insert, update, delete on public.multiplayer_rooms from anon, authenticated;

create table mamba_private.room_tokens (
  code text primary key references public.multiplayer_rooms(code) on delete cascade,
  host_hash text not null,
  guest_hash text
);
create table mamba_private.operations (
  code text references public.multiplayer_rooms(code) on delete cascade,
  op_id text not null,
  payload_hash text not null,
  version bigint not null,
  primary key (code, op_id)
);
revoke all on schema mamba_private from public, anon, authenticated;
revoke all on all tables in schema mamba_private from public, anon, authenticated;

create function public.mamba_staging_action(payload jsonb) returns jsonb
language plpgsql security definer set search_path = '' as $$
declare
  action text := payload->>'action';
  requested_code text := upper(payload->>'code');
  room public.multiplayer_rooms%rowtype;
  tokens mamba_private.room_tokens%rowtype;
  op mamba_private.operations%rowtype;
  token text;
  token_hash text;
  role_name text := payload->>'role';
  slot integer;
  st jsonb := payload->'game_state';
  requested_op_id text := st->>'opId';
  hash text;
begin
  if octet_length(payload::text) > 131072 then return jsonb_build_object('error','payload_too_large'); end if;
  delete from public.multiplayer_rooms where expires_at <= now();
  if action = 'create' then
    -- Explicit staging cap; this function never provisions resources.
    perform pg_catalog.pg_advisory_xact_lock(1112026);
    if (select count(*) from public.multiplayer_rooms) >= 100 then return jsonb_build_object('error','staging_room_limit'); end if;
    requested_code := upper(substr(encode(extensions.gen_random_bytes(8),'hex'),1,6));
    token := pg_catalog.gen_random_uuid()::text;
    token_hash := encode(extensions.digest(token,'sha256'),'hex');
    insert into public.multiplayer_rooms(code,host_name,game_state)
      values(requested_code,left(coalesce(nullif(trim(payload->>'name'),''),'Jugador 1'),18),coalesce(st,'{}')) returning * into room;
    insert into mamba_private.room_tokens(code,host_hash) values(requested_code,token_hash);
    return jsonb_build_object('code',requested_code,'token',token);
  end if;
  select * into room from public.multiplayer_rooms where code=requested_code for update;
  if not found then return jsonb_build_object('error','room_not_found'); end if;
  if action = 'get' then return jsonb_build_object('room',to_jsonb(room)); end if;
  if action = 'join' then
    if room.guest_name is not null then return jsonb_build_object('error','room_full'); end if;
    token := pg_catalog.gen_random_uuid()::text;
    update public.multiplayer_rooms set guest_name=left(coalesce(nullif(trim(payload->>'name'),''),'Jugador 2'),18),version=version+1 where code=requested_code;
    update mamba_private.room_tokens set guest_hash=encode(extensions.digest(token,'sha256'),'hex') where code=requested_code;
    return jsonb_build_object('code',requested_code,'token',token);
  end if;
  if role_name not in ('host','guest') or role_name is null then return jsonb_build_object('error','unauthorized'); end if;
  select * into tokens from mamba_private.room_tokens where code=requested_code;
  token_hash := encode(extensions.digest(coalesce(payload->>'token',''),'sha256'),'hex');
  if token_hash is distinct from (case when role_name='host' then tokens.host_hash else tokens.guest_hash end) then
    return jsonb_build_object('error','unauthorized');
  end if;
  if action = 'resume' then return jsonb_build_object('room',to_jsonb(room)); end if;
  if action <> 'sync' then return jsonb_build_object('error','invalid_action'); end if;
  if requested_op_id is null or length(requested_op_id)>128 then return jsonb_build_object('error','invalid_operation'); end if;
  hash := encode(extensions.digest(st::text,'sha256'),'hex');
  select * into op from mamba_private.operations where code=requested_code and operations.op_id=requested_op_id;
  if found then
    if op.payload_hash <> hash then return jsonb_build_object('error','operation_conflict'); end if;
    return jsonb_build_object('version',op.version);
  end if;
  if payload->>'version' is distinct from room.version::text then return jsonb_build_object('error','version_conflict'); end if;
  slot := case when role_name='host' then 0 else 1 end;
  if room.status='finished' then
    if slot<>0 then return jsonb_build_object('error','not_turn_owner'); end if;
  elsif room.game_state ? 'players' then
    if (room.game_state->>'active')::integer <> slot then return jsonb_build_object('error','not_turn_owner'); end if;
  elsif slot<>0 or room.guest_name is null then return jsonb_build_object('error','not_turn_owner');
  end if;
  if jsonb_typeof(st->'players') is distinct from 'array' or jsonb_array_length(st->'players')<>2
     or coalesce(st->>'active','') not in ('0','1')
     or coalesce(st->>'turnState','') not in ('READING','ANSWERING','VALIDATING','SWITCHING')
     or coalesce(payload->>'status','') not in ('playing','finished') then
    return jsonb_build_object('error','invalid_game_state');
  end if;
  update public.multiplayer_rooms set game_state=st,status=payload->>'status',version=version+1 where code=requested_code returning * into room;
  insert into mamba_private.operations values(requested_code,requested_op_id,hash,room.version);
  delete from mamba_private.operations where code=requested_code and version < room.version-64;
  return jsonb_build_object('version',room.version);
exception when unique_violation then
  return jsonb_build_object('error','retry_create');
end;
$$;
revoke all on function public.mamba_staging_action(jsonb) from public, anon, authenticated;
grant execute on function public.mamba_staging_action(jsonb) to service_role;

-- Supabase Realtime is optional: the existing client also polls every 2 s.
do $$ begin
  if exists(select 1 from pg_publication where pubname='supabase_realtime') then
    alter publication supabase_realtime add table public.multiplayer_rooms;
  end if;
end $$;
