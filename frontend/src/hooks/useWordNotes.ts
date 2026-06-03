import { useState, useCallback, useMemo, useEffect } from 'react';
import type { WordNote, SortType } from '../types';
import { fetchWordNotes, addWordNote, deleteWordNote, clearWordNotes } from '../services/api';

const STORAGE_KEY = 'my-word-notes';

export function useWordNotes() {
  const [notes, setNotes] = useState<WordNote[]>([]);
  const [loaded, setLoaded] = useState(false);
  const [sortType, setSortType] = useState<SortType>('time');
  const [searchKeyword, setSearchKeyword] = useState('');
  const [isReciteMode, setIsReciteMode] = useState(false);
  const [selectedWord, setSelectedWord] = useState<WordNote | null>(null);
  const [viewMode, setViewMode] = useState<'fullscreen' | 'detail'>('fullscreen');

  // 初始加载：优先从后端加载，若后端无数据则从 localStorage 迁移
  useEffect(() => {
    let cancelled = false;
    async function load() {
      try {
        const serverNotes = await fetchWordNotes();
        if (!cancelled) {
          if (serverNotes.length > 0) {
            setNotes(serverNotes);
          } else {
            // 后端无数据，尝试从 localStorage 迁移
            try {
              const stored = localStorage.getItem(STORAGE_KEY);
              if (stored) {
                const localNotes: WordNote[] = JSON.parse(stored);
                if (localNotes.length > 0) {
                  // 批量迁移到后端
                  for (const item of localNotes) {
                    try {
                      await addWordNote(item);
                    } catch { /* 跳过失败的项 */ }
                  }
                  setNotes(localNotes);
                  // 迁移成功后清除 localStorage
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
            setNotes(JSON.parse(stored));
          }
        } catch { /* ignore */ }
        setLoaded(true);
      }
    }
    load();
    return () => { cancelled = true; };
  }, []);

  const addWord = useCallback(
    async (wordData: { word: string; phonetic: string; meanings: { part_of_speech: string; definition: string; example: string }[] }) => {
      const exists = notes.some((n) => n.word === wordData.word);
      if (exists) return 'exists';

      const newNote: WordNote = {
        word: wordData.word,
        phonetic: wordData.phonetic,
        meaning: wordData.meanings[0]?.definition || '暂无释义',
        meanings: wordData.meanings,
        createTime: Date.now(),
      };

      // 乐观更新本地状态
      setNotes((prev) => [...prev, newNote]);

      try {
        const result = await addWordNote(newNote);
        if (result.status === 'exists') {
          // 后端已存在，回滚
          setNotes((prev) => prev.filter((n) => n.word !== wordData.word));
          return 'exists';
        }
        return 'success';
      } catch {
        // 后端保存失败，保留在 localStorage 作为 fallback
        try {
          const stored = localStorage.getItem(STORAGE_KEY);
          const localNotes: WordNote[] = stored ? JSON.parse(stored) : [];
          localNotes.push(newNote);
          localStorage.setItem(STORAGE_KEY, JSON.stringify(localNotes));
        } catch { /* ignore */ }
        return 'success';
      }
    },
    [notes],
  );

  const deleteWord = useCallback(
    async (word: string) => {
      const prevNotes = notes;
      setNotes((prev) => prev.filter((n) => n.word !== word));
      setSelectedWord((prev) => (prev?.word === word ? null : prev));

      try {
        await deleteWordNote(word);
      } catch {
        // 回滚
        setNotes(prevNotes);
      }
    },
    [notes],
  );

  const clearAll = useCallback(async () => {
    const prevNotes = notes;
    setNotes([]);
    setSelectedWord(null);
    setViewMode('fullscreen');

    try {
      await clearWordNotes();
    } catch {
      setNotes(prevNotes);
    }
  }, [notes]);

  const sortedNotes = useMemo(() => {
    let filtered = notes;
    if (searchKeyword) {
      const kw = searchKeyword.toLowerCase();
      filtered = notes.filter((n) => n.word.toLowerCase().includes(kw));
    }
    return [...filtered].sort((a, b) => {
      if (sortType === 'time') return b.createTime - a.createTime;
      return a.word.localeCompare(b.word);
    });
  }, [notes, sortType, searchKeyword]);

  return {
    notes: sortedNotes,
    allNotes: notes,
    loaded,
    sortType,
    setSortType,
    searchKeyword,
    setSearchKeyword,
    isReciteMode,
    setIsReciteMode,
    selectedWord,
    setSelectedWord,
    viewMode,
    setViewMode,
    addWord,
    deleteWord,
    clearAll,
  };
}
