import { useCallback, useRef } from 'react';

const EMOJI_REGEX =
  /[\u{1F600}-\u{1F6FF}\u{1F300}-\u{1F5FF}\u{1F900}-\u{1F9FF}\u{1F1E0}-\u{1F1FF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}\u{FE00}-\u{FE0F}]/gu;

function removeEmojis(text: string): string {
  return text.replace(EMOJI_REGEX, '').trim();
}

export function useSpeechSynthesis(speechRate: number) {
  const rateRef = useRef(speechRate);
  rateRef.current = speechRate;

  const speak = useCallback((text: string) => {
    if (!text) return;
    const clean = removeEmojis(text);
    if (!clean) return;

    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(clean);
    utterance.lang = 'en-US';
    utterance.rate = rateRef.current;

    setTimeout(() => {
      window.speechSynthesis.speak(utterance);
    }, 0);
  }, []);

  return speak;
}
