import { useCallback, useEffect, useRef } from 'react';

const EMOJI_REGEX =
  /[\u{1F600}-\u{1F6FF}\u{1F300}-\u{1F5FF}\u{1F900}-\u{1F9FF}\u{1F1E0}-\u{1F1FF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}\u{FE00}-\u{FE0F}]/gu;

function removeEmojis(text: string): string {
  return text.replace(EMOJI_REGEX, '').trim();
}

export function useSpeechSynthesis(speechRate: number) {
  const rateRef = useRef(speechRate);
  rateRef.current = speechRate;
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const abortRef = useRef(0);

  const cancelPrevious = useCallback(() => {
    abortRef.current += 1;
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current = null;
    }
  }, []);

  const speak = useCallback(async (text: string) => {
    if (!text) return;
    const clean = removeEmojis(text);
    if (!clean) return;

    cancelPrevious();
    const gen = abortRef.current;

    try {
      const params = new URLSearchParams({ text: clean, rate: String(rateRef.current) });
      const resp = await fetch(`/api/tts?${params}`);
      if (abortRef.current !== gen) return;

      if (!resp.ok) throw new Error(`TTS request failed: ${resp.status}`);

      const blob = await resp.blob();
      if (abortRef.current !== gen) return;

      const url = URL.createObjectURL(blob);
      const audio = new Audio(url);
      audioRef.current = audio;

      audio.onended = () => {
        URL.revokeObjectURL(url);
        if (audioRef.current === audio) audioRef.current = null;
      };

      await audio.play();
    } catch (err) {
      console.error('TTS play failed:', err);
      if (audioRef.current) {
        audioRef.current = null;
      }
    }
  }, [cancelPrevious]);

  useEffect(() => {
    return () => {
      abortRef.current += 1;
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current = null;
      }
    };
  }, []);

  return speak;
}
