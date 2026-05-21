import { useState, useCallback, useEffect, useMemo, useRef, useLayoutEffect } from 'react';
import type { ListeningSetMeta, ListeningSet, ListeningSection, ListeningSentence, ListeningLevel, ListeningQuestion, ExamResult, ExamHistoryItem } from '../../types';
import { fetchListeningSets, fetchListeningSetDetail, fetchQuestions, fetchExamHistory, fetchExamDetail } from '../../services/api';
import { useSpeechSynthesis } from '../../hooks/useSpeechSynthesis';
import { useSequentialTTS } from '../../hooks/useSequentialTTS';
import { useRecording } from '../../hooks/useRecording';
import { useRecordingPlayback } from '../../hooks/useRecordingPlayback';
import { useSentenceCollection } from '../../hooks/useSentenceCollection';
import { useToast } from '../../components/Toast/toastContext';
import { LevelTabs } from './LevelTabs';
import { SetSelector } from './SetSelector';
import { SectionSelector } from './SectionSelector';
import { ListeningPlayer } from './ListeningPlayer';
import { SentenceItem } from './SentenceItem';
import { MockExamPlayer } from './MockExamPlayer';
import { QuestionCard } from './QuestionCard';
import { ExamResultView } from './ExamResultView';
import { ExamHistoryPanel } from './ExamHistoryPanel';
import { SentenceAnalysis } from './SentenceAnalysis';

type PageStep = 'level_select' | 'set_select' | 'section_select' | 'practice' | 'exam' | 'exam_result';

function saveProgress(setId: string, sentenceIds: string[], total: number) {
  try {
    const key = `listening_progress_${setId}`;
    const raw = localStorage.getItem(key);
    const existing = raw ? JSON.parse(raw) : { played: [], total };
    const playedSet = new Set<string>(existing.played || []);
    for (const id of sentenceIds) playedSet.add(id);
    localStorage.setItem(key, JSON.stringify({ played: [...playedSet], total }));
  } catch { /* ignore */ }
}

const LEVEL_LABEL: Record<string, string> = { cet4: '四级真题', cet6: '六级真题' };

export function ListeningPage() {
  const [step, setStep] = useState<PageStep>('level_select');
  const [selectedLevel, setSelectedLevel] = useState<ListeningLevel | null>(null);
  const [setList, setSetList] = useState<ListeningSetMeta[]>([]);
  const [setListLoading, setSetListLoading] = useState(false);
  const [selectedSet, setSelectedSet] = useState<ListeningSet | null>(null);
  const [selectedSetLoading, setSelectedSetLoading] = useState(false);
  const [selectedSection, setSelectedSection] = useState<ListeningSection | null>(null);
  const [showTranslations, setShowTranslations] = useState(true);
  const [recordingTarget, setRecordingTarget] = useState<string | null>(null);
  const [practiceQuestions, setPracticeQuestions] = useState<ListeningQuestion[]>([]);
  const [examQuestions, setExamQuestions] = useState<ListeningQuestion[]>([]);
  const [currentExamResult, setCurrentExamResult] = useState<ExamResult | null>(null);
  const [examHistory, setExamHistory] = useState<ExamHistoryItem[]>([]);
  const [examHistoryLoading, setExamHistoryLoading] = useState(false);
  const [analysisSentence, setAnalysisSentence] = useState<ListeningSentence | null>(null);
  const sentenceListRef = useRef<HTMLDivElement | null>(null);
  const savedScrollTopRef = useRef(0);

  const seq = useSequentialTTS(1.0);
  const speak = useSpeechSynthesis(1.0);
  const { addSentence } = useSentenceCollection();
  const { showToast } = useToast();
  const recordingPlayback = useRecordingPlayback();
  const recording = useRecording(recordingPlayback.storeRecording);

  const isPlayingFull = seq.playState === 'playing' || seq.playState === 'paused';

  const practiceSentences = useMemo(() => {
    if (!selectedSet) return [];
    if (selectedSection && selectedSection.id !== null) {
      if (selectedSection.items && selectedSection.items.length > 0) {
        return selectedSection.items.flatMap((item) => item.sentences);
      }
      return selectedSection.sentences;
    }
    return selectedSet.sections.flatMap((s) => {
      if (s.items && s.items.length > 0) return s.items.flatMap((item) => item.sentences);
      return s.sentences;
    });
  }, [selectedSet, selectedSection]);

  const totalSetSentences = useMemo(() => {
    if (!selectedSet) return 0;
    return selectedSet.sections.reduce((sum, s) => {
      if (s.items && s.items.length > 0) {
        return sum + s.items.reduce((isum, item) => isum + item.sentences.length, 0);
      }
      return sum + s.sentences.length;
    }, 0);
  }, [selectedSet]);

  // Load sets when level is selected
  useEffect(() => {
    if (!selectedLevel) return;
    let cancelled = false;
    setSetListLoading(true);
    fetchListeningSets(selectedLevel)
      .then((sets) => { if (!cancelled) setSetList(sets); })
      .catch(() => { if (!cancelled) showToast('加载真题列表失败', 'warning'); })
      .finally(() => { if (!cancelled) setSetListLoading(false); });
    return () => { cancelled = true; };
  }, [selectedLevel, showToast]);

  // Load exam history on mount
  useEffect(() => {
    setExamHistoryLoading(true);
    fetchExamHistory()
      .then(setExamHistory)
      .catch(() => {})
      .finally(() => setExamHistoryLoading(false));
  }, []);

  // ─── Navigation handlers ───

  const handleSelectLevel = useCallback((level: ListeningLevel) => {
    setSelectedLevel(level);
    setSelectedSet(null);
    setSelectedSection(null);
    setStep('set_select');
  }, []);

  const goSetSelect = useCallback(() => {
    seq.stop();
    setSelectedSet(null);
    setSelectedSection(null);
    setCurrentExamResult(null);
    setExamQuestions([]);
    setStep('set_select');
  }, [seq]);

  const goLevelSelect = useCallback(() => {
    seq.stop();
    setSelectedLevel(null);
    setSelectedSet(null);
    setSelectedSection(null);
    setCurrentExamResult(null);
    setExamQuestions([]);
    setStep('level_select');
  }, [seq]);

  const goSectionSelect = useCallback(() => {
    seq.stop();
    setSelectedSection(null);
    setStep('section_select');
  }, [seq]);

  const handleStartPractice = useCallback(async (meta: ListeningSetMeta) => {
    seq.stop();
    setSelectedSetLoading(true);
    setSelectedSet(null);
    setSelectedSection(null);
    try {
      const [detail, qData] = await Promise.all([
        fetchListeningSetDetail(meta.id),
        fetchQuestions(meta.id),
      ]);
      setSelectedSet(detail);
      setPracticeQuestions(qData.questions);
      const hasSections = detail.sections.some((s) => s.id !== null);
      setStep(hasSections ? 'section_select' : 'practice');
    } catch {
      showToast('加载真题失败，请重试', 'warning');
    } finally {
      setSelectedSetLoading(false);
    }
  }, [seq, showToast]);

  const handleStartExam = useCallback(async (meta: ListeningSetMeta) => {
    seq.stop();
    setSelectedSetLoading(true);
    setSelectedSet(null);
    try {
      const [detail, qData] = await Promise.all([
        fetchListeningSetDetail(meta.id),
        fetchQuestions(meta.id),
      ]);
      setSelectedSet(detail);
      setExamQuestions(qData.questions);
      setStep('exam');
    } catch {
      showToast('加载失败，请重试', 'warning');
    } finally {
      setSelectedSetLoading(false);
    }
  }, [seq, showToast]);

  const handleSelectSection = useCallback((section: ListeningSection) => {
    setSelectedSection(section);
    setStep('practice');
  }, []);

  const handleExamFinish = useCallback((result: ExamResult) => {
    setCurrentExamResult(result);
    setExamHistory((prev) => [
      {
        id: result.id,
        set_id: result.set_id,
        set_name: selectedSet?.name ?? '',
        totalQuestions: result.totalQuestions,
        correctCount: result.correctCount,
        accuracy: result.accuracy,
        createdAt: result.createdAt,
      },
      ...prev,
    ]);
  }, [selectedSet]);

  const handleViewHistoryRecord = useCallback(async (record: ExamHistoryItem) => {
    try {
      const detail = await fetchExamDetail(record.id);
      setCurrentExamResult(detail);
      setStep('exam_result');
    } catch {
      showToast('加载考试详情失败', 'warning');
    }
  }, [showToast]);

  const handleAnalyzeSentence = useCallback((s: ListeningSentence) => {
    if (sentenceListRef.current) {
      savedScrollTopRef.current = sentenceListRef.current.scrollTop;
    }
    setAnalysisSentence(s);
  }, []);

  const handleCloseAnalysis = useCallback(() => {
    setAnalysisSentence(null);
  }, []);

  useLayoutEffect(() => {
    if (!analysisSentence && sentenceListRef.current && savedScrollTopRef.current > 0) {
      sentenceListRef.current.scrollTop = savedScrollTopRef.current;
    }
  }, [analysisSentence]);

  // ─── Playback handlers ───

  const handleFullPlay = useCallback(() => {
    const texts = practiceSentences.map((s) => s.en);
    if (texts.length === 0) return;
    seq.play(texts, 0);
    if (selectedSet) {
      saveProgress(selectedSet.id, practiceSentences.map((s) => s.id), totalSetSentences);
    }
  }, [practiceSentences, seq, selectedSet, totalSetSentences]);

  const handleSinglePlay = useCallback((text: string, sentenceId: string) => {
    speak(text);
    if (selectedSet) {
      saveProgress(selectedSet.id, [sentenceId], totalSetSentences);
    }
  }, [speak, selectedSet, totalSetSentences]);

  const handleStartRecord = useCallback((sentenceId: string) => {
    recordingPlayback.clearRecording();
    setRecordingTarget(sentenceId);
    recording.start();
  }, [recording, recordingPlayback]);

  const handleStopRecord = useCallback(() => {
    recording.stop();
  }, [recording]);

  const handlePlayRecording = useCallback(() => {
    recordingPlayback.playRecording();
  }, [recordingPlayback]);

  const handleCollect = useCallback(async (text: string) => {
    const result = await addSentence(text);
    if (result === 'exists') {
      showToast('该句子已收藏！', 'info');
    } else {
      showToast('句子收藏成功！', 'success');
    }
  }, [addSentence, showToast]);

  // ─── Breadcrumb ───

  const breadcrumb = useMemo(() => {
    const items: { label: string; onClick?: () => void }[] = [];
    if (step === 'level_select') return items;

    items.push({ label: '四六级听力练习', onClick: goLevelSelect });

    const lvl = LEVEL_LABEL[selectedLevel ?? ''] ?? '';
    if (step === 'set_select') {
      items.push({ label: lvl });
      return items;
    }
    items.push({ label: lvl, onClick: goSetSelect });

    const setName = selectedSet?.name ?? '';
    if (step === 'section_select') {
      if (setName) items.push({ label: setName });
      return items;
    }

    if (step === 'practice') {
      if (setName) items.push({ label: setName, onClick: goSectionSelect });
      if (selectedSection?.id) items.push({ label: selectedSection.name });
      return items;
    }

    if (step === 'exam') {
      if (setName) items.push({ label: setName });
      items.push({ label: '全真模拟' });
      return items;
    }

    if (step === 'exam_result') {
      if (setName) items.push({ label: setName });
      items.push({ label: '成绩报告' });
      return items;
    }

    return items;
  }, [step, selectedLevel, selectedSet, selectedSection, goLevelSelect, goSetSelect, goSectionSelect]);

  // ─── Render ───

  const renderBreadcrumb = () => {
    if (breadcrumb.length === 0) return null;
    return (
      <div className="listening-breadcrumb">
        {breadcrumb.map((item, i) => (
          <span key={i}>
            {i > 0 && <span className="breadcrumb-sep">&gt;</span>}
            {item.onClick ? (
              <button className="breadcrumb-link" onClick={item.onClick}>
                {item.label}
              </button>
            ) : (
              <span>{item.label}</span>
            )}
          </span>
        ))}
      </div>
    );
  };

  // ─── LEVEL SELECT ───
  if (step === 'level_select') {
    return (
      <div className="page">
        <div className="listening-linear">
          <LevelTabs selectedLevel={selectedLevel} onSelect={handleSelectLevel} variant="hero" />
          <div className="listening-history-section">
            <ExamHistoryPanel
              history={examHistory}
              onSelectRecord={handleViewHistoryRecord}
              loading={examHistoryLoading}
              visible={true}
            />
          </div>
        </div>
      </div>
    );
  }

  // ─── SET SELECT ───
  if (step === 'set_select') {
    return (
      <div className="page">
        <div className="listening-linear">
          {renderBreadcrumb()}
          <SetSelector
            sets={setList}
            loading={setListLoading}
            level={selectedLevel!}
            onStartPractice={handleStartPractice}
            onStartExam={handleStartExam}
          />
          <div className="listening-history-section">
            <ExamHistoryPanel
              history={examHistory}
              onSelectRecord={handleViewHistoryRecord}
              loading={examHistoryLoading}
              visible={true}
            />
          </div>
        </div>
      </div>
    );
  }

  // ─── SECTION SELECT ───
  if (step === 'section_select') {
    if (selectedSetLoading) {
      return (
        <div className="page">
          <div className="listening-linear">
            {renderBreadcrumb()}
            <div className="listening-empty">加载中...</div>
          </div>
        </div>
      );
    }
    if (!selectedSet) {
      return (
        <div className="page">
          <div className="listening-linear">
            {renderBreadcrumb()}
            <div className="listening-empty">加载失败</div>
          </div>
        </div>
      );
    }
    return (
      <div className="page">
        <div className="listening-linear">
          {renderBreadcrumb()}
          <SectionSelector
            sections={selectedSet.sections}
            setId={selectedSet.id}
            onSelect={handleSelectSection}
          />
        </div>
      </div>
    );
  }

  // ─── PRACTICE ───
  if (step === 'practice') {
    // Sentence analysis sub-view
    if (analysisSentence) {
      const s = analysisSentence;
      const sIdx = practiceSentences.findIndex((ps) => ps.id === s.id);
      return (
        <div className="page">
          <div className="listening-linear">
            <SentenceAnalysis
              sentence={s}
              showTranslation={showTranslations}
              isPlayingFull={isPlayingFull}
              isRecording={recordingTarget === s.id && recording.state.isRecording}
              recordingSeconds={recording.state.seconds}
              hasRecording={recordingTarget === s.id && recordingPlayback.hasRecording}
              isPlayingRecording={recordingTarget === s.id && recordingPlayback.isPlayingRecording}
              onPlay={() => handleSinglePlay(s.en, s.id)}
              onCollect={() => handleCollect(s.en)}
              onStartRecord={() => handleStartRecord(s.id)}
              onStopRecord={handleStopRecord}
              onPlayRecording={handlePlayRecording}
              onBack={handleCloseAnalysis}
            />
          </div>
        </div>
      );
    }

    return (
      <div className="page">
        <div className="listening-linear">
          {renderBreadcrumb()}
          <div className="listening-practice-top">
            <button className="listening-back-btn" onClick={goSectionSelect}>
              &larr; 返回段落选择
            </button>
          </div>
          <div className="listening-content" style={{ maxHeight: 'calc(100vh - 240px)' }}>
            <ListeningPlayer
              playState={seq.playState}
              currentIndex={seq.currentIndex}
              totalCount={seq.totalCount}
              showTranslations={showTranslations}
              hasSelectedSet={practiceSentences.length > 0}
              variant="practice"
              onPlay={handleFullPlay}
              onPause={seq.pause}
              onResume={seq.resume}
              onStop={seq.stop}
              onNext={seq.next}
              onPrev={seq.prev}
              onToggleTranslations={() => setShowTranslations((v) => !v)}
            />

            <div className="listening-sentence-list" ref={sentenceListRef}>
              {practiceSentences.length === 0 ? (
                <div className="listening-empty">暂无句子</div>
              ) : selectedSection?.items && selectedSection.items.length > 0 ? (
                selectedSection.items.map((item) => {
                  const itemQuestions = practiceQuestions.filter((q) => q.item_id === item.id);
                  return (
                    <div key={item.id} className="listening-item-group">
                      <div className="listening-item-name">{item.name}</div>
                      {item.sentences.map((s) => (
                        <SentenceItem
                          key={s.id}
                          sentence={s}
                          isActive={seq.currentIndex >= 0 && practiceSentences[seq.currentIndex]?.id === s.id}
                          showTranslation={showTranslations}
                          isPlayingFull={isPlayingFull}
                          isRecording={recordingTarget === s.id && recording.state.isRecording}
                          recordingSeconds={recording.state.seconds}
                          hasRecording={recordingTarget === s.id && recordingPlayback.hasRecording}
                          isPlayingRecording={recordingTarget === s.id && recordingPlayback.isPlayingRecording}
                          onPlay={() => handleSinglePlay(s.en, s.id)}
                          onCollect={() => handleCollect(s.en)}
                          onStartRecord={() => handleStartRecord(s.id)}
                          onStopRecord={handleStopRecord}
                          onPlayRecording={handlePlayRecording}
                          onAnalyze={() => handleAnalyzeSentence(s)}
                        />
                      ))}
                      {itemQuestions.length > 0 && (
                        <div className="listening-item-questions">
                          {itemQuestions.map((q) => (
                            <QuestionCard
                              key={q.id}
                              question={q}
                              selectedOption=""
                              disabled={true}
                              showResult={false}
                              practiceMode={true}
                              isPlayingFull={isPlayingFull}
                              isRecording={recordingTarget === q.id && recording.state.isRecording}
                              recordingSeconds={recording.state.seconds}
                              hasRecording={recordingTarget === q.id && recordingPlayback.hasRecording}
                              isPlayingRecording={recordingTarget === q.id && recordingPlayback.isPlayingRecording}
                              onPlay={() => handleSinglePlay(q.question_text, q.id)}
                              onCollect={() => handleCollect(q.question_text)}
                              onStartRecord={() => handleStartRecord(q.id)}
                              onStopRecord={handleStopRecord}
                              onPlayRecording={handlePlayRecording}
                              onSelect={() => {}}
                            />
                          ))}
                        </div>
                      )}
                    </div>
                  );
                })
              ) : (
                practiceSentences.map((s) => (
                  <SentenceItem
                    key={s.id}
                    sentence={s}
                    isActive={seq.currentIndex >= 0 && practiceSentences[seq.currentIndex]?.id === s.id}
                    showTranslation={showTranslations}
                    isPlayingFull={isPlayingFull}
                    isRecording={recordingTarget === s.id && recording.state.isRecording}
                    recordingSeconds={recording.state.seconds}
                    hasRecording={recordingTarget === s.id && recordingPlayback.hasRecording}
                    isPlayingRecording={recordingTarget === s.id && recordingPlayback.isPlayingRecording}
                    onPlay={() => handleSinglePlay(s.en, s.id)}
                    onCollect={() => handleCollect(s.en)}
                    onStartRecord={() => handleStartRecord(s.id)}
                    onStopRecord={handleStopRecord}
                    onPlayRecording={handlePlayRecording}
                    onAnalyze={() => handleAnalyzeSentence(s)}
                  />
                )))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  // ─── EXAM ───
  if (step === 'exam') {
    return (
      <div className="page">
        <div className="listening-linear">
          {renderBreadcrumb()}
          <MockExamPlayer
            set={selectedSet!}
            questions={examQuestions}
            onFinish={handleExamFinish}
            onExit={goSetSelect}
          />
        </div>
      </div>
    );
  }

  // ─── EXAM RESULT ───
  if (step === 'exam_result' && currentExamResult) {
    return (
      <div className="page">
        <div className="listening-linear">
          {renderBreadcrumb()}
          <div className="listening-content" style={{ maxWidth: 900, maxHeight: 'calc(100vh - 200px)' }}>
            <ExamResultView
              result={currentExamResult}
              setTitle={selectedSet?.name ?? currentExamResult.set_name ?? ''}
              onBack={goSetSelect}
            />
          </div>
        </div>
      </div>
    );
  }

  return null;
}
