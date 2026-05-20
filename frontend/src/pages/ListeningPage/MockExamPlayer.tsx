import { useState, useRef, useCallback, useEffect, useMemo } from 'react';
import type { ListeningSet, ListeningQuestion, ExamResult } from '../../types';
import { submitExamAnswers } from '../../services/api';
import { QuestionCard } from './QuestionCard';

const EMOJI_REGEX =
  /[\u{1F600}-\u{1F6FF}\u{1F300}-\u{1F5FF}\u{1F900}-\u{1F9FF}\u{1F1E0}-\u{1F1FF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}\u{FE00}-\u{FE0F}]/gu;

// ====================== Types ======================

type PlayerPhase = 'idle' | 'playing' | 'paused' | 'completed';

interface PlaylistStep {
  kind: 'direction' | 'material' | 'question' | 'answer';
  text?: string;
  questionId?: string;
  questionNumber?: number;
  duration?: number;
  sectionLabel: string;
}

// ====================== Constants ======================

const ANSWER_SECONDS = 15;

const SECTION_DIRECTIONS: Record<string, string> = {
  news_report:
    'Directions: In this section, you will hear three news reports. At the end of each news report, you will hear two or three questions. Both the news report and the questions will be spoken only once. After you hear a question, you must choose the best answer from the four choices marked A, B, C and D.',
  long_conversation:
    'Directions: In this section, you will hear two long conversations. At the end of each conversation, you will hear four questions. Both the conversation and the questions will be spoken only once. After you hear a question, you must choose the best answer from the four choices marked A, B, C and D.',
  passage:
    'Directions: In this section, you will hear three passages. At the end of each passage, you will hear three or four questions. Both the passage and the questions will be spoken only once. After you hear a question, you must choose the best answer from the four choices marked A, B, C and D.',
};

// ====================== Helpers ======================

function cleanText(text: string): string {
  return text.replace(EMOJI_REGEX, '').trim();
}

function buildPlaylist(set: ListeningSet, questions: ListeningQuestion[]): PlaylistStep[] {
  const steps: PlaylistStep[] = [];

  const itemQuestionMap = new Map<string, ListeningQuestion[]>();
  for (const q of questions) {
    const key = q.item_id || q.section_id || '';
    if (!itemQuestionMap.has(key)) itemQuestionMap.set(key, []);
    itemQuestionMap.get(key)!.push(q);
  }

  for (const section of set.sections) {
    const dirText = SECTION_DIRECTIONS[section.sectionType];
    if (dirText) {
      steps.push({ kind: 'direction', text: dirText, sectionLabel: section.name });
    }

    if (section.items && section.items.length > 0) {
      // New data: iterate over items within section
      for (const item of section.items) {
        for (const sentence of item.sentences) {
          if (sentence.en) {
            steps.push({ kind: 'material', text: sentence.en, sectionLabel: item.name });
          }
        }
        const qs = itemQuestionMap.get(item.id) || [];
        for (const q of qs) {
          steps.push({
            kind: 'question',
            text: `Question ${q.question_number}. ${q.question_text}`,
            questionId: q.id,
            questionNumber: q.question_number,
            sectionLabel: item.name,
          });
          steps.push({
            kind: 'answer',
            questionId: q.id,
            questionNumber: q.question_number,
            duration: ANSWER_SECONDS,
            sectionLabel: item.name,
          });
        }
      }
    } else {
      // Old data: section-level sentences (no items)
      for (const sentence of section.sentences) {
        if (sentence.en) {
          steps.push({ kind: 'material', text: sentence.en, sectionLabel: section.name });
        }
      }
      const qs = itemQuestionMap.get(section.id || '') || [];
      for (const q of qs) {
        steps.push({
          kind: 'question',
          text: `Question ${q.question_number}. ${q.question_text}`,
          questionId: q.id,
          questionNumber: q.question_number,
          sectionLabel: section.name,
        });
        steps.push({
          kind: 'answer',
          questionId: q.id,
          questionNumber: q.question_number,
          duration: ANSWER_SECONDS,
          sectionLabel: section.name,
        });
      }
    }
  }

  return steps;
}

// ====================== Component ======================

interface Props {
  set: ListeningSet;
  questions: ListeningQuestion[];
  onFinish: (result: ExamResult) => void;
  onExit: () => void;
}

export function MockExamPlayer({ set, questions, onFinish, onExit }: Props) {
  const playlist = useMemo(() => buildPlaylist(set, questions), [set, questions]);

  // --- UI state ---
  const [phase, setPhase] = useState<PlayerPhase>('idle');
  const [currentStep, setCurrentStep] = useState(-1);
  const [answerTimeLeft, setAnswerTimeLeft] = useState(0);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [showExitConfirm, setShowExitConfirm] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  // --- Refs ---
  const genRef = useRef(0);
  const stepRef = useRef(-1);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const abortRef = useRef<AbortController | null>(null);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // --- Full cleanup ---
  const fullStop = useCallback(() => {
    genRef.current += 1;
    if (timerRef.current !== null) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
    if (abortRef.current) {
      abortRef.current.abort();
      abortRef.current = null;
    }
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current = null;
    }
  }, []);

  useEffect(() => () => fullStop(), [fullStop]);

  // --- TTS speak helper (returns false if cancelled) ---
  const speakText = useCallback(async (text: string, gen: number): Promise<boolean> => {
    const cleaned = cleanText(text);
    if (!cleaned) return true;

    const controller = new AbortController();
    abortRef.current = controller;

    try {
      const params = new URLSearchParams({ text: cleaned, rate: '1.0' });
      const resp = await fetch(`/api/tts?${params}`, { signal: controller.signal });
      if (genRef.current !== gen) return false;

      if (!resp.ok) return true;

      const blob = await resp.blob();
      if (genRef.current !== gen) return false;

      const url = URL.createObjectURL(blob);

      return new Promise((resolve) => {
        const audio = new Audio(url);
        audioRef.current = audio;

        const done = (continued: boolean) => {
          URL.revokeObjectURL(url);
          if (audioRef.current === audio) audioRef.current = null;
          resolve(continued);
        };

        audio.onended = () => done(genRef.current === gen);
        audio.onerror = () => done(true);
        audio.play().catch(() => done(true));
      });
    } catch {
      return true;
    }
  }, []);

  // --- Core: play a single step, then auto-advance ---
  const playStep = useCallback(async (index: number) => {
    if (index >= playlist.length) {
      stepRef.current = -1;
      setCurrentStep(-1);
      setPhase('completed');
      setAnswerTimeLeft(0);
      return;
    }

    const gen = genRef.current;
    stepRef.current = index;
    setCurrentStep(index);

    const step = playlist[index];

    if (step.kind === 'answer') {
      let left = step.duration!;
      setAnswerTimeLeft(left);

      timerRef.current = setInterval(() => {
        left -= 1;
        if (left <= 0) {
          const t = timerRef.current;
          if (t !== null) {
            clearInterval(t);
            timerRef.current = null;
          }
          setAnswerTimeLeft(0);
          if (genRef.current === gen) {
            playStep(index + 1);
          }
        } else {
          setAnswerTimeLeft(left);
        }
      }, 1000);
    } else {
      setAnswerTimeLeft(0);
      const ok = await speakText(step.text!, gen);
      if (!ok) return;
      if (genRef.current === gen) {
        playStep(index + 1);
      }
    }
  }, [playlist, speakText]);

  // --- Controls ---
  const handleStart = useCallback(() => {
    setPhase('playing');
    playStep(0);
  }, [playStep]);

  const handlePause = useCallback(() => {
    setPhase('paused');
    genRef.current += 1;
    if (timerRef.current !== null) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
    if (audioRef.current) {
      audioRef.current.pause();
    }
  }, []);

  const handleResume = useCallback(() => {
    setPhase('playing');
    const idx = stepRef.current;
    if (idx >= 0 && idx < playlist.length) {
      playStep(idx);
    } else if (idx >= playlist.length) {
      setPhase('completed');
    } else {
      playStep(0);
    }
  }, [playStep, playlist.length]);

  // --- Answer selection ---
  const handleSelectOption = useCallback((questionId: string, option: string) => {
    setAnswers((prev) => ({ ...prev, [questionId]: option }));
  }, []);

  // --- Submit ---
  const answeredCount = Object.keys(answers).length;
  const allAnswered = questions.every((q) => answers[q.id]);
  const canSubmit = phase !== 'idle' && allAnswered && !submitting;

  const handleSubmit = useCallback(async () => {
    if (!canSubmit) return;
    setSubmitting(true);
    try {
      const answerList = Object.entries(answers).map(([questionId, selectedOption]) => ({
        questionId,
        selectedOption,
      }));
      const result = await submitExamAnswers(set.id, answerList);
      onFinish(result);
    } catch {
      setSubmitting(false);
    }
  }, [canSubmit, answers, set.id, onFinish]);

  // --- Derived ---
  const activeQuestionId = useMemo(() => {
    if (currentStep < 0 || currentStep >= playlist.length) return null;
    const step = playlist[currentStep];
    return step.questionId || null;
  }, [currentStep, playlist]);

  const statusText = useMemo(() => {
    if (phase === 'idle') return '点击「开始考试」进入全真模拟';
    if (phase === 'paused') return '已暂停';
    if (phase === 'completed') return '音频播放完毕，请检查答案并提交';
    if (currentStep < 0 || currentStep >= playlist.length) return '';

    const step = playlist[currentStep];
    switch (step.kind) {
      case 'direction':
        return `正在播放: ${step.sectionLabel} — 考试指令`;
      case 'material':
        return `正在播放材料 · ${step.sectionLabel}`;
      case 'question':
        return `正在播放: Question ${step.questionNumber}`;
      case 'answer':
        return `答题时间剩余 ${answerTimeLeft}s · Question ${step.questionNumber}`;
    }
  }, [phase, currentStep, playlist, answerTimeLeft]);

  const questionGroups = useMemo(() => {
    const groups = new Map<string, ListeningQuestion[]>();
    for (const q of questions) {
      const key = q.item_name || q.section_name || q.section_id || '题目';
      if (!groups.has(key)) groups.set(key, []);
      groups.get(key)!.push(q);
    }
    return [...groups.entries()];
  }, [questions]);

  const completedTtsSteps = useMemo(() => {
    if (currentStep < 0) return 0;
    let count = 0;
    for (let i = 0; i <= currentStep && i < playlist.length; i++) {
      if (playlist[i].kind !== 'answer') count++;
    }
    return count;
  }, [currentStep, playlist]);

  const totalTtsSteps = useMemo(() => {
    return playlist.filter((s) => s.kind !== 'answer').length;
  }, [playlist]);

  // --- Render ---
  return (
    <div className="exam-unified">
      {/* Exit confirmation modal */}
      {showExitConfirm && (
        <div className="exam-exit-overlay" onClick={() => setShowExitConfirm(false)}>
          <div className="exam-exit-dialog" onClick={(e) => e.stopPropagation()}>
            <div className="exam-exit-dialog-title">确认退出模拟考试？</div>
            <div className="exam-exit-dialog-body">
              已作答 {answeredCount}/{questions.length} 题，退出后答题进度将丢失。
            </div>
            <div className="exam-exit-dialog-actions">
              <button className="exam-exit-btn cancel" onClick={() => setShowExitConfirm(false)}>
                继续考试
              </button>
              <button className="exam-exit-btn confirm" onClick={onExit}>
                确认退出
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Top bar */}
      <div className="exam-topbar">
        <button className="exam-topbar-exit" onClick={() => setShowExitConfirm(true)}>
          &larr; 退出模拟
        </button>
        <span className="exam-topbar-title">{set.name} — 全真模拟</span>
        <span className="exam-topbar-progress">
          已答 <strong>{answeredCount}</strong>/{questions.length}
        </span>
      </div>

      {/* Player bar */}
      <div className="exam-player-bar">
        <div className="exam-player-left">
          {phase === 'idle' && (
            <button className="exam-player-btn primary" onClick={handleStart}>
              ▶ 开始考试
            </button>
          )}
          {phase === 'playing' && (
            <button className="exam-player-btn" onClick={handlePause}>
              ⏸ 暂停
            </button>
          )}
          {phase === 'paused' && (
            <button className="exam-player-btn primary" onClick={handleResume}>
              ▶ 继续
            </button>
          )}
          {phase === 'completed' && (
            <span className="exam-player-done">全部播放完毕</span>
          )}
        </div>
        <div className="exam-player-center">
          <span className="exam-player-status">{statusText}</span>
          {(phase === 'playing' || phase === 'paused') && totalTtsSteps > 0 && (
            <span className="exam-player-step-count">
              音频 {Math.min(completedTtsSteps + 1, totalTtsSteps)}/{totalTtsSteps}
            </span>
          )}
        </div>
        <div className="exam-player-right">
          {phase === 'playing' && answerTimeLeft > 0 && (
            <span className="exam-player-timer">{answerTimeLeft}s</span>
          )}
        </div>
      </div>

      {/* Answer sheet */}
      <div className="exam-answer-sheet">
        {questionGroups.map(([groupName, qs]) => (
          <div key={groupName} className="exam-section-group">
            <h4 className="exam-section-title">{groupName}</h4>
            {qs.map((q) => (
              <QuestionCard
                key={q.id}
                question={q}
                selectedOption={answers[q.id] || ''}
                disabled={false}
                showResult={false}
                highlighted={q.id === activeQuestionId}
                onSelect={(opt) => handleSelectOption(q.id, opt)}
              />
            ))}
          </div>
        ))}

        {phase !== 'idle' && (
          <div className="exam-submit-area">
            {phase !== 'completed' && (
              <div className="exam-submit-warning">
                音频尚未播放完毕，提前提交将无法修改答案
              </div>
            )}
            {!allAnswered && (
              <div className="exam-submit-warning">
                还有 {questions.length - answeredCount} 题未作答，请检查后提交
              </div>
            )}
            <button
              className="exam-submit-btn"
              disabled={!allAnswered || submitting}
              onClick={handleSubmit}
            >
              {submitting ? '提交中...' : `提交答案 (${answeredCount}/${questions.length})`}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
