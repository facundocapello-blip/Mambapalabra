// Only injected by the regression server; never shipped in the game.
window.audioMode = 'ok';
window.ttsMode = 'ok';
window.audioPlays = [];
window.ttsUtterances = [];
class TestAudio {
  currentTime = 0; duration = 1; playbackRate = 1; paused = true;
  setAttribute() {}
  play() {
    this.paused = false;
    window.audioPlays.push(this.src);
    if (window.audioMode === 'reject') return Promise.reject(new Error('audio unavailable'));
    if (window.audioMode === 'hang') return new Promise(() => {});
    setTimeout(() => {
      if (this.paused) return;
      this.onplaying?.();
      if (window.audioMode === 'stall') return;
      setTimeout(() => { if (!this.paused) this.onended?.(); }, 20);
    }, 10);
    return Promise.resolve();
  }
  pause() { this.paused = true; }
}
window.Audio = TestAudio;
window.SpeechSynthesisUtterance = class { constructor(text) { this.text = text; } };
const synth = {
  paused: false, utterance: null,
  getVoices: () => [],
  speak(u) {
    this.utterance = u; window.ttsUtterances.push(u);
    if (window.ttsMode === 'throw') throw new Error('TTS unavailable');
    if (window.ttsMode === 'hang') return;
    setTimeout(() => {
      if (this.utterance !== u || this.paused) return;
      if (window.ttsMode === 'error') { u.onerror?.(); return; }
      u.onstart?.();
      if (window.ttsMode === 'stall') return;
      setTimeout(() => { if (this.utterance === u && !this.paused) u.onend?.(); }, 20);
    }, 10);
  },
  cancel() { this.utterance = null; this.paused = false; },
  pause() { this.paused = true; },
  resume() { this.paused = false; },
};
Object.defineProperty(window, 'speechSynthesis', {value: synth, configurable: true});
window.SpeechRecognition = class {
  start() { window.lastRecognition = this; setTimeout(() => this.onstart?.(), 1); }
  stop() {} // Explicitly test engines that never deliver onend.
  abort() { if (!window.recognitionHangs) setTimeout(() => this.onend?.(), 1); }
};
