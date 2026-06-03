import type { ConversationMessage, WordData, SentenceItem, ListeningSetMeta, ListeningSet, ListeningQuestion, ExamResult, ExamHistoryItem, ListeningLevel, SentenceAnalysisResult, GrammarCheckResult } from '../types';

const API_BASE = 'http://127.0.0.1:8000';

// ====================== Auth token 管理 ======================
// 使用 sessionStorage 实现单标签登录态隔离：
// 同一浏览器多个标签可分别登录不同账号，各自独立，互不顶替。
// sessionStorage 生命周期绑定单个标签页，关闭标签即清除登录态。
function getAuthHeaders(): Record<string, string> {
  const token = sessionStorage.getItem('access_token');
  if (token) {
    return { 'Authorization': `Bearer ${token}` };
  }
  return {};
}

async function post(path: string, body: Record<string, string>): Promise<Response> {
  const formBody = new URLSearchParams(body).toString();
  return fetch(`${API_BASE}${path}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
      ...getAuthHeaders(),
    },
    body: formBody,
  });
}

// ====================== 场景初始化 ======================
export async function initScene(sceneChoice: string): Promise<{ scene: string; initial_message: string }> {
  const res = await post('/init', { scene_choice: sceneChoice });
  return res.json();
}

// ====================== 语音对话 ======================
export async function sendVoiceMessage(
  audioBlob: Blob,
  scene: string,
  history: ConversationMessage[],
): Promise<{ user_text: string; ai_text: string }> {
  const formData = new FormData();
  formData.append('audio', audioBlob, 'recording.wav');
  formData.append('scene', scene);
  formData.append('conversation_history', JSON.stringify(history));
  const res = await fetch(`${API_BASE}/chat`, {
    method: 'POST',
    headers: { ...getAuthHeaders() },
    body: formData,
  });
  return res.json();
}

/**
 * 流式语音对话 — 返回 userTextPromise（ASR 识别结果）、token stream 和 abort。
 * userTextPromise 在收到第一个 SSE 事件时 resolve。
 */
export function sendVoiceMessageStream(
  audioBlob: Blob,
  scene: string,
  history: ConversationMessage[],
): { userTextPromise: Promise<string>; stream: AsyncGenerator<string, string, unknown>; abort: () => void } {
  const controller = new AbortController();
  let resolveUserText!: (text: string) => void;
  const userTextPromise = new Promise<string>((resolve) => { resolveUserText = resolve; });

  async function* streamGenerator(): AsyncGenerator<string, string, unknown> {
    const formData = new FormData();
    formData.append('audio', audioBlob, 'recording.wav');
    formData.append('scene', scene);
    formData.append('conversation_history', JSON.stringify(history));
    formData.append('stream', 'true');

    const res = await fetch(`${API_BASE}/chat`, {
      method: 'POST',
      headers: { ...getAuthHeaders() },
      body: formData,
      signal: controller.signal,
    });

    if (!res.ok) {
      resolveUserText('');
      throw new Error(`Stream request failed: ${res.status}`);
    }

    const reader = res.body?.getReader();
    if (!reader) {
      resolveUserText('');
      throw new Error('No response body');
    }

    const decoder = new TextDecoder();
    let buffer = '';
    let fullText = '';

    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6);
            if (data === '[DONE]') {
              return fullText;
            }
            try {
              const parsed = JSON.parse(data);
              if (parsed.user_text !== undefined) {
                resolveUserText(parsed.user_text);
              } else if (parsed.token) {
                fullText += parsed.token;
                yield parsed.token;
              }
            } catch {
              // skip malformed JSON lines
            }
          }
        }
      }
      return fullText;
    } finally {
      // 确保 userTextPromise 必定 resolve，防止 hook 挂起
      resolveUserText('');
    }
  }

  return { userTextPromise, stream: streamGenerator(), abort: () => controller.abort() };
}

// ====================== 文本对话 ======================
export async function sendTextMessage(
  text: string,
  scene: string,
  history: ConversationMessage[],
): Promise<{ user_text: string; ai_text: string }> {
  const res = await post('/chat_text', {
    user_text: text,
    scene,
    conversation_history: JSON.stringify(history),
  });
  return res.json();
}

/**
 * 流式文本对话 — 返回一个 AbortController 和 async generator，
 * 逐 token yield，实现打字机实时输出。
 */
export function sendTextMessageStream(
  text: string,
  scene: string,
  history: ConversationMessage[],
): { stream: AsyncGenerator<string, string, unknown>; abort: () => void } {
  const controller = new AbortController();

  async function* streamGenerator(): AsyncGenerator<string, string, unknown> {
    const formBody = new URLSearchParams({
      user_text: text,
      scene,
      conversation_history: JSON.stringify(history),
      stream: 'true',
    }).toString();

    const res = await fetch(`${API_BASE}/chat_text`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        ...getAuthHeaders(),
      },
      body: formBody,
      signal: controller.signal,
    });

    if (!res.ok) {
      throw new Error(`Stream request failed: ${res.status}`);
    }

    const reader = res.body?.getReader();
    if (!reader) throw new Error('No response body');

    const decoder = new TextDecoder();
    let buffer = '';
    let fullText = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6);
          if (data === '[DONE]') {
            return fullText;
          }
          try {
            const parsed = JSON.parse(data);
            if (parsed.token) {
              fullText += parsed.token;
              yield parsed.token;
            }
          } catch {
            // skip malformed JSON lines
          }
        }
      }
    }
    return fullText;
  }

  return { stream: streamGenerator(), abort: () => controller.abort() };
}

// ====================== 翻译 ======================
export async function translateToChinese(text: string): Promise<string> {
  const res = await post('/translate', { text });
  const data = await res.json();
  return data.translation || '翻译出错';
}

export async function translateToEnglish(text: string): Promise<string> {
  const res = await post('/translate_to_en', { text });
  const data = await res.json();
  return data.translation || '翻译出错';
}

// ====================== 单词查询 ======================
export async function queryWord(word: string): Promise<WordData | { error: string }> {
  const res = await fetch(`${API_BASE}/word/query?word=${encodeURIComponent(word)}`, {
    method: 'POST',
    headers: { ...getAuthHeaders() },
  });
  if (!res.ok) throw new Error(`请求失败，状态码：${res.status}`);
  return res.json();
}

// ====================== JSON 请求辅助 ======================
async function postJSON(path: string, body: unknown): Promise<Response> {
  return fetch(`${API_BASE}${path}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...getAuthHeaders(),
    },
    body: JSON.stringify(body),
  });
}

async function del(path: string): Promise<Response> {
  return fetch(`${API_BASE}${path}`, {
    method: 'DELETE',
    headers: { ...getAuthHeaders() },
  });
}

// ====================== 对话历史持久化 ======================
export async function saveChatHistory(
  scene: string,
  history: ConversationMessage[],
  translations?: { source: string; target: string; isUser: boolean }[],
): Promise<void> {
  const res = await postJSON('/chat/save', { scene, history, translations: translations || [] });
  if (!res.ok) throw new Error(`保存对话失败: ${res.status}`);
}

export async function fetchChatHistory(
  scene: string,
): Promise<{ history: ConversationMessage[]; translations: { source: string; target: string; isUser: boolean }[] }> {
  const res = await fetch(`${API_BASE}/chat/history?scene=${encodeURIComponent(scene)}`, {
    headers: { ...getAuthHeaders() },
  });
  if (!res.ok) throw new Error(`获取对话历史失败: ${res.status}`);
  return res.json();
}

export async function clearChatHistory(scene: string): Promise<void> {
  const res = await fetch(`${API_BASE}/chat/clear?scene=${encodeURIComponent(scene)}`, {
    headers: { ...getAuthHeaders() },
  });
  if (!res.ok) throw new Error(`清空对话失败: ${res.status}`);
}

// ====================== 单词笔记持久化 ======================
export interface WordNoteItem {
  word: string;
  phonetic: string;
  meaning: string;
  meanings: { part_of_speech: string; definition: string; example: string }[];
  createTime: number;
}

export async function fetchWordNotes(): Promise<WordNoteItem[]> {
  const res = await fetch(`${API_BASE}/notes/all`, {
    headers: { ...getAuthHeaders() },
  });
  if (!res.ok) throw new Error(`获取单词笔记失败: ${res.status}`);
  const data = await res.json();
  return data.notes;
}

export async function addWordNote(item: WordNoteItem): Promise<{ status: string; message: string }> {
  const res = await postJSON('/notes/add', item);
  return res.json();
}

export async function deleteWordNote(word: string): Promise<void> {
  await postJSON(`/notes/delete?word=${encodeURIComponent(word)}`, {});
}

export async function clearWordNotes(): Promise<void> {
  await postJSON('/notes/clear', {});
}

// ====================== 句子收藏持久化 ======================
export async function fetchSentences(): Promise<SentenceItem[]> {
  const res = await fetch(`${API_BASE}/sentences/all`, {
    headers: { ...getAuthHeaders() },
  });
  if (!res.ok) throw new Error(`获取句子收藏失败: ${res.status}`);
  const data = await res.json();
  return data.sentences;
}

export async function addSentenceItem(
  text: string,
  translation: string,
  createTime?: number,
): Promise<{ status: string; message: string }> {
  const res = await postJSON('/sentences/add', { text, translation, createTime });
  return res.json();
}

export async function deleteSentenceItem(index: number): Promise<void> {
  await postJSON(`/sentences/delete?index=${index}`, {});
}

export async function clearSentenceItems(): Promise<void> {
  await postJSON('/sentences/clear', {});
}

// ====================== 语法打分历史持久化 ======================
export interface GrammarHistoryRecord {
  sourceSent: string;
  score: number;
  errorIndex: number[];
  errorInfo: string[];
  fixedSent: string;
  createdAt: string;
}

export async function saveGrammarResult(result: Omit<GrammarHistoryRecord, 'createdAt'>): Promise<void> {
  const res = await postJSON('/grammar/save', result);
  if (!res.ok) throw new Error(`保存语法记录失败: ${res.status}`);
}

export async function fetchGrammarHistory(): Promise<GrammarHistoryRecord[]> {
  const res = await fetch(`${API_BASE}/grammar/history`, {
    headers: { ...getAuthHeaders() },
  });
  if (!res.ok) throw new Error(`获取语法历史失败: ${res.status}`);
  const data = await res.json();
  return data.records;
}

export async function deleteGrammarRecord(index: number): Promise<void> {
  const res = await del(`/grammar/history/${index}`);
  if (!res.ok) throw new Error(`删除语法记录失败: ${res.status}`);
}

export async function clearGrammarHistory(): Promise<void> {
  const res = await del('/grammar/history');
  if (!res.ok) throw new Error(`清空语法历史失败: ${res.status}`);
}

// ====================== 句子收藏翻译 ======================
export async function translateSentence(text: string): Promise<string> {
  return translateToChinese(text);
}

// ====================== 听力练习 ======================
export async function fetchListeningSets(level?: ListeningLevel): Promise<ListeningSetMeta[]> {
  let url = `${API_BASE}/api/listening/sets`;
  if (level) url += `?level=${level}`;
  const res = await fetch(url, { headers: { ...getAuthHeaders() } });
  if (!res.ok) throw new Error(`获取听力套题列表失败: ${res.status}`);
  const data = await res.json();
  return data.sets;
}

export async function fetchListeningSetDetail(setId: string): Promise<ListeningSet> {
  const res = await fetch(`${API_BASE}/api/listening/sets/${encodeURIComponent(setId)}`, {
    headers: { ...getAuthHeaders() },
  });
  if (!res.ok) throw new Error(`获取听力套题详情失败: ${res.status}`);
  const data = await res.json();
  return data.set;
}

export async function fetchQuestions(setId: string): Promise<{ set_id: string; questions: ListeningQuestion[] }> {
  const res = await fetch(`${API_BASE}/api/listening/sets/${encodeURIComponent(setId)}/questions`, {
    headers: { ...getAuthHeaders() },
  });
  if (!res.ok) throw new Error(`获取题目失败: ${res.status}`);
  return res.json();
}

export async function submitExamAnswers(
  setId: string,
  answers: { questionId: string; selectedOption: string }[],
): Promise<ExamResult> {
  const body = {
    set_id: setId,
    answers: answers.map((a) => ({
      question_id: a.questionId,
      selected_option: a.selectedOption,
    })),
  };
  const res = await fetch(`${API_BASE}/api/listening/exam/submit`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...getAuthHeaders(),
    },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`提交答案失败: ${res.status} ${text}`);
  }
  return res.json();
}

export async function fetchExamHistory(): Promise<ExamHistoryItem[]> {
  const res = await fetch(`${API_BASE}/api/listening/exam/history`, {
    headers: { ...getAuthHeaders() },
  });
  if (!res.ok) throw new Error(`获取考试历史失败: ${res.status}`);
  const data = await res.json();
  return data.records;
}

export async function fetchExamDetail(examId: string): Promise<ExamResult> {
  const res = await fetch(`${API_BASE}/api/listening/exam/history/${encodeURIComponent(examId)}`, {
    headers: { ...getAuthHeaders() },
  });
  if (!res.ok) throw new Error(`获取考试详情失败: ${res.status}`);
  return res.json();
}

export async function analyzeSentence(text: string): Promise<SentenceAnalysisResult> {
  const res = await fetch(`${API_BASE}/api/listening/analyze`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...getAuthHeaders(),
    },
    body: JSON.stringify({ text }),
  });
  if (!res.ok) throw new Error(`句子分析失败: ${res.status}`);
  return res.json();
}

// ====================== 语法检测 ======================
export async function checkGrammar(text: string): Promise<GrammarCheckResult> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 45000); // 45s timeout
  try {
    const res = await fetch(`${API_BASE}/api/listening/grammar-check`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders(),
      },
      body: JSON.stringify({ text }),
      signal: controller.signal,
    });
    if (!res.ok) {
      // Try to extract backend error detail
      let detail = '';
      try {
        const errBody = await res.json();
        detail = errBody.detail || '';
      } catch { /* ignore parse errors */ }
      throw new Error(detail || `语法检测失败: HTTP ${res.status}`);
    }
    return res.json();
  } finally {
    clearTimeout(timeoutId);
  }
}

export async function deleteExamRecord(examId: string): Promise<void> {
  const res = await fetch(`${API_BASE}/api/listening/exam/history/${encodeURIComponent(examId)}`, {
    method: 'DELETE',
    headers: { ...getAuthHeaders() },
  });
  if (!res.ok) throw new Error(`删除模考记录失败: ${res.status}`);
}

export async function clearExamHistory(): Promise<void> {
  const res = await fetch(`${API_BASE}/api/listening/exam/history`, {
    method: 'DELETE',
    headers: { ...getAuthHeaders() },
  });
  if (!res.ok) throw new Error(`清空模考记录失败: ${res.status}`);
}

// ====================== 认证 ======================
export interface AuthUser {
  id: string;
  email: string;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: AuthUser;
}

export async function register(email: string, password: string): Promise<AuthResponse> {
  const res = await fetch(`${API_BASE}/api/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || 'Registration failed');
  }
  return res.json();
}

export async function login(email: string, password: string): Promise<AuthResponse> {
  const res = await fetch(`${API_BASE}/api/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || 'Login failed');
  }
  return res.json();
}

// ====================== 邮箱验证码认证（仅用于注册）======================
export async function sendVerificationCode(email: string): Promise<{ message: string }> {
  const res = await fetch(`${API_BASE}/api/auth/send-code`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, purpose: 'register' }),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || '发送验证码失败');
  }
  return res.json();
}

export async function verifyCodeAndRegister(
  email: string,
  code: string,
  password: string,
  confirmPassword: string,
): Promise<AuthResponse> {
  const res = await fetch(`${API_BASE}/api/auth/verify-code`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, code, password, confirm_password: confirmPassword }),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || '验证失败');
  }
  return res.json();
}

// ====================== 个人看板统计 ======================
export interface OverviewStats {
  totalMessages: number;
  practiceMinutes: number;
  sceneCount: number;
  wordCount: number;
  examCount: number;
  avgAccuracy: number;
  todayMessages: number;
}

export interface SceneStat {
  scene: string;
  label: string;
  messageCount: number;
}

export interface DailyTrend {
  date: string;
  count: number;
}

export interface SpeakingStats {
  sceneStats: SceneStat[];
  dailyTrend: DailyTrend[];
  totalScenes: number;
  practicedScenes: number;
}

export interface LevelSummary {
  count: number;
  avgAccuracy: number;
  bestAccuracy: number;
}

export interface WeakSection {
  type: string;
  label: string;
  total: number;
  correct: number;
  accuracy: number;
}

export interface ListeningRecord {
  id: string;
  setId: string;
  setName: string;
  level: string;
  totalQuestions: number;
  correctCount: number;
  accuracy: number;
  createdAt: string;
}

export interface ListeningStats {
  records: ListeningRecord[];
  cet4: LevelSummary;
  cet6: LevelSummary;
  weakSections: WeakSection[];
  totalExams: number;
  overallAvgAccuracy: number;
}

export interface WeeklyTrend {
  week: string;
  count: number;
}

export interface RecentWord {
  word: string;
  phonetic: string;
  meaning: string;
  createTime: number;
}

export interface VocabularyStats {
  totalWords: number;
  weeklyTrend: WeeklyTrend[];
  recentWords: RecentWord[];
}

export interface Achievement {
  id: string;
  name: string;
  description: string;
  icon: string;
  unlocked: boolean;
}

export interface StreakStats {
  streak: number;
  activeDates: string[];
  achievements: Achievement[];
  totalActiveDays: number;
}

export async function fetchOverviewStats(): Promise<OverviewStats> {
  const res = await fetch(`${API_BASE}/api/stats/overview`, {
    headers: { ...getAuthHeaders() },
  });
  if (!res.ok) throw new Error(`获取概览失败: ${res.status}`);
  return res.json();
}

export async function fetchSpeakingStats(): Promise<SpeakingStats> {
  const res = await fetch(`${API_BASE}/api/stats/speaking`, {
    headers: { ...getAuthHeaders() },
  });
  if (!res.ok) throw new Error(`获取口语统计失败: ${res.status}`);
  return res.json();
}

export async function fetchListeningStats(): Promise<ListeningStats> {
  const res = await fetch(`${API_BASE}/api/stats/listening`, {
    headers: { ...getAuthHeaders() },
  });
  if (!res.ok) throw new Error(`获取听力统计失败: ${res.status}`);
  return res.json();
}

export async function fetchVocabularyStats(): Promise<VocabularyStats> {
  const res = await fetch(`${API_BASE}/api/stats/vocabulary`, {
    headers: { ...getAuthHeaders() },
  });
  if (!res.ok) throw new Error(`获取词汇统计失败: ${res.status}`);
  return res.json();
}

export async function fetchStreakStats(): Promise<StreakStats> {
  const res = await fetch(`${API_BASE}/api/stats/streak`, {
    headers: { ...getAuthHeaders() },
  });
  if (!res.ok) throw new Error(`获取打卡统计失败: ${res.status}`);
  return res.json();
}

export async function fetchCurrentUser(): Promise<AuthUser | null> {
  const token = sessionStorage.getItem('access_token');
  if (!token) return null;
  try {
    const res = await fetch(`${API_BASE}/api/auth/me`, {
      headers: { 'Authorization': `Bearer ${token}` },
    });
    if (!res.ok) return null;
    return res.json();
  } catch {
    return null;
  }
}
