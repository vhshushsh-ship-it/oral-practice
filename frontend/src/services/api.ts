import type { ConversationMessage, WordData, SentenceItem, ListeningSetMeta, ListeningSet } from '../types';

const API_BASE = 'http://127.0.0.1:8000';

async function post(path: string, body: Record<string, string>): Promise<Response> {
  const formBody = new URLSearchParams(body).toString();
  return fetch(`${API_BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
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
  });
  if (!res.ok) throw new Error(`请求失败，状态码：${res.status}`);
  return res.json();
}

// ====================== 句子收藏翻译 ======================
export async function translateSentence(text: string): Promise<string> {
  return translateToChinese(text);
}

// ====================== 听力练习 ======================
export async function fetchListeningSets(): Promise<ListeningSetMeta[]> {
  const res = await fetch(`${API_BASE}/api/listening/sets`);
  if (!res.ok) throw new Error(`获取听力套题列表失败: ${res.status}`);
  const data = await res.json();
  return data.sets;
}

export async function fetchListeningSetDetail(setId: string): Promise<ListeningSet> {
  const res = await fetch(`${API_BASE}/api/listening/sets/${encodeURIComponent(setId)}`);
  if (!res.ok) throw new Error(`获取听力套题详情失败: ${res.status}`);
  const data = await res.json();
  return data.set;
}
