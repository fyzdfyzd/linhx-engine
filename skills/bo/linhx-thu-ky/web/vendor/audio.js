// AudioCapture — 16kHz PCM16 microphone capture via AudioWorklet
class AudioCapture {
  constructor(sampleRate = 16000) {
    this.sampleRate = sampleRate;
    this.onAudioData = null; // callback(base64PcmString)
    this.audioContext = null;
    this.stream = null;
    this.source = null;
    this.workletNode = null;
    this.level = 0;
    this.muted = false;
  }

  async start() {
    this.stream = await navigator.mediaDevices.getUserMedia({
      audio: { sampleRate: this.sampleRate, channelCount: 1, echoCancellation: true, noiseSuppression: true }
    });
    this.audioContext = new AudioContext({ sampleRate: this.sampleRate });
    await this.audioContext.resume();
    this.source = this.audioContext.createMediaStreamSource(this.stream);

    // Worklet served as a static file (CSP forbids blob: scripts).
    await this.audioContext.audioWorklet.addModule('/worklets/audio-recorder-worklet.js');
    this.workletNode = new AudioWorkletNode(this.audioContext, 'audio-processing-worklet');
    this.workletNode.port.onmessage = (ev) => {
      if (ev.data && ev.data.event === 'chunk' && this.onAudioData) {
        const pcm = new Int16Array(ev.data.data);
        let sum = 0;
        for (let i = 0; i < pcm.length; i++) { const v = pcm[i] / 32768; sum += v * v; }
        this.level = Math.sqrt(sum / Math.max(1, pcm.length));
        if (!this.muted) this.onAudioData(this._arrayBufferToBase64(ev.data.data));
      }
    };
    this.source.connect(this.workletNode);
    // Keep the graph pulled without making the mic audible.
    this.sink = this.audioContext.createGain();
    this.sink.gain.value = 0;
    this.workletNode.connect(this.sink).connect(this.audioContext.destination);
    console.log('[DEBUG][AudioCapture] Started 16kHz PCM capture');
  }

  stop() {
    if (this.workletNode) {
      // A MessagePort with a handler stays alive while entangled: release it explicitly (no leak across sessions).
      this.workletNode.port.onmessage = null;
      this.workletNode.port.close();
      this.workletNode.disconnect(); this.workletNode = null;
    }
    if (this.sink) { this.sink.disconnect(); this.sink = null; }
    if (this.source) { this.source.disconnect(); this.source = null; }
    if (this.stream) { this.stream.getTracks().forEach(t => t.stop()); this.stream = null; }
    if (this.audioContext) { this.audioContext.close(); this.audioContext = null; }
    console.log('[DEBUG][AudioCapture] Stopped');
  }

  mute() { this.muted = true; }
  unmute() { this.muted = false; }

  _arrayBufferToBase64(buffer) {
    const bytes = new Uint8Array(buffer);
    let binary = '';
    for (let i = 0; i < bytes.length; i += 0x8000) binary += String.fromCharCode.apply(null, bytes.subarray(i, i + 0x8000));
    return btoa(binary);
  }
}

// AudioPlayer — 24kHz scheduled PCM16 playback with barge-in support
class AudioPlayer {
  constructor(sampleRate = 24000) {
    this.sampleRate = sampleRate;
    this.audioContext = null;
    this.gainNode = null;
    this.audioQueue = [];
    this.scheduledTime = 0;
    this.isPlaying = false;
    this.checkInterval = null;
    this.onPlaybackStart = null;
    this.onPlaybackEnd = null;
    this.endOfQueueSource = null;
  }

  init() {
    this.audioContext = new AudioContext({ sampleRate: this.sampleRate });
    this.gainNode = this.audioContext.createGain();
    this.gainNode.connect(this.audioContext.destination);
    this.scheduledTime = this.audioContext.currentTime;
  }

  resume() { if (this.audioContext?.state === 'suspended') this.audioContext.resume(); }

  addPCM16(arrayBuffer) {
    if (!this.audioContext) this.init();
    this.resume();
    const float32 = this._pcm16ToFloat32(new Uint8Array(arrayBuffer));
    this.audioQueue.push(float32);
    if (!this.isPlaying) {
      this.isPlaying = true;
      this.scheduledTime = this.audioContext.currentTime + 0.1; // 100ms jitter buffer
      if (this.onPlaybackStart) this.onPlaybackStart();
    }
    this._scheduleNextBuffer();
  }

  _scheduleNextBuffer() {
    const AHEAD = 0.2;
    while (this.audioQueue.length > 0 && this.scheduledTime < this.audioContext.currentTime + AHEAD) {
      const data = this.audioQueue.shift();
      const buf = this.audioContext.createBuffer(1, data.length, this.sampleRate);
      buf.getChannelData(0).set(data);
      const src = this.audioContext.createBufferSource();
      src.buffer = buf;
      src.connect(this.gainNode);

      if (this.audioQueue.length === 0) {
        if (this.endOfQueueSource) this.endOfQueueSource.onended = null;
        this.endOfQueueSource = src;
        src.onended = () => {
          if (!this.audioQueue.length && this.endOfQueueSource === src) {
            this.endOfQueueSource = null;
            this.isPlaying = false;
            if (this.onPlaybackEnd) this.onPlaybackEnd();
          }
        };
      }

      const startTime = Math.max(this.scheduledTime, this.audioContext.currentTime);
      src.start(startTime);
      this.scheduledTime = startTime + buf.duration;
    }

    if (this.audioQueue.length > 0) {
      const delay = Math.max(0, (this.scheduledTime - this.audioContext.currentTime) * 1000 - 50);
      setTimeout(() => this._scheduleNextBuffer(), delay);
    } else if (!this.checkInterval) {
      this.checkInterval = setInterval(() => {
        if (this.audioQueue.length > 0) this._scheduleNextBuffer();
      }, 100);
    }
  }

  // CRITICAL: Barge-in support — smooth fade-out then clear
  clearQueue() {
    this.isPlaying = false;
    this.audioQueue = [];
    if (this.checkInterval) { clearInterval(this.checkInterval); this.checkInterval = null; }
    if (this.gainNode && this.audioContext) {
      this.scheduledTime = this.audioContext.currentTime;
      this.gainNode.gain.linearRampToValueAtTime(0, this.audioContext.currentTime + 0.1);
      setTimeout(() => {
        if (this.gainNode && this.audioContext) {
          this.gainNode.disconnect();
          this.gainNode = this.audioContext.createGain();
          this.gainNode.connect(this.audioContext.destination);
        }
      }, 200);
    }
    if (this.onPlaybackEnd) this.onPlaybackEnd();
    console.log('[DEBUG][AudioPlayer] Queue cleared (barge-in)');
  }

  stop() {
    this.clearQueue();
    if (this.audioContext) { this.audioContext.close(); this.audioContext = null; }
  }

  _pcm16ToFloat32(chunk) {
    const float32 = new Float32Array(chunk.length / 2);
    const dv = new DataView(chunk.buffer, chunk.byteOffset, chunk.byteLength);
    for (let i = 0; i < float32.length; i++) float32[i] = dv.getInt16(i * 2, true) / 32768;
    return float32;
  }

  // RMS volume level (0-1) for lip-sync
  getRMS(float32) {
    let sum = 0;
    for (let i = 0; i < float32.length; i++) sum += float32[i] * float32[i];
    return Math.sqrt(sum / float32.length);
  }
}
