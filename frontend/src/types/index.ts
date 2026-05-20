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

// ====================== 连读规则 ======================
export interface LinkingExample {
  original: string;
  linked: string;
  translation: string;
}

export interface LinkingRule {
  id: string;
  name: string;
  nameEn: string;
  description: string;
  examples: LinkingExample[];
}

// ====================== 听力练习 ======================
export interface ListeningSentence {
  id: string;
  en: string;
  zh: string;
  audioUrl?: string;
  questionRef?: string;
}

export interface ListeningItem {
  id: string;
  name: string;
  sortOrder: number;
  sentences: ListeningSentence[];
}

export interface ListeningSection {
  id: string | null;
  name: string;
  sectionType: 'news_report' | 'long_conversation' | 'passage' | 'none';
  sortOrder: number;
  sentences: ListeningSentence[];
  items?: ListeningItem[];
}

export interface ListeningSet {
  id: string;
  name: string;
  type: 'cet4' | 'cet6';
  year?: number;
  month?: number;
  sections: ListeningSection[];
  question_count?: number;
}

export interface ListeningSetMeta {
  id: string;
  name: string;
  type: 'cet4' | 'cet6';
  year: number;
  month: number;
  sentence_count: number;
  question_count?: number;
}

export type ListeningLevel = 'cet4' | 'cet6';
export type ListeningView = 'browse' | 'practice' | 'exam' | 'exam_result';

export interface ListeningQuestion {
  id: string;
  set_id: string;
  section_id?: string;
  section_name?: string;
  item_id?: string;
  item_name?: string;
  question_number: number;
  question_text: string;
  question_text_zh?: string;
  option_a: string;
  option_b: string;
  option_c: string;
  option_d: string;
  sort_order: number;
}

export interface ExamAnswerDetail {
  questionId: string;
  questionNumber: number;
  questionText: string;
  questionTextZh?: string;
  optionA: string;
  optionB: string;
  optionC: string;
  optionD: string;
  correctAnswer: string;
  userAnswer: string;
  isCorrect: boolean;
}

export interface ExamResult {
  id: string;
  set_id: string;
  set_name?: string;
  totalQuestions: number;
  correctCount: number;
  accuracy: number;
  createdAt: string;
  details?: ExamAnswerDetail[];
}

export interface ExamHistoryItem {
  id: string;
  set_id: string;
  set_name: string;
  totalQuestions: number;
  correctCount: number;
  accuracy: number;
  createdAt: string;
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
