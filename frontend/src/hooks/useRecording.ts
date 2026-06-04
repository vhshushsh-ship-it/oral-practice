import { useState, useRef, useCallback } from 'react';

function formatTime(seconds: number): string {
  const m = Math.floor(seconds / 60)
    .toString()
    .padStart(2, '0');
  const s = (seconds % 60).toString().padStart(2, '0');
  return `${m}:${s}`;
}

function resample(audioData: Float32Array, fromRate: number, toRate: number): Float32Array {
  const ratio = fromRate / toRate;
  const newLength = Math.round(audioData.length / ratio);
  const result = new Float32Array(newLength);
  for (let i = 0; i < newLength; i++) {
    const index = i * ratio;
    const floor = Math.floor(index);
    const ceil = Math.ceil(index);
    const t = index - floor;
    result[i] =
      ceil >= audioData.length
        ? audioData[floor]
        : audioData[floor] * (1 - t) + audioData[ceil] * t;
  }
  return result;
}

function createWavBlob(audioData: Float32Array, sampleRate: number): Blob {
  const targetRate = 16000;
  const ratio = sampleRate / targetRate;
  const newLength = Math.round(audioData.length / ratio);
  const resampled = new Float32Array(newLength);
  for (let i = 0; i < newLength; i++) {
    const idx = i * ratio;
    const floor = Math.floor(idx);
    const ceil = Math.min(Math.ceil(idx), audioData.length - 1);
    const t = idx - floor;
    resampled[i] = audioData[floor] * (1 - t) + audioData[ceil] * t;
  }
  const pcm = new Int16Array(resampled.length);
  for (let i = 0; i < resampled.length; i++) {
    const s = Math.max(-1, Math.min(1, resampled[i]));
    pcm[i] = s < 0 ? s * 0x8000 : s * 0x7fff;
  }
  const buffer = new ArrayBuffer(44 + pcm.length * 2);
  const view = new DataView(buffer);
  view.setUint8(0, 0x52); view.setUint8(1, 0x49); view.setUint8(2, 0x46); view.setUint8(3, 0x46);
  view.setUint32(4, 36 + pcm.length * 2, true);
  view.setUint8(8, 0x57); view.setUint8(9, 0x41); view.setUint8(10, 0x56); view.setUint8(11, 0x45);
  view.setUint8(12, 0x66); view.setUint8(13, 0x6d); view.setUint8(14, 0x74); view.setUint8(15, 0x20);
  view.setUint32(16, 16, true);
  view.setUint16(20, 1, true);
  view.setUint16(22, 1, true);
  view.setUint32(24, targetRate, true);
  view.setUint32(28, targetRate * 2, true);
  view.setUint16(32, 2, true);
  view.setUint16(34, 16, true);
  view.setUint8(36, 0x64); view.setUint8(37, 0x61); view.setUint8(38, 0x74); view.setUint8(39, 0x61);
  view.setUint32(40, pcm.length * 2, true);
  for (let i = 0; i < pcm.length; i++) {
    view.setInt16(44 + i * 2, pcm[i], true);
  }
  return new Blob([view], { type: 'audio/wav' });
}

interface RecordingState {
  isRecording: boolean;
  seconds: number;
}

export function useRecording(onSend: (blob: Blob) => void) {
  const [state, setState] = useState<RecordingState>({ isRecording: false, seconds: 0 });
  const streamRef = useRef<MediaStream | null>(null);
  const contextRef = useRef<AudioContext | null>(null);
  const timerRef = useRef<number | null>(null);
  const chunksRef = useRef<Float32Array[]>([]);
  const cancelRef = useRef(false);

  const cleanup = useCallback(() => {
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
    streamRef.current?.getTracks().forEach((t) => t.stop());
    streamRef.current = null;
    contextRef.current?.close();
    contextRef.current = null;
    chunksRef.current = [];
    cancelRef.current = false;
  }, []);

  const start = useCallback(async () => {
    chunksRef.current = [];
    cancelRef.current = false;

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;
      const ctx = new (window.AudioContext || (window as any).webkitAudioContext)();
      contextRef.current = ctx;

      // Chrome 自动播放策略：await getUserMedia 后 AudioContext 可能处于 suspended 状态，
      // 必须显式 resume，否则 onaudioprocess 永远不会触发，导致录音数据为空
      if (ctx.state === 'suspended') {
        await ctx.resume();
      }

      const source = ctx.createMediaStreamSource(stream);
      const processor = ctx.createScriptProcessor(4096, 1, 1);
      // 通过零音量的 GainNode 连接到 destination，既保证 onaudioprocess 触发，
      // 又避免麦克风输入直通扬声器造成啸叫反馈
      const gainNode = ctx.createGain();
      gainNode.gain.value = 0;
      source.connect(processor);
      processor.connect(gainNode);
      gainNode.connect(ctx.destination);

      processor.onaudioprocess = (e: AudioProcessingEvent) => {
        const input = e.inputBuffer.getChannelData(0);
        chunksRef.current.push(new Float32Array(input));
      };

      setState({ isRecording: true, seconds: 0 });
      timerRef.current = window.setInterval(() => {
        setState((prev) => ({ ...prev, seconds: prev.seconds + 1 }));
      }, 1000);
    } catch (err) {
      console.error('录音失败:', err);
      cleanup();
    }
  }, [cleanup]);

  const stop = useCallback(() => {
    // Save data before cleanup clears refs
    const chunks = chunksRef.current;
    const sampleRate = contextRef.current?.sampleRate || 44100;
    const wasCancelled = cancelRef.current;

    cleanup();

    if (wasCancelled || chunks.length === 0) {
      setState({ isRecording: false, seconds: 0 });
      return;
    }

    const merged = (() => {
      let totalLen = 0;
      for (const ch of chunks) totalLen += ch.length;
      const merged = new Float32Array(totalLen);
      let offset = 0;
      for (const ch of chunks) {
        merged.set(ch, offset);
        offset += ch.length;
      }
      return merged;
    })();

    const wavBlob = createWavBlob(merged, sampleRate);
    setState({ isRecording: false, seconds: 0 });
    onSend(wavBlob);
  }, [cleanup, onSend]);

  const cancel = useCallback(() => {
    cancelRef.current = true;
    cleanup();
    setState({ isRecording: false, seconds: 0 });
  }, [cleanup]);

  return { state, start, stop, cancel, formatTime };
}
