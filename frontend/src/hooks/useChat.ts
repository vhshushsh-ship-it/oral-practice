import { useState, useCallback, useRef, useEffect } from 'react';
import type { ConversationMessage, Translation } from '../types';
import { sendTextMessage, sendVoiceMessage, translateToChinese } from '../services/api';
import { useLocalStorage } from './useLocalStorage';

export function useChat(scene: string) {
  const [messages, setMessages] = useState<ConversationMessage[]>([]);
  const [translations, setTranslations] = useState<Translation[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const loadingRef = useRef(false);

  const sceneRef = useRef(scene);
  sceneRef.current = scene;

  const [history, setHistory] = useLocalStorage<ConversationMessage[]>(
    `chat_history_${scene}`,
    [],
  );

  const pendingAutoPlayRef = useRef(false);

  // Load history + translations when scene changes
  useEffect(() => {
    const storageKey = `chat_history_${scene}`;
    const transKey = `translations_${scene}`;
    try {
      const stored = localStorage.getItem(storageKey);
      const loaded: ConversationMessage[] = stored ? JSON.parse(stored) : [];
      setMessages(loaded);

      // Restore saved translations
      const storedTrans = localStorage.getItem(transKey);
      const savedTranslations: Translation[] = storedTrans ? JSON.parse(storedTrans) : [];
      setTranslations(savedTranslations);

      // Translate any messages that don't have saved translations yet
      const translatedSources = new Set(savedTranslations.map((t) => t.source));
      const missing = loaded.filter((m) => !translatedSources.has(m.content));

      if (missing.length > 0) {
        translateMissingSequentially(missing, transKey);
      }
    } catch {
      setMessages([]);
      setTranslations([]);
    }
  }, [scene]);

  // Translate missing messages one at a time to avoid race conditions with localStorage writes
  const translateMissingSequentially = useCallback(
    async (msgs: ConversationMessage[], transKey: string) => {
      for (const msg of msgs) {
        try {
          const translation = await translateToChinese(msg.content);
          setTranslations((prev) => {
            const next = [...prev, { source: msg.content, target: translation, isUser: msg.role === 'user' }];
            localStorage.setItem(transKey, JSON.stringify(next));
            return next;
          });
        } catch {
          setTranslations((prev) => {
            const next = [...prev, { source: msg.content, target: '翻译暂不可用', isUser: msg.role === 'user' }];
            localStorage.setItem(transKey, JSON.stringify(next));
            return next;
          });
        }
      }
    },
    [],
  );

  const addTranslation = useCallback(
    async (text: string, isUser: boolean) => {
      const transKey = `translations_${sceneRef.current}`;
      try {
        const translation = await translateToChinese(text);
        setTranslations((prev) => {
          const next = [...prev, { source: text, target: translation, isUser }];
          localStorage.setItem(transKey, JSON.stringify(next));
          return next;
        });
      } catch {
        setTranslations((prev) => {
          const next = [...prev, { source: text, target: '翻译暂不可用', isUser }];
          localStorage.setItem(transKey, JSON.stringify(next));
          return next;
        });
      }
    },
    [],
  );

  const sendText = useCallback(
    async (text: string) => {
      if (!text.trim() || loadingRef.current) return;
      loadingRef.current = true;
      setIsLoading(true);

      const last10 = messages.slice(-10);

      const userMsg: ConversationMessage = { role: 'user', content: text };
      setMessages((prev) => [...prev, userMsg]);
      setHistory((prev) => [...prev, userMsg]);
      await addTranslation(text, true);

      try {
        const res = await sendTextMessage(text, scene, last10);
        const aiMsg: ConversationMessage = { role: 'assistant', content: res.ai_text };
        setMessages((prev) => [...prev, aiMsg]);
        setHistory((prev) => [...prev, aiMsg]);
        pendingAutoPlayRef.current = true;
        await addTranslation(res.ai_text, false);
      } catch {
        setMessages((prev) => [
          ...prev,
          { role: 'assistant', content: '发送失败，请重试' },
        ]);
      } finally {
        loadingRef.current = false;
        setIsLoading(false);
      }
    },
    [scene, messages, addTranslation, setHistory],
  );

  const sendVoice = useCallback(
    async (audioBlob: Blob) => {
      if (loadingRef.current) return;
      loadingRef.current = true;
      setIsLoading(true);

      const last10 = messages.slice(-10);

      try {
        const res = await sendVoiceMessage(audioBlob, scene, last10);

        if (res.user_text) {
          const userMsg: ConversationMessage = { role: 'user', content: res.user_text };
          setMessages((prev) => [...prev, userMsg]);
          setHistory((prev) => [...prev, userMsg]);
          await addTranslation(res.user_text, true);
        }

        if (res.ai_text) {
          const aiMsg: ConversationMessage = { role: 'assistant', content: res.ai_text };
          setMessages((prev) => [...prev, aiMsg]);
          setHistory((prev) => [...prev, aiMsg]);
          pendingAutoPlayRef.current = true;
          await addTranslation(res.ai_text, false);
        }
      } catch {
        setMessages((prev) => [
          ...prev,
          { role: 'assistant', content: '网络错误，请重试' },
        ]);
      } finally {
        loadingRef.current = false;
        setIsLoading(false);
      }
    },
    [scene, messages, addTranslation, setHistory],
  );

  const clearHistory = useCallback(() => {
    const welcomeMsg = history.find((m) => m.role === 'assistant');
    const newHistory = welcomeMsg ? [welcomeMsg] : [];
    const transKey = `translations_${sceneRef.current}`;
    setMessages(newHistory);
    setHistory(newHistory);
    if (welcomeMsg) {
      setTranslations([]);
      localStorage.removeItem(transKey);
      addTranslation(welcomeMsg.content, false);
    } else {
      setTranslations([]);
      localStorage.removeItem(transKey);
    }
  }, [history, setHistory, addTranslation]);

  return { messages, translations, isLoading, sendText, sendVoice, clearHistory, setHistory, pendingAutoPlayRef };
}
