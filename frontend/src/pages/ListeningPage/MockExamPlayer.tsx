import { useState, useRef, useCallback, useEffect, useMemo } from 'react';
import type { ListeningSet, ListeningQuestion, ExamResult, ExamAnswerDetail } from '../../types';
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
  const [showSubmitConfirm, setShowSubmitConfirm] = useState(false);
  const [showResultModal, setShowResultModal] = useState(false);
  const [lastResult, setLastResult] = useState<ExamResult | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState('');

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

  // --- Submit flow ---
  const answeredCount = Object.keys(answers).length;
  const unansweredCount = questions.length - answeredCount;
  const isAudioActive = phase === 'playing';

  const handleSubmitClick = useCallback(() => {
    setSubmitError('');
    setShowSubmitConfirm(true);
  }, []);

  const handleConfirmSubmit = useCallback(async () => {
    setShowSubmitConfirm(false);
    setSubmitting(true);
    setSubmitError('');

    fullStop();
    setPhase('completed');

    try {
      const answerList = Object.entries(answers).map(([questionId, selectedOption]) => ({
        questionId,
        selectedOption,
      }));
      const result = await submitExamAnswers(set.id, answerList);
      setLastResult(result);
      setShowResultModal(true);
      onFinish(result);
    } catch {
      setSubmitError('提交失败，请检查网络后重试');
    } finally {
      setSubmitting(false);
    }
  }, [answers, set.id, onFinish, fullStop]);

  const handleCloseResult = useCallback(() => {
    setShowResultModal(false);
    onExit();
  }, [onExit]);

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

  // --- Result data ---
  const correctDetails = useMemo(() =>
    (lastResult?.details ?? []).filter((d) => d.isCorrect).sort((a, b) => a.questionNumber - b.questionNumber),
  [lastResult]);

  const wrongDetails = useMemo(() =>
    (lastResult?.details ?? []).filter((d) => !d.isCorrect).sort((a, b) => a.questionNumber - b.questionNumber),
  [lastResult]);

  const accuracyClass = lastResult
    ? lastResult.accuracy >= 80 ? 'good' : lastResult.accuracy >= 60 ? 'fair' : 'poor'
    : '';

  // --- Build confirm message ---
  const confirmMessages: string[] = [];
  if (unansweredCount > 0) {
    confirmMessages.push(`还有 ${unansweredCount} 道题目未作答，提交后将无法修改答案，是否确认提交？`);
  }
  if (isAudioActive) {
    confirmMessages.push('音频尚未播放完毕，提交后将无法继续听题，是否确认提交？');
  }
  if (confirmMessages.length === 0) {
    confirmMessages.push('确认提交答案？提交后将无法修改。');
  }

  // --- Render ---
  return (
    <div className="exam-unified">
      {/* ========== Exit confirmation modal ========== */}
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

      {/* ========== Submit confirmation modal ========== */}
      {showSubmitConfirm && (
        <div className="exam-exit-overlay" onClick={() => setShowSubmitConfirm(false)}>
          <div className="exam-exit-dialog" onClick={(e) => e.stopPropagation()}>
            <div className="exam-exit-dialog-title">确认提交答案</div>
            <div className="exam-exit-dialog-body">
              {confirmMessages.map((msg, i) => (
                <p key={i} style={i > 0 ? { marginTop: 8 } : undefined}>{msg}</p>
              ))}
              <p style={{ marginTop: 8, fontSize: 12, color: 'var(--ink-muted)' }}>
                已作答 {answeredCount}/{questions.length} 题
              </p>
            </div>
            <div className="exam-exit-dialog-actions">
              <button className="exam-exit-btn cancel" onClick={() => setShowSubmitConfirm(false)}>
                取消
              </button>
              <button className="exam-exit-btn confirm" onClick={handleConfirmSubmit}>
                确认提交
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ========== Result modal ========== */}
      {showResultModal && lastResult && (
        <div className="exam-result-overlay">
          <div className="exam-result-modal">
            {/* Header */}
            <div className="exam-result-header">
              <div className="exam-result-header-title">成绩报告</div>
              <div className="exam-result-header-set">{set.name}</div>
            </div>

            {/* Score summary */}
            <div className="exam-result-score-area">
              <div className={`exam-result-accuracy ${accuracyClass}`}>
                {lastResult.accuracy}%
              </div>
              <div className="exam-result-score-label">正确率</div>
              <div className="exam-result-score-detail">
                <div className="exam-result-stat">
                  <span className="exam-result-stat-num correct">{lastResult.correctCount}</span>
                  <span className="exam-result-stat-label">答对</span>
                </div>
                <div className="exam-result-stat-divider" />
                <div className="exam-result-stat">
                  <span className="exam-result-stat-num wrong">{lastResult.totalQuestions - lastResult.correctCount}</span>
                  <span className="exam-result-stat-label">答错</span>
                </div>
                <div className="exam-result-stat-divider" />
                <div className="exam-result-stat">
                  <span className="exam-result-stat-num">{lastResult.totalQuestions}</span>
                  <span className="exam-result-stat-label">总题数</span>
                </div>
              </div>
            </div>

            {/* Detail list */}
            <div className="exam-result-detail-area">
              {wrongDetails.length > 0 && (
                <div className="exam-result-detail-section">
                  <div className="exam-result-detail-section-title wrong">
                    答错题目 ({wrongDetails.length})
                  </div>
                  {wrongDetails.map((d) => (
                    <ResultDetailRow key={d.questionId} detail={d} />
                  ))}
                </div>
              )}
              {correctDetails.length > 0 && (
                <div className="exam-result-detail-section">
                  <div className="exam-result-detail-section-title correct">
                    答对题目 ({correctDetails.length})
                  </div>
                  {correctDetails.map((d) => (
                    <ResultDetailRow key={d.questionId} detail={d} />
                  ))}
                </div>
              )}
            </div>

            {/* Actions */}
            <div className="exam-result-actions">
              <button className="exam-result-btn secondary" onClick={handleCloseResult}>
                返回练习
              </button>
              <button className="exam-result-btn primary" onClick={handleCloseResult}>
                查看错题解析
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ========== Submit error toast ========== */}
      {submitError && (
        <div className="exam-submit-error">
          <span>{submitError}</span>
          <button onClick={() => setSubmitError('')} className="exam-submit-error-close">&times;</button>
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
              &#9654; 开始考试
            </button>
          )}
          {phase === 'playing' && (
            <button className="exam-player-btn" onClick={handlePause}>
              &#9208; 暂停
            </button>
          )}
          {phase === 'paused' && (
            <button className="exam-player-btn primary" onClick={handleResume}>
              &#9654; 继续
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
          {phase !== 'idle' && (
            <button
              className="exam-player-btn submit-btn"
              disabled={submitting}
              onClick={handleSubmitClick}
            >
              {submitting ? '提交中...' : `提交答案 (${answeredCount}/${questions.length})`}
            </button>
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
      </div>
    </div>
  );
}

// ====================== Result detail row ======================

function ResultDetailRow({ detail }: { detail: ExamAnswerDetail }) {
  const [expanded, setExpanded] = useState(false);

  const optionLabels: Record<string, string> = {
    A: detail.optionA,
    B: detail.optionB,
    C: detail.optionC,
    D: detail.optionD,
  };

  return (
    <div
      className={`exam-result-detail-row${expanded ? ' expanded' : ''}`}
      onClick={() => setExpanded(!expanded)}
    >
      <div className="exam-result-detail-row-top">
        <span className="exam-result-detail-num">#{detail.questionNumber}</span>
        <span className="exam-result-detail-text">{detail.questionText}</span>
        <span className="exam-result-detail-answers">
          {detail.isCorrect ? (
            <span className="exam-result-badge correct">{detail.userAnswer}</span>
          ) : (
            <>
              <span className="exam-result-badge wrong">{detail.userAnswer || '未答'}</span>
              <span className="exam-result-badge-arrow">&rarr;</span>
              <span className="exam-result-badge correct">{detail.correctAnswer}</span>
            </>
          )}
        </span>
      </div>
      {expanded && (
        <div className="exam-result-detail-row-options">
          {(['A', 'B', 'C', 'D'] as const).map((opt) => {
            const isCorrect = opt === detail.correctAnswer;
            const isUser = opt === detail.userAnswer;
            let cls = 'exam-result-option';
            if (isCorrect) cls += ' is-correct';
            if (isUser && !detail.isCorrect) cls += ' is-wrong';
            return (
              <div key={opt} className={cls}>
                <span className="exam-result-option-label">{opt}.</span>
                <span>{optionLabels[opt]}</span>
                {isCorrect && <span className="exam-result-option-tag correct">正确答案</span>}
                {isUser && !isCorrect && <span className="exam-result-option-tag wrong">你的答案</span>}
                {isUser && isCorrect && <span className="exam-result-option-tag correct">你的答案</span>}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
