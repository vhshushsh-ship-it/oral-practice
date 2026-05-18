import { useState, useCallback, useMemo } from 'react';
import type { WordNote, SortType } from '../types';

const STORAGE_KEY = 'my-word-notes';

export function useWordNotes() {
  const [notes, setNotes] = useState<WordNote[]>(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      return stored ? JSON.parse(stored) : [];
    } catch {
      return [];
    }
  });
  const [sortType, setSortType] = useState<SortType>('time');
  const [searchKeyword, setSearchKeyword] = useState('');
  const [isReciteMode, setIsReciteMode] = useState(false);
  const [selectedWord, setSelectedWord] = useState<WordNote | null>(null);
  const [viewMode, setViewMode] = useState<'fullscreen' | 'detail'>('fullscreen');

  const save = useCallback((newNotes: WordNote[]) => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(newNotes));
    setNotes(newNotes);
  }, []);

  const addWord = useCallback(
    (wordData: { word: string; phonetic: string; meanings: { part_of_speech: string; definition: string; example: string }[] }) => {
      if (notes.some((n) => n.word === wordData.word)) return 'exists';
      const newNote: WordNote = {
        word: wordData.word,
        phonetic: wordData.phonetic,
        meaning: wordData.meanings[0]?.definition || '暂无释义',
        meanings: wordData.meanings,
        createTime: Date.now(),
      };
      save([...notes, newNote]);
      return 'success';
    },
    [notes, save],
  );

  const deleteWord = useCallback(
    (word: string) => {
      const newNotes = notes.filter((n) => n.word !== word);
      save(newNotes);
      setSelectedWord((prev) => (prev?.word === word ? null : prev));
    },
    [notes, save],
  );

  const clearAll = useCallback(() => {
    save([]);
    setSelectedWord(null);
    setViewMode('fullscreen');
  }, [save]);

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
