param(
  [string]$Base = "https://facundocapello-blip.github.io/Mambapalabra/",
  [switch]$Full,
  [int]$Sample = 10
)

$ErrorActionPreference = "Stop"
$fallas = New-Object System.Collections.Generic.List[string]

function Get-Remote {
  param([string]$Url, [string]$Out)
  Invoke-WebRequest -Uri $Url -OutFile $Out -UseBasicParsing -TimeoutSec 30
}

Write-Host "== Mambapalabra: $Base ==" -ForegroundColor Cyan

# 1. Index responde y es el build esperado.
$idx = Join-Path $env:TEMP ("mb_index_" + [guid]::NewGuid().ToString("N") + ".html")
try {
  $head = Invoke-WebRequest -Uri $Base -Method Head -UseBasicParsing -TimeoutSec 30
  Get-Remote -Url $Base -Out $idx
  $html = [System.IO.File]::ReadAllText($idx)
  Write-Host "index: $($head.StatusCode) ($([math]::Round($html.Length/1024)) KB)" -ForegroundColor Green
} catch {
  $fallas.Add("index -> $($_.Exception.Message)")
  Write-Host "index: FALLA" -ForegroundColor Red
  $html = ""
} finally {
  if (Test-Path $idx) { Remove-Item $idx -Force }
}

if ($html -and $html -notmatch 'B1\.13') {
  $fallas.Add("index no muestra B1.13 (build viejo o pagina de error)")
}

# 2. Assets: hash contra ASSETS_SHA256.json.
$manifestPath = Join-Path $PSScriptRoot "..\ASSETS_SHA256.json"
if (-not (Test-Path $manifestPath)) {
  $fallas.Add("no encuentro ASSETS_SHA256.json")
} else {
  $map = Get-Content $manifestPath -Raw | ConvertFrom-Json
  $keys = @($map.PSObject.Properties.Name)
  $total = $keys.Count

  if ($Full) {
    $objetivo = $keys
  } else {
    $step = [math]::Max(1, [math]::Floor($total / [math]::Max(1, $Sample)))
    $objetivo = @()
    for ($i = 0; $i -lt $total; $i += $step) { $objetivo += $keys[$i] }
    $objetivo = $objetivo | Select-Object -First $Sample
  }

  Write-Host "assets: revisando $($objetivo.Count) de $total" -ForegroundColor Cyan
  $ok = 0
  foreach ($rel in $objetivo) {
    $esperado = ([string]$map.$rel).ToLower()
    $tmp = Join-Path $env:TEMP ("mb_" + [guid]::NewGuid().ToString("N") + ".bin")
    try {
      Get-Remote -Url ($Base.TrimEnd("/") + "/" + $rel) -Out $tmp
      $real = (Get-FileHash $tmp -Algorithm SHA256).Hash.ToLower()
      if ($real -eq $esperado) { $ok++ } else { $fallas.Add("$rel -> hash distinto") }
    } catch {
      $fallas.Add("$rel -> $($_.Exception.Message)")
    } finally {
      if (Test-Path $tmp) { Remove-Item $tmp -Force }
    }
  }
  Write-Host "assets OK: $ok / $($objetivo.Count)" -ForegroundColor Green
}

Write-Host ""
if ($fallas.Count -eq 0) {
  Write-Host "SMOKE OK" -ForegroundColor Green
  exit 0
}
Write-Host "SMOKE FALLA ($($fallas.Count))" -ForegroundColor Red
$fallas | ForEach-Object { Write-Host " - $_" -ForegroundColor Yellow }
exit 1
