import { useState, useCallback } from 'react';
import type { SentenceItem } from '../types';
import { translateSentence } from '../services/api';

const STORAGE_KEY = 'my-sentence-collection';

export function useSentenceCollection() {
  const [collection, setCollection] = useState<SentenceItem[]>(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      return stored ? JSON.parse(stored) : [];
    } catch {
      return [];
    }
  });

  const save = useCallback((items: SentenceItem[]) => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(items));
    setCollection(items);
  }, []);

  const addSentence = useCallback(
    async (text: string) => {
      if (!text.trim()) return;
      if (collection.some((s) => s.text === text)) {
        return 'exists';
      }
      let translation = '';
      try {
        translation = await translateSentence(text);
      } catch {
        translation = '翻译获取失败';
      }
      const newItems: SentenceItem[] = [
        ...collection,
        { text, translation, createTime: Date.now() },
      ];
      save(newItems);
      return 'success';
    },
    [collection, save],
  );

  const deleteSentence = useCallback(
    (index: number) => {
      const newItems = collection.filter((_, i) => i !== index);
      save(newItems);
    },
    [collection, save],
  );

  const clearAll = useCallback(() => {
    save([]);
  }, [save]);

  return { collection, addSentence, deleteSentence, clearAll };
}
