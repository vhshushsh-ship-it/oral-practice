import { useCallback, useRef } from 'react';

const EMOJI_REGEX =
  /[\u{1F600}-\u{1F6FF}\u{1F300}-\u{1F5FF}\u{1F900}-\u{1F9FF}\u{1F1E0}-\u{1F1FF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}\u{FE00}-\u{FE0F}]/gu;

function removeEmojis(text: string): string {
  return text.replace(EMOJI_REGEX, '').trim();
}

export function useSpeechSynthesis(speechRate: number) {
  const rateRef = useRef(speechRate);
  rateRef.current = speechRate;
  const utteranceRef = useRef<SpeechSynthesisUtterance | null>(null);
  const speakTimerRef = useRef<number | null>(null);
  const joltTimerRef = useRef<number | null>(null);

  const clearTimers = useCallback(() => {
    if (speakTimerRef.current != null) {
      clearTimeout(speakTimerRef.current);
      speakTimerRef.current = null;
    }
    if (joltTimerRef.current != null) {
      clearTimeout(joltTimerRef.current);
      joltTimerRef.current = null;
    }
  }, []);

  const speak = useCallback((text: string) => {
    if (!text) return;
    const clean = removeEmojis(text);
    if (!clean) return;

    clearTimers();
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(clean);
    utterance.lang = 'en-US';
    utterance.rate = rateRef.current;
    utteranceRef.current = utterance;

    // Chrome speechSynthesis needs a small delay after cancel(),
    // and a pause+resume jolt to avoid its "silent stuck" bug.
    speakTimerRef.current = window.setTimeout(() => {
      speakTimerRef.current = null;
      window.speechSynthesis.speak(utterance);
      joltTimerRef.current = window.setTimeout(() => {
        joltTimerRef.current = null;
        window.speechSynthesis.pause();
        window.speechSynthesis.resume();
      }, 100);
    }, 50);
  }, [clearTimers]);

  return speak;
}
