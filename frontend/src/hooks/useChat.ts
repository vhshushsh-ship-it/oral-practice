import { useState, useCallback, useRef, useEffect } from 'react';
import type { ConversationMessage, Translation } from '../types';
import { sendTextMessage, sendVoiceMessage, translateToChinese } from '../services/api';
import { useLocalStorage } from './useLocalStorage';

export function useChat(scene: string) {
  const [messages, setMessages] = useState<ConversationMessage[]>([]);
  const [translations, setTranslations] = useState<Translation[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const loadingRef = useRef(false);

  const [history, setHistory] = useLocalStorage<ConversationMessage[]>(
    `chat_history_${scene}`,
    [],
  );

  // Load history when scene changes — read directly from localStorage to avoid
  // useLocalStorage's async-state timing issue (old key value for one render tick).
  useEffect(() => {
    const storageKey = `chat_history_${scene}`;
    try {
      const stored = localStorage.getItem(storageKey);
      const loaded: ConversationMessage[] = stored ? JSON.parse(stored) : [];
      setMessages(loaded);
      setTranslations([]);
      if (loaded.length === 1) {
        addTranslation(loaded[0].content, false);
      }
    } catch {
      setMessages([]);
      setTranslations([]);
    }
  }, [scene]);

  const addTranslation = useCallback(
    async (text: string, isUser: boolean) => {
      try {
        const translation = await translateToChinese(text);
        setTranslations((prev) => [
          ...prev,
          { source: text, target: translation, isUser },
        ]);
      } catch {
        setTranslations((prev) => [
          ...prev,
          { source: text, target: '翻译暂不可用', isUser },
        ]);
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
    setMessages(newHistory);
    setHistory(newHistory);
    setTranslations([]);
    if (welcomeMsg) {
      addTranslation(welcomeMsg.content, false);
    }
  }, [history, setHistory, addTranslation]);

  return { messages, translations, isLoading, sendText, sendVoice, clearHistory, setHistory };
}
