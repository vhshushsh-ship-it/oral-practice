import { useState, useCallback } from 'react';

export function useLocalStorage<T>(key: string, initialValue: T) {
  const [value, setValue] = useState<T>(() => {
    try {
      const stored = localStorage.getItem(key);
      return stored ? (JSON.parse(stored) as T) : initialValue;
    } catch {
      return initialValue;
    }
  });

  const update = useCallback(
    (newValue: T | ((prev: T) => T)) => {
      setValue((prev) => {
        const next = typeof newValue === 'function' ? (newValue as (prev: T) => T)(prev) : newValue;
        localStorage.setItem(key, JSON.stringify(next));
        return next;
      });
    },
    [key],
  );

  return [value, update] as const;
}
