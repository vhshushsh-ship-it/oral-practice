import { useState, useCallback, useEffect, useMemo } from 'react';
import { useSequentialTTS } from '../../hooks/useSequentialTTS';
import { useSpeechSynthesis } from '../../hooks/useSpeechSynthesis';
import { useRecording } from '../../hooks/useRecording';
import { useRecordingPlayback } from '../../hooks/useRecordingPlayback';
import { useSentenceCollection } from '../../hooks/useSentenceCollection';
import { useToast } from '../../components/Toast/toastContext';
import { fetchListeningSets, fetchListeningSetDetail } from '../../services/api';
import { SetSelector } from './SetSelector';
import { ListeningPlayer } from './ListeningPlayer';
import { SentenceItem } from './SentenceItem';
import type { ListeningSet, ListeningSetMeta } from '../../types';

export function ListeningPage() {
  const [setList, setSetList] = useState<ListeningSetMeta[]>([]);
  const [setListLoading, setSetListLoading] = useState(true);
  const [setListError, setSetListError] = useState<string | null>(null);

  const [selectedSet, setSelectedSet] = useState<ListeningSet | null>(null);
  const [selectedSetLoading, setSelectedSetLoading] = useState(false);
  const [showTranslations, setShowTranslations] = useState(true);
  const [recordingTarget, setRecordingTarget] = useState<string | null>(null);

  const seq = useSequentialTTS(1.0);
  const speak = useSpeechSynthesis(1.0);
  const { addSentence } = useSentenceCollection();
  const { showToast } = useToast();
  const recordingPlayback = useRecordingPlayback();
  const recording = useRecording(recordingPlayback.storeRecording);

  const isPlayingFull = seq.playState === 'playing' || seq.playState === 'paused';

  // 展平所有 sections 中的句子
  const allSentences = useMemo(() => {
    if (!selectedSet) return [];
    return selectedSet.sections.flatMap((sec) => sec.sentences);
  }, [selectedSet]);

  // 组件挂载时加载套题列表
  useEffect(() => {
    fetchListeningSets()
      .then((sets) => { setSetList(sets); setSetListLoading(false); })
      .catch((err) => { setSetListError(err.message); setSetListLoading(false); });
  }, []);

  const handleSelectSet = useCallback(async (meta: ListeningSetMeta) => {
    seq.stop();
    setSelectedSetLoading(true);
    setSelectedSet(null);
    try {
      const detail = await fetchListeningSetDetail(meta.id);
      setSelectedSet(detail);
    } catch (err: any) {
      showToast('加载真题失败，请重试', 'warning');
    } finally {
      setSelectedSetLoading(false);
    }
  }, [seq, showToast]);

  const handleFullPlay = useCallback(() => {
    if (allSentences.length === 0) return;
    const texts = allSentences.map((s) => s.en);
    seq.play(texts, 0);
  }, [allSentences, seq]);

  const handleSinglePlay = useCallback((text: string) => {
    speak(text);
  }, [speak]);

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

  return (
    <div className="page" style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <h1>四六级听力练习</h1>
      <div className="listening-layout">
        <SetSelector
          sets={setList}
          selectedId={selectedSet?.id ?? null}
          onSelect={handleSelectSet}
          loading={setListLoading}
          error={setListError}
        />
        <div className="listening-content">
          {selectedSetLoading ? (
            <div className="listening-empty">加载真题中...</div>
          ) : selectedSet ? (
            <>
              <ListeningPlayer
                playState={seq.playState}
                currentIndex={seq.currentIndex}
                totalCount={seq.totalCount}
                showTranslations={showTranslations}
                hasSelectedSet
                onPlay={handleFullPlay}
                onPause={seq.pause}
                onResume={seq.resume}
                onStop={seq.stop}
                onNext={seq.next}
                onPrev={seq.prev}
                onToggleTranslations={() => setShowTranslations((v) => !v)}
              />
              <div className="listening-sentence-list">
                {selectedSet.sections.map((sec) => (
                  <div key={sec.id ?? 'ungrouped'} className="listening-section-group">
                    {sec.sectionType !== 'none' && (
                      <h4 className="listening-section-title">{sec.name}</h4>
                    )}
                    {sec.sentences.map((s) => (
                      <SentenceItem
                        key={s.id}
                        sentence={s}
                        isActive={seq.currentIndex >= 0 && allSentences[seq.currentIndex]?.id === s.id}
                        showTranslation={showTranslations}
                        isPlayingFull={isPlayingFull}
                        isRecording={recordingTarget === s.id && recording.state.isRecording}
                        recordingSeconds={recording.state.seconds}
                        hasRecording={recordingTarget === s.id && recordingPlayback.hasRecording}
                        isPlayingRecording={recordingTarget === s.id && recordingPlayback.isPlayingRecording}
                        onPlay={() => handleSinglePlay(s.en)}
                        onCollect={() => handleCollect(s.en)}
                        onStartRecord={() => handleStartRecord(s.id)}
                        onStopRecord={handleStopRecord}
                        onPlayRecording={handlePlayRecording}
                      />
                    ))}
                  </div>
                ))}
              </div>
            </>
          ) : (
            <div className="listening-empty">
              请选择一个真题集开始练习
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
