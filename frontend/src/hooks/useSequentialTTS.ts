import { useState, useRef, useCallback, useEffect } from 'react';

const EMOJI_REGEX =
  /[\u{1F600}-\u{1F6FF}\u{1F300}-\u{1F5FF}\u{1F900}-\u{1F9FF}\u{1F1E0}-\u{1F1FF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}\u{FE00}-\u{FE0F}]/gu;

type PlayState = 'idle' | 'playing' | 'paused';

export function useSequentialTTS(rate: number) {
  const [playState, setPlayState] = useState<PlayState>('idle');
  const [currentIndex, setCurrentIndex] = useState(-1);
  const [totalCount, setTotalCount] = useState(0);

  const rateRef = useRef(rate);
  rateRef.current = rate;

  const textsRef = useRef<string[]>([]);
  const indexRef = useRef(-1);
  const genRef = useRef(0);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const abortRef = useRef<AbortController | null>(null);

  const cleanupAudio = useCallback(() => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current = null;
    }
  }, []);

  const cancelFetch = useCallback(() => {
    if (abortRef.current) {
      abortRef.current.abort();
      abortRef.current = null;
    }
  }, []);

  const playAtIndex = useCallback(async (index: number) => {
    const texts = textsRef.current;
    if (index < 0 || index >= texts.length) {
      // playback complete
      indexRef.current = -1;
      setCurrentIndex(-1);
      setPlayState('idle');
      setTotalCount(0);
      textsRef.current = [];
      return;
    }

    const text = texts[index].replace(EMOJI_REGEX, '').trim();
    if (!text) {
      indexRef.current = index + 1;
      setCurrentIndex(index + 1);
      playAtIndex(index + 1);
      return;
    }

    genRef.current += 1;
    const gen = genRef.current;
    indexRef.current = index;
    setCurrentIndex(index);

    try {
      const controller = new AbortController();
      abortRef.current = controller;

      const params = new URLSearchParams({ text, rate: String(rateRef.current) });
      const resp = await fetch(`/api/tts?${params}`, { signal: controller.signal });
      if (genRef.current !== gen) return;

      if (!resp.ok) throw new Error(`TTS request failed: ${resp.status}`);

      const blob = await resp.blob();
      if (genRef.current !== gen) return;

      const url = URL.createObjectURL(blob);
      const audio = new Audio(url);
      audioRef.current = audio;

      audio.onended = () => {
        URL.revokeObjectURL(url);
        if (genRef.current !== gen) return;
        audioRef.current = null;
        const next = indexRef.current + 1;
        playAtIndex(next);
      };

      audio.onerror = () => {
        URL.revokeObjectURL(url);
        if (genRef.current !== gen) return;
        audioRef.current = null;
        const next = indexRef.current + 1;
        playAtIndex(next);
      };

      await audio.play();
    } catch (err) {
      if (err instanceof DOMException && err.name === 'AbortError') return;
      console.error('Sequential TTS play failed:', err);
      // skip this sentence and try next
      audioRef.current = null;
      if (genRef.current !== gen) return;
      const next = indexRef.current + 1;
      playAtIndex(next);
    }
  }, []);

  const stopInternal = useCallback(() => {
    genRef.current += 1;
    cancelFetch();
    cleanupAudio();
    textsRef.current = [];
    indexRef.current = -1;
    setCurrentIndex(-1);
    setPlayState('idle');
    setTotalCount(0);
  }, [cancelFetch, cleanupAudio]);

  const play = useCallback((texts: string[], startIndex = 0) => {
    stopInternal();
    textsRef.current = texts;
    setTotalCount(texts.length);
    if (texts.length === 0) return;
    const start = Math.max(0, Math.min(startIndex, texts.length - 1));
    setPlayState('playing');
    playAtIndex(start);
  }, [stopInternal, playAtIndex]);

  const pause = useCallback(() => {
    if (audioRef.current) {
      audioRef.current.pause();
    }
    setPlayState('paused');
  }, []);

  const resume = useCallback(() => {
    if (audioRef.current) {
      audioRef.current.play();
    }
    setPlayState('playing');
  }, []);

  const next = useCallback(() => {
    genRef.current += 1;
    cancelFetch();
    cleanupAudio();
    const i = Math.min(indexRef.current + 1, textsRef.current.length - 1);
    if (i >= 0 && textsRef.current.length > 0) {
      setPlayState('playing');
      playAtIndex(i);
    }
  }, [cancelFetch, cleanupAudio, playAtIndex]);

  const prev = useCallback(() => {
    genRef.current += 1;
    cancelFetch();
    cleanupAudio();
    const i = Math.max(indexRef.current - 1, 0);
    if (i >= 0 && textsRef.current.length > 0) {
      setPlayState('playing');
      playAtIndex(i);
    }
  }, [cancelFetch, cleanupAudio, playAtIndex]);

  const stop = useCallback(() => {
    stopInternal();
  }, [stopInternal]);

  useEffect(() => {
    return () => {
      stopInternal();
    };
  }, [stopInternal]);

  return { playState, currentIndex, totalCount, play, pause, resume, next, prev, stop };
}
