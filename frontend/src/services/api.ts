import type { ConversationMessage, WordData, SentenceItem, ListeningSetMeta, ListeningSet, ListeningQuestion, ExamResult, ExamHistoryItem, ListeningLevel, SentenceAnalysisResult, GrammarCheckResult } from '../types';

const API_BASE = 'http://127.0.0.1:8000';

// ====================== Auth token 管理 ======================
function getAuthHeaders(): Record<string, string> {
  const token = localStorage.getItem('access_token');
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
  const token = localStorage.getItem('access_token');
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
