import { useState } from 'react';
import type { DialogueScene } from '../types';
import defaultDialogues from '../data/sceneDialogues';

const DATA_VERSION = 2;

export function useSceneDialogues() {
  const [dialogues] = useState<DialogueScene[]>(() => {
    try {
      const storedVersion = localStorage.getItem('scene-dialogues-version');
      const stored = localStorage.getItem('scene-dialogues');
      if (storedVersion === String(DATA_VERSION) && stored) {
        return JSON.parse(stored);
      }
      localStorage.setItem('scene-dialogues-version', String(DATA_VERSION));
      localStorage.setItem('scene-dialogues', JSON.stringify(defaultDialogues));
      return defaultDialogues;
    } catch {
      return defaultDialogues;
    }
  });
  const [selectedScene, setSelectedScene] = useState<DialogueScene | null>(null);

  return { dialogues, selectedScene, setSelectedScene };
}
