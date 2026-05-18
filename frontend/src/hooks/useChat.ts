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

  // Load history when scene changes
  useEffect(() => {
    setMessages(history);
    setTranslations([]);
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
        // silently fail
      }
    },
    [],
  );

  const sendText = useCallback(
    async (text: string) => {
      if (!text.trim() || loadingRef.current) return;
      loadingRef.current = true;
      setIsLoading(true);

      const last10 = [...messages, { role: 'user' as const, content: text }].slice(-10);

      setMessages((prev) => [...prev, { role: 'user', content: text }]);
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
  }, [history, setHistory]);

  return { messages, translations, isLoading, sendText, sendVoice, clearHistory, setHistory };
}
