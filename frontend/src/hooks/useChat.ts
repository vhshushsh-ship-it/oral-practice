import { useState, useCallback, useRef, useEffect } from 'react';
import type { ConversationMessage, Translation } from '../types';
import { sendTextMessageStream, sendVoiceMessageStream, translateToChinese, saveChatHistory, fetchChatHistory, clearChatHistory } from '../services/api';

export function useChat(scene: string) {
  const [messages, setMessages] = useState<ConversationMessage[]>([]);
  const [translations, setTranslations] = useState<Translation[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [historyLoaded, setHistoryLoaded] = useState(false);
  const loadingRef = useRef(false);
  // 用于在 streaming 期间中断请求
  const abortRef = useRef<(() => void) | null>(null);

  const sceneRef = useRef(scene);
  sceneRef.current = scene;

  const pendingAutoPlayRef = useRef(false);

  // 保存对话到后端（调用时立即捕获 scene，避免异步执行时 scene 已变化）
  const persistChat = useCallback(
    async (msgs: ConversationMessage[], trans: Translation[]) => {
      const capturedScene = sceneRef.current;
      try {
        await saveChatHistory(capturedScene, msgs, trans);
      } catch {
        // 后端保存失败，fallback 到 localStorage
        try {
          localStorage.setItem(`chat_history_${capturedScene}`, JSON.stringify(msgs));
          localStorage.setItem(`translations_${capturedScene}`, JSON.stringify(trans));
        } catch { /* ignore */ }
      }
    },
    [],
  );

  // 加载历史消息 + 翻译
  useEffect(() => {
    let cancelled = false;
    setHistoryLoaded(false);
    setMessages([]);
    setTranslations([]);
    async function load() {
      try {
        const data = await fetchChatHistory(scene);
        if (!cancelled) {
          if (data.history.length > 0 || data.translations.length > 0) {
            setMessages(data.history);
            setTranslations(data.translations);

            // 补翻译：后端有消息但缺少翻译的，按需翻译
            const translatedSources = new Set(data.translations.map((t) => t.source));
            const missing = data.history.filter((m) => !translatedSources.has(m.content));
            if (missing.length > 0) {
              translateMissingSequentially(missing);
            }
          } else {
            // 后端无数据，从 localStorage 迁移
            const storageKey = `chat_history_${scene}`;
            const transKey = `translations_${scene}`;
            try {
              const stored = localStorage.getItem(storageKey);
              if (stored) {
                const localHistory: ConversationMessage[] = JSON.parse(stored);
                const storedTrans = localStorage.getItem(transKey);
                const localTranslations: Translation[] = storedTrans ? JSON.parse(storedTrans) : [];

                if (localHistory.length > 0) {
                  setMessages(localHistory);
                  setTranslations(localTranslations);
                  // 迁移到后端
                  try {
                    await saveChatHistory(scene, localHistory, localTranslations);
                    localStorage.removeItem(storageKey);
                    localStorage.removeItem(transKey);
                  } catch { /* 迁移失败，保留 localStorage */ }

                  const translatedSources = new Set(localTranslations.map((t) => t.source));
                  const missing = localHistory.filter((m) => !translatedSources.has(m.content));
                  if (missing.length > 0) {
                    translateMissingSequentially(missing);
                  }
                }
              }
            } catch { /* ignore */ }
          }
          setHistoryLoaded(true);
        }
      } catch {
        // 后端不可用，fallback 到 localStorage
        try {
          const storageKey = `chat_history_${scene}`;
          const transKey = `translations_${scene}`;
          const stored = localStorage.getItem(storageKey);
          if (stored && !cancelled) {
            setMessages(JSON.parse(stored));
          }
          const storedTrans = localStorage.getItem(transKey);
          if (storedTrans && !cancelled) {
            setTranslations(JSON.parse(storedTrans));
          }
        } catch { /* ignore */ }
        setHistoryLoaded(true);
      }
    }
    load();
    return () => { cancelled = true; };
  }, [scene]);

  // 逐条翻译未翻译的消息（仅补充翻译到 state，persist 留到下次用户操作）
  const translateMissingSequentially = useCallback(
    async (msgs: ConversationMessage[]) => {
      for (const msg of msgs) {
        try {
          const translation = await translateToChinese(msg.content);
          setTranslations((prev) => [...prev, { source: msg.content, target: translation, isUser: msg.role === 'user' }]);
        } catch {
          setTranslations((prev) => [...prev, { source: msg.content, target: '翻译暂不可用', isUser: msg.role === 'user' }]);
        }
      }
    },
    [],
  );

  // ===================================================================
  //  sendText — 文本发送（即时显示 + 流式输出 + 后台翻译）
  //  关键：用户消息 ≤100ms 展示，翻译不阻塞 UI
  // ===================================================================
  const sendText = useCallback(
    async (text: string) => {
      if (!text.trim() || loadingRef.current) return;
      loadingRef.current = true;
      setIsLoading(true);

      // 在 async 入口快照当前状态，避免闭包过期
      const prevMessages = messages;
      const prevTranslations = translations;
      const last10 = prevMessages.slice(-10);

      const userMsg: ConversationMessage = { role: 'user', content: text };

      // ① 即刻展示用户消息 + AI 占位气泡（同步，≤1ms）
      const aiPlaceholder: ConversationMessage = { role: 'assistant', content: '' };
      setMessages([...prevMessages, userMsg, aiPlaceholder]);
      setTranslations([...prevTranslations, { source: text, target: '翻译中...', isUser: true }]);

      // ② 后台并行：翻译用户文本 + 启动 AI 流式（互不阻塞）
      const userTransPromise = translateToChinese(text).catch(() => '翻译暂不可用');

      try {
        const { stream, abort } = sendTextMessageStream(text, scene, last10);
        abortRef.current = abort;

        let fullAiText = '';
        for await (const token of stream) {
          fullAiText += token;
          // 逐 token 更新最后一个 assistant 消息的内容
          setMessages((prev) => {
            const updated = [...prev];
            const lastIdx = updated.length - 1;
            if (lastIdx >= 0 && updated[lastIdx].role === 'assistant') {
              updated[lastIdx] = { role: 'assistant', content: fullAiText };
            }
            return updated;
          });
        }

        abortRef.current = null;

        // ③ 收集翻译结果（用户翻译在后台早已完成，AI 翻译现在发起）
        const userTrans = await userTransPromise;
        let aiTrans = '翻译暂不可用';
        try {
          aiTrans = await translateToChinese(fullAiText);
        } catch { /* 翻译失败使用默认值 */ }
        const userTranslation: Translation = { source: text, target: userTrans, isUser: true };
        const aiTranslation: Translation = { source: fullAiText, target: aiTrans, isUser: false };

        // ④ 组装最终状态，单次 setState
        const finalMessages: ConversationMessage[] = [...prevMessages, userMsg, { role: 'assistant' as const, content: fullAiText }];
        const finalTranslations: Translation[] = [...prevTranslations, userTranslation, aiTranslation];

        // 必须在 setMessages 之前置位，确保 useEffect 触发时能检测到
        pendingAutoPlayRef.current = true;
        setMessages(finalMessages);
        setTranslations(finalTranslations);
        persistChat(finalMessages, finalTranslations);
      } catch (err: any) {
        abortRef.current = null;
        if (err?.name === 'AbortError') {
          // 用户取消：保留已收到的 token
          setMessages((prev) => {
            const updated = [...prev];
            const lastIdx = updated.length - 1;
            if (lastIdx >= 0 && updated[lastIdx].role === 'assistant' && !updated[lastIdx].content) {
              updated[lastIdx] = { role: 'assistant', content: '（已取消）' };
            }
            return updated;
          });
        } else {
          const errorMsg: ConversationMessage = { role: 'assistant', content: '发送失败，请重试' };
          const finalMessages = [...prevMessages, userMsg, errorMsg];
          setMessages(finalMessages);
          setTranslations([...prevTranslations, { source: text, target: '翻译暂不可用', isUser: true }]);
          persistChat(finalMessages, [...prevTranslations, { source: text, target: '翻译暂不可用', isUser: true }]);
        }
      } finally {
        loadingRef.current = false;
        setIsLoading(false);
      }
    },
    [scene, messages, translations, persistChat],
  );

  // ===================================================================
  //  sendVoice — 语音发送（ASR 完成后即时显示 + 流式输出 + 后台翻译）
  // ===================================================================
  const sendVoice = useCallback(
    async (audioBlob: Blob) => {
      if (loadingRef.current) return;
      loadingRef.current = true;
      setIsLoading(true);

      const prevMessages = messages;
      const prevTranslations = translations;
      const last10 = prevMessages.slice(-10);

      try {
        const { userTextPromise, stream, abort } = sendVoiceMessageStream(audioBlob, scene, last10);
        abortRef.current = abort;

        // 等待 ASR 识别结果（服务端延迟不可消除，但一拿到就立即展示）
        const userText = await userTextPromise;

        let userMsg: ConversationMessage | null = null;

        if (userText) {
          userMsg = { role: 'user', content: userText };

          // ① 即刻展示用户消息 + AI 占位（同步，≤1ms）
          const aiPlaceholder: ConversationMessage = { role: 'assistant', content: '' };
          setMessages([...prevMessages, userMsg, aiPlaceholder]);
          setTranslations([...prevTranslations, { source: userText, target: '翻译中...', isUser: true }]);

          // ② 后台翻译用户文本（不阻塞 AI 流式）
          const userTransPromise = translateToChinese(userText).catch(() => '翻译暂不可用');

          // ③ 流式接收 AI 回复 token
          let fullAiText = '';
          for await (const token of stream) {
            fullAiText += token;
            setMessages((prev) => {
              const updated = [...prev];
              const lastIdx = updated.length - 1;
              if (lastIdx >= 0 && updated[lastIdx].role === 'assistant') {
                updated[lastIdx] = { role: 'assistant', content: fullAiText };
              }
              return updated;
            });
          }

          abortRef.current = null;

          // ④ 收集翻译结果
          const userTrans = await userTransPromise;
          let aiTrans = '翻译暂不可用';
          if (fullAiText) {
            try {
              aiTrans = await translateToChinese(fullAiText);
            } catch { /* 翻译失败使用默认值 */ }
          }

          const userTranslation: Translation = { source: userText, target: userTrans, isUser: true };
          const aiTranslation: Translation | null = fullAiText
            ? { source: fullAiText, target: aiTrans, isUser: false }
            : null;

          // ⑤ 组装最终状态
          const finalMessages: ConversationMessage[] = [...prevMessages, userMsg];
          if (fullAiText) finalMessages.push({ role: 'assistant', content: fullAiText });
          const finalTranslations: Translation[] = [...prevTranslations, userTranslation];
          if (aiTranslation) finalTranslations.push(aiTranslation);

          if (fullAiText) {
            pendingAutoPlayRef.current = true;
          }
          setMessages(finalMessages);
          setTranslations(finalTranslations);

          if (fullAiText) {
            persistChat(finalMessages, finalTranslations);
          }
        } else {
          // ASR 返回空文本
          abortRef.current = null;
          const errorMsg: ConversationMessage = { role: 'assistant', content: '未识别到语音，请重试' };
          setMessages([...prevMessages, errorMsg]);
          // 消费 stream 以避免资源泄漏
          try { for await (const _ of stream) { /* drain */ } } catch { /* ignore drain errors */ }
        }
      } catch (err: any) {
        abortRef.current = null;
        if (err?.name !== 'AbortError') {
          const errorMsg: ConversationMessage = { role: 'assistant', content: '网络错误，请重试' };
          const finalMessages = [...prevMessages, errorMsg];
          setMessages(finalMessages);
          setTranslations(prevTranslations);
          persistChat(finalMessages, prevTranslations);
        }
      } finally {
        loadingRef.current = false;
        setIsLoading(false);
      }
    },
    [scene, messages, translations, persistChat],
  );

  // ===================================================================
  //  clearHistory — 清空对话（保留欢迎消息）
  // ===================================================================
  const clearHistory = useCallback(async () => {
    const currentMessages = messages;
    const welcomeMsg = currentMessages.find((m) => m.role === 'assistant');
    const newHistory = welcomeMsg ? [welcomeMsg] : [];
    setMessages(newHistory);
    setTranslations([]);

    try {
      await clearChatHistory(sceneRef.current);
      if (welcomeMsg) {
        let welcomeTrans = '翻译暂不可用';
        try {
          welcomeTrans = await translateToChinese(welcomeMsg.content);
        } catch { /* 翻译失败使用默认值 */ }
        const welcomeTranslation: Translation = {
          source: welcomeMsg.content,
          target: welcomeTrans,
          isUser: false,
        };
        setTranslations([welcomeTranslation]);
        await persistChat(newHistory, [welcomeTranslation]);
      }
    } catch {
      localStorage.removeItem(`chat_history_${sceneRef.current}`);
      localStorage.removeItem(`translations_${sceneRef.current}`);
      if (welcomeMsg) {
        try {
          const welcomeTrans = await translateToChinese(welcomeMsg.content);
          setTranslations([{ source: welcomeMsg.content, target: welcomeTrans, isUser: false }]);
        } catch {
          setTranslations([]);
        }
      }
    }
  }, [messages, persistChat]);

  // ===================================================================
  //  setHistory — 外部设置消息（PracticePage 欢迎消息）
  // ===================================================================
  const setHistory = useCallback(
    (newHistory: ConversationMessage[] | ((prev: ConversationMessage[]) => ConversationMessage[])) => {
      setMessages((prev) => {
        const resolved = typeof newHistory === 'function' ? newHistory(prev) : newHistory;
        // 不嵌套 setTranslations — 直接在这里读取闭包中的 translations 做 persist
        persistChat(resolved, translations);
        return resolved;
      });
    },
    [translations, persistChat],
  );

  return { messages, translations, isLoading, historyLoaded, sendText, sendVoice, clearHistory, setHistory, pendingAutoPlayRef };
}
