/**
 * AudioProcessingWorklet
 * Captures microphone stream, converts Float32 [-1.0, 1.0] to 16-bit Int16 PCM,
 * and posts 2048-sample chunks to the main thread for streaming to Gemini Live API.
 */
class AudioProcessingWorklet extends AudioWorkletProcessor {
  constructor() {
    super();
    // 2048 samples at 16kHz is ~128ms per packet
    this.buffer = new Int16Array(2048);
    this.bufferWriteIndex = 0;
  }

  process(inputs) {
    if (inputs[0] && inputs[0].length > 0) {
      const channel0 = inputs[0][0];
      this.processChunk(channel0);
    }
    return true;
  }

  sendAndClearBuffer() {
    if (this.bufferWriteIndex === 0) return;
    
    // Slice only written portion
    const chunk = this.buffer.slice(0, this.bufferWriteIndex);
    this.port.postMessage({
      event: 'chunk',
      data: chunk.buffer,
    }, [chunk.buffer]); // Transfer buffer for zero-copy performance

    this.bufferWriteIndex = 0;
  }

  processChunk(float32Array) {
    const len = float32Array.length;
    for (let i = 0; i < len; i++) {
      // Clamp float32 between -1 and 1
      const s = Math.max(-1, Math.min(1, float32Array[i]));
      // Convert to Int16 range [-32768, 32767]
      this.buffer[this.bufferWriteIndex++] = s < 0 ? s * 0x8000 : s * 0x7fff;

      if (this.bufferWriteIndex >= this.buffer.length) {
        this.sendAndClearBuffer();
      }
    }
  }
}

registerProcessor('audio-processing-worklet', AudioProcessingWorklet);
