import { useState, useCallback, useEffect } from 'react';
import type { SentenceItem } from '../types';
import { fetchSentences, addSentenceItem, deleteSentenceItem, clearSentenceItems, translateSentence } from '../services/api';

const STORAGE_KEY = 'my-sentence-collection';

export function useSentenceCollection() {
  const [collection, setCollection] = useState<SentenceItem[]>([]);
  const [loaded, setLoaded] = useState(false);

  // 初始加载：优先从后端加载，若后端无数据则从 localStorage 迁移
  useEffect(() => {
    let cancelled = false;
    async function load() {
      try {
        const serverItems = await fetchSentences();
        if (!cancelled) {
          if (serverItems.length > 0) {
            setCollection(serverItems);
          } else {
            // 后端无数据，尝试从 localStorage 迁移
            try {
              const stored = localStorage.getItem(STORAGE_KEY);
              if (stored) {
                const localItems: SentenceItem[] = JSON.parse(stored);
                if (localItems.length > 0) {
                  // 批量迁移到后端
                  for (const item of localItems) {
                    try {
                      await addSentenceItem(item.text, item.translation, item.createTime);
                    } catch { /* 跳过失败的项 */ }
                  }
                  setCollection(localItems);
                  localStorage.removeItem(STORAGE_KEY);
                }
              }
            } catch { /* localStorage 解析失败，忽略 */ }
          }
          setLoaded(true);
        }
      } catch {
        // 后端不可用，fallback 到 localStorage
        try {
          const stored = localStorage.getItem(STORAGE_KEY);
          if (stored && !cancelled) {
            setCollection(JSON.parse(stored));
          }
        } catch { /* ignore */ }
        setLoaded(true);
      }
    }
    load();
    return () => { cancelled = true; };
  }, []);

  const addSentence = useCallback(
    async (text: string) => {
      if (!text.trim()) return;
      if (collection.some((s) => s.text === text)) {
        return 'exists';
      }

      // 先获取翻译
      let translation = '';
      try {
        translation = await translateSentence(text);
      } catch {
        translation = '翻译获取失败';
      }

      const newItem: SentenceItem = { text, translation, createTime: Date.now() };

      // 乐观更新
      setCollection((prev) => [...prev, newItem]);

      try {
        const result = await addSentenceItem(text, translation, newItem.createTime);
        if (result.status === 'exists') {
          setCollection((prev) => prev.filter((s) => s.text !== text));
          return 'exists';
        }
        return 'success';
      } catch {
        // 后端失败，保留在 localStorage 作为 fallback
        try {
          const stored = localStorage.getItem(STORAGE_KEY);
          const localItems: SentenceItem[] = stored ? JSON.parse(stored) : [];
          localItems.push(newItem);
          localStorage.setItem(STORAGE_KEY, JSON.stringify(localItems));
        } catch { /* ignore */ }
        return 'success';
      }
    },
    [collection],
  );

  const deleteSentence = useCallback(
    async (index: number) => {
      const prevCollection = collection;
      setCollection((prev) => prev.filter((_, i) => i !== index));

      try {
        await deleteSentenceItem(index);
      } catch {
        setCollection(prevCollection);
      }
    },
    [collection],
  );

  const clearAll = useCallback(async () => {
    const prevCollection = collection;
    setCollection([]);

    try {
      await clearSentenceItems();
    } catch {
      setCollection(prevCollection);
    }
  }, [collection]);

  return { collection, loaded, addSentence, deleteSentence, clearAll };
}
