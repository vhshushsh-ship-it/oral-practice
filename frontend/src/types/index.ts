// ====================== 对话 ======================
export interface ConversationMessage {
  role: 'user' | 'assistant';
  content: string;
}

// ====================== 场景 ======================
export interface DialogueTurn {
  speaker: string;
  en: string;
  zh: string;
}

export interface DialogueScene {
  id: string;
  name: string;
  turns: DialogueTurn[];
}

// ====================== 翻译 ======================
export interface Translation {
  source: string;
  target: string;
  isUser: boolean;
}

// ====================== 单词 ======================
export interface WordMeaning {
  part_of_speech: string;
  definition: string;
  example: string; // "en|zh" format
}

export interface WordData {
  word: string;
  phonetic: string;
  meanings: WordMeaning[];
}

export interface WordNote {
  word: string;
  phonetic: string;
  meaning: string;
  meanings: WordMeaning[];
  createTime: number;
}

// ====================== 句子收藏 ======================
export interface SentenceItem {
  text: string;
  translation: string;
  createTime: number;
}

// ====================== Toast ======================
export type ToastType = 'success' | 'info' | 'warning';

export interface Toast {
  id: number;
  message: string;
  type: ToastType;
}

// ====================== 全局 App 状态 ======================
export type SortType = 'time' | 'alphabet';
export type NotesViewMode = 'fullscreen' | 'detail';
export type RightModule = 'word' | 'translate';
