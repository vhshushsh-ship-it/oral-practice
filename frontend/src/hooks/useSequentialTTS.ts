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
  const timerRef = useRef<number | null>(null);
  const pollTimeoutRef = useRef<number | null>(null);
  const keepAliveRef = useRef<number | null>(null);
  const genRef = useRef(0);
  const activeGenRef = useRef(0);
  const utteranceRef = useRef<SpeechSynthesisUtterance | null>(null);

  const clearTimer = useCallback(() => {
    if (timerRef.current != null) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
    if (pollTimeoutRef.current != null) {
      clearTimeout(pollTimeoutRef.current);
      pollTimeoutRef.current = null;
    }
  }, []);

  const clearKeepAlive = useCallback(() => {
    if (keepAliveRef.current != null) {
      clearInterval(keepAliveRef.current);
      keepAliveRef.current = null;
    }
  }, []);

  const clearAllTimers = useCallback(() => {
    clearTimer();
    clearKeepAlive();
  }, [clearTimer, clearKeepAlive]);

  const startKeepAlive = useCallback(() => {
    clearKeepAlive();
    // Chrome speechSynthesis gets stuck after ~15s of continuous speech.
    // Periodically pause+resume to keep the internal state machine alive.
    keepAliveRef.current = window.setInterval(() => {
      if (window.speechSynthesis.speaking) {
        window.speechSynthesis.pause();
        window.speechSynthesis.resume();
      }
    }, 5000);
  }, [clearKeepAlive]);

  const speakAtIndex = useCallback((index: number) => {
    const texts = textsRef.current;
    if (index < 0 || index >= texts.length) {
      stopInternal();
      return;
    }

    const text = texts[index].replace(EMOJI_REGEX, '').trim();
    if (!text) {
      indexRef.current = index + 1;
      setCurrentIndex(index + 1);
      speakAtIndex(index + 1);
      return;
    }

    genRef.current += 1;
    const gen = genRef.current;
    activeGenRef.current = gen;
    indexRef.current = index;
    setCurrentIndex(index);

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'en-US';
    utterance.rate = rateRef.current;
    utteranceRef.current = utterance;

    const onDone = () => {
      if (genRef.current !== gen) return;
      genRef.current += 1; // Invalidate stale callbacks (double-fire, old utterance)
      clearTimer();
      utteranceRef.current = null;
      const next = indexRef.current + 1;
      if (next >= texts.length) {
        clearKeepAlive();
        indexRef.current = -1;
        setCurrentIndex(-1);
        setPlayState('idle');
        setTotalCount(0);
        textsRef.current = [];
      } else {
        speakAtIndex(next);
      }
    };

    utterance.onend = onDone;
    utterance.onerror = () => {
      onDone();
    };

    window.speechSynthesis.cancel();
    // Small delay after cancel to let Chrome's internal state settle
    setTimeout(() => {
      window.speechSynthesis.speak(utterance);
      startKeepAlive();
      // Initial jolt to ensure Chrome starts speaking
      setTimeout(() => {
        window.speechSynthesis.pause();
        window.speechSynthesis.resume();
      }, 100);
    }, 50);

    // polling fallback: Android Chrome sometimes doesn't fire onend.
    // Also detects Chrome's "stuck speech" bug (speaking becomes false without onend).
    clearTimer();
    timerRef.current = window.setInterval(() => {
      if (!window.speechSynthesis.speaking && !window.speechSynthesis.pending) {
        if (genRef.current === gen) {
          // Chrome stuck-speech workaround: try to jolt it back
          window.speechSynthesis.pause();
          window.speechSynthesis.resume();
          // After pause+resume, if still not speaking within 200ms, it's truly done
          pollTimeoutRef.current = window.setTimeout(() => {
            pollTimeoutRef.current = null;
            if (genRef.current === gen && !window.speechSynthesis.speaking) {
              onDone();
            }
          }, 200);
        }
      }
    }, 150);
  }, [clearTimer, clearKeepAlive, startKeepAlive]);

  const stopInternal = useCallback(() => {
    genRef.current += 1;
    window.speechSynthesis.cancel();
    clearAllTimers();
    utteranceRef.current = null;
    textsRef.current = [];
    indexRef.current = -1;
    setCurrentIndex(-1);
    setPlayState('idle');
    setTotalCount(0);
  }, [clearAllTimers]);

  const play = useCallback((texts: string[], startIndex = 0) => {
    stopInternal();
    textsRef.current = texts;
    setTotalCount(texts.length);
    if (texts.length === 0) return;
    const start = Math.max(0, Math.min(startIndex, texts.length - 1));
    setPlayState('playing');
    speakAtIndex(start);
  }, [stopInternal, speakAtIndex]);

  const pause = useCallback(() => {
    window.speechSynthesis.pause();
    clearAllTimers();
    setPlayState('paused');
  }, [clearAllTimers]);

  const resume = useCallback(() => {
    window.speechSynthesis.resume();
    setPlayState('playing');
    startKeepAlive();
    // restart polling
    const gen = activeGenRef.current;
    clearTimer();
    timerRef.current = window.setInterval(() => {
      if (!window.speechSynthesis.speaking && !window.speechSynthesis.pending) {
        if (genRef.current === gen) {
          window.speechSynthesis.pause();
          window.speechSynthesis.resume();
          pollTimeoutRef.current = window.setTimeout(() => {
            pollTimeoutRef.current = null;
            if (genRef.current === gen && !window.speechSynthesis.speaking) {
              genRef.current += 1;
              clearTimer();
              utteranceRef.current = null;
              const next = indexRef.current + 1;
              if (next >= textsRef.current.length) {
                clearKeepAlive();
                indexRef.current = -1;
                setCurrentIndex(-1);
                setPlayState('idle');
                setTotalCount(0);
                textsRef.current = [];
              } else {
                speakAtIndex(next);
              }
            }
          }, 200);
        }
      }
    }, 150);
  }, [clearTimer, clearKeepAlive, startKeepAlive, speakAtIndex]);

  const next = useCallback(() => {
    clearAllTimers();
    utteranceRef.current = null;
    window.speechSynthesis.cancel();
    const i = Math.min(indexRef.current + 1, textsRef.current.length - 1);
    if (i >= 0 && textsRef.current.length > 0) {
      speakAtIndex(i);
    }
  }, [clearAllTimers, speakAtIndex]);

  const prev = useCallback(() => {
    clearAllTimers();
    utteranceRef.current = null;
    window.speechSynthesis.cancel();
    const i = Math.max(indexRef.current - 1, 0);
    if (i >= 0 && textsRef.current.length > 0) {
      speakAtIndex(i);
    }
  }, [clearAllTimers, speakAtIndex]);

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
