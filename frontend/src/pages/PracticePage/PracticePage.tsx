import { useState, useCallback, useEffect, useRef } from 'react';
import { initScene, checkGrammar, sendVoiceMessage } from '../../services/api';
import { useSpeechSynthesis } from '../../hooks/useSpeechSynthesis';
import { useChat } from '../../hooks/useChat';
import { useRecording } from '../../hooks/useRecording';
import { useToast } from '../../components/Toast/toastContext';
import { SceneBar } from './SceneBar';
import { ChatBox } from './ChatBox';
import { InputArea } from './InputArea';
import { TranslatePanel } from './TranslatePanel';
import { WordQueryModule } from './WordQueryModule';
import { SentenceTranslateModule } from './SentenceTranslateModule';
import { GrammarScorePanel } from './GrammarScorePanel';
import type { GrammarCheckResult } from '../../types';

const SCENE_OPTIONS = [
  { value: '0', label: '英语自由交流' },
  { value: '1', label: '餐厅点餐用餐' },
  { value: '2', label: '职场英文面试' },
  { value: '3', label: '酒店入住办理' },
  { value: '4', label: '日常居家交流' },
  { value: '5', label: '出行问路乘车' },
  { value: '6', label: '商场购物逛街' },
  { value: '7', label: '看病就医问诊' },
  { value: '8', label: '校园师生交流' },
  { value: '9', label: '日常社交寒暄' },
  { value: '10', label: '旅游景点沟通' },
  { value: '11', label: '职场工作沟通' },
  { value: '12', label: '生活办事咨询' },
  { value: '13', label: '电话微信沟通' },
  { value: '14', label: '兴趣爱好闲聊' },
  { value: '15', label: '机场高铁出行' },
  { value: '16', label: '租房看房沟通' },
];

export function PracticePage() {
  const [scene, setScene] = useState('free_talk');
  const [sceneChoice, setSceneChoice] = useState('0');
  const [speechRate, setSpeechRate] = useState(1.0);
  const [isTranslateVisible, setIsTranslateVisible] = useState(() => {
    return localStorage.getItem('translate_visible_free_talk') === 'true';
  });
  const [rightModule, setRightModule] = useState<'word' | 'translate' | 'grammar'>('word');
  const [grammarCheckText, setGrammarCheckText] = useState<string | null>(null);
  const [prefillText, setPrefillText] = useState<string | null>(null);

  // ---- Grammar state (lifted from SentenceTranslateModule) ----
  const [grammarResult, setGrammarResult] = useState<GrammarCheckResult | null>(null);
  const [grammarLoading, setGrammarLoading] = useState(false);
  const [grammarError, setGrammarError] = useState('');

  const speak = useSpeechSynthesis(speechRate);
  const { messages, translations, isLoading, sendText, sendVoice, clearHistory, pendingAutoPlayRef } = useChat(scene);
  const { showToast } = useToast();

  const handleVoiceSend = useCallback(
    (blob: Blob) => {
      sendVoice(blob);
    },
    [sendVoice],
  );

  const recording = useRecording(handleVoiceSend);

  // ---- Grammar recording (separate instance for grammar tab) ----
  const handleGrammarVoiceSend = useCallback(
    async (blob: Blob) => {
      try {
        const res = await sendVoiceMessage(blob, scene, []);
        if (res.user_text) {
          setGrammarCheckText(res.user_text);
        } else {
          showToast('语音识别未返回文本，请重试', 'warning');
        }
      } catch {
        showToast('语音识别失败，请重试', 'warning');
      }
    },
    [scene, showToast],
  );
  const grammarRecording = useRecording(handleGrammarVoiceSend);

  const handleSendText = useCallback(
    (text: string) => {
      sendText(text);
    },
    [sendText],
  );

  const handleSceneChange = useCallback(
    async (choice: string) => {
      setSceneChoice(choice);
      try {
        const data = await initScene(choice);
        const key = `chat_history_${data.scene}`;
        if (!localStorage.getItem(key)) {
          localStorage.setItem(
            key,
            JSON.stringify([{ role: 'assistant', content: data.initial_message }]),
          );
        }
        setScene(data.scene);
      } catch {
        showToast('场景加载失败', 'warning');
      }
    },
    [showToast],
  );

  const handleClearHistory = useCallback(() => {
    clearHistory();
    showToast('聊天记录已清空，开场白已保留！', 'success');
  }, [clearHistory, showToast]);

  const handleGrammarCheck = useCallback((text: string) => {
    setGrammarCheckText(text);
    setRightModule('grammar');
  }, []);

  const handleGrammarTextSend = useCallback((text: string) => {
    setGrammarCheckText(text);
  }, []);

  const handleFillInput = useCallback((text: string) => {
    setPrefillText(text);
  }, []);

  const handlePrefillConsumed = useCallback(() => {
    setPrefillText(null);
  }, []);

  // ---- Grammar check trigger ----
  useEffect(() => {
    if (!grammarCheckText) return;

    const text = grammarCheckText.trim();

    if (!text || !/[a-zA-Z]/.test(text)) {
      showToast('请输入英文内容后再检测语法', 'warning');
      setGrammarCheckText(null);
      return;
    }

    setGrammarLoading(true);
    setGrammarError('');
    setGrammarResult(null);

    let cancelled = false;

    checkGrammar(text)
      .then((data) => {
        if (!cancelled) setGrammarResult(data);
      })
      .catch(() => {
        if (!cancelled) setGrammarError('语法检测失败，请稍后重试');
      })
      .finally(() => {
        if (!cancelled) setGrammarLoading(false);
        setGrammarCheckText(null);
      });

    return () => { cancelled = true; };
  }, [grammarCheckText]); // eslint-disable-line react-hooks/exhaustive-deps

  // Sync translation visibility with persisted per-scene preference
  useEffect(() => {
    const saved = localStorage.getItem(`translate_visible_${scene}`);
    setIsTranslateVisible(saved === 'true');
  }, [scene]);

  // Initialize
  useEffect(() => {
    handleSceneChange('0');
  }, []);

  // Auto-speak AI responses — only when triggered by a new user-initiated reply
  const prevLenRef = useRef(0);
  useEffect(() => {
    if (messages.length > prevLenRef.current && messages.length > 0) {
      const last = messages[messages.length - 1];
      if (last.role === 'assistant' && pendingAutoPlayRef.current) {
        pendingAutoPlayRef.current = false;
        speak(last.content);
      }
    }
    prevLenRef.current = messages.length;
  }, [messages, speak, pendingAutoPlayRef]);

  return (
    <div className="page">
      <h1>SceneTalk — 英语口语练习</h1>
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: isTranslateVisible ? '1.4fr 1fr 0.9fr' : '1.2fr 1fr',
          gap: 16,
          width: '100%',
          height: 'calc(100vh - 120px)',
          overflow: 'hidden',
        }}
      >
        {/* Left: Chat */}
        <div className="panel">
          <SceneBar
            sceneChoice={sceneChoice}
            onSceneChange={handleSceneChange}
            speechRate={speechRate}
            onSpeechRateChange={setSpeechRate}
            isTranslateVisible={isTranslateVisible}
            onToggleTranslate={() => {
              const next = !isTranslateVisible;
              setIsTranslateVisible(next);
              localStorage.setItem(`translate_visible_${scene}`, String(next));
            }}
            onClearHistory={handleClearHistory}
          />
          <ChatBox messages={messages} onSpeak={speak} onGrammarCheck={handleGrammarCheck} />
          <InputArea
            recording={recording}
            onSendText={handleSendText}
            isLoading={isLoading}
            prefillText={prefillText}
            onPrefillConsumed={handlePrefillConsumed}
          />
        </div>

        {/* Middle: Translation */}
        {isTranslateVisible && (
          <div className="panel">
            <h3 style={{ marginBottom: 12, fontFamily: 'var(--font-mono)', fontSize: 14, color: 'var(--ink-muted)', flexShrink: 0 }}>
              实时翻译
            </h3>
            <TranslatePanel translations={translations} onSpeak={speak} />
          </div>
        )}

        {/* Right: Word Query / Sentence Translate / Grammar Score */}
        <div className="panel">
          <div style={{ display: 'flex', gap: 10, marginBottom: 15 }}>
            <button
              className={`toggle-btn${rightModule === 'word' ? ' active' : ''}`}
              onClick={() => setRightModule('word')}
            >
              单词查询
            </button>
            <button
              className={`toggle-btn${rightModule === 'translate' ? ' active' : ''}`}
              onClick={() => setRightModule('translate')}
            >
              句子翻译
            </button>
            <button
              className={`toggle-btn${rightModule === 'grammar' ? ' active' : ''}`}
              onClick={() => setRightModule('grammar')}
            >
              语法打分
            </button>
          </div>
          {rightModule === 'word' ? (
            <WordQueryModule onSpeak={speak} onToast={showToast} />
          ) : rightModule === 'translate' ? (
            <SentenceTranslateModule onSpeak={speak} />
          ) : (
            <GrammarScorePanel
              sourceText=""
              result={grammarResult}
              loading={grammarLoading}
              error={grammarError}
              onFillInput={handleFillInput}
              onSpeak={speak}
              recording={grammarRecording}
              onSendText={handleGrammarTextSend}
            />
          )}
        </div>
      </div>
    </div>
  );
}
