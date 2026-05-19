import { useState, useCallback, useRef } from 'react';
import { listeningSets } from '../../data/listeningData';
import { useSequentialTTS } from '../../hooks/useSequentialTTS';
import { useSpeechSynthesis } from '../../hooks/useSpeechSynthesis';
import { useRecording } from '../../hooks/useRecording';
import { useRecordingPlayback } from '../../hooks/useRecordingPlayback';
import { useSentenceCollection } from '../../hooks/useSentenceCollection';
import { useToast } from '../../components/Toast/toastContext';
import { SetSelector } from './SetSelector';
import { ListeningPlayer } from './ListeningPlayer';
import { SentenceItem } from './SentenceItem';
import type { ListeningSet } from '../../types';

export function ListeningPage() {
  const [selectedSet, setSelectedSet] = useState<ListeningSet | null>(null);
  const [showTranslations, setShowTranslations] = useState(true);
  const [recordingTarget, setRecordingTarget] = useState<string | null>(null);

  const seq = useSequentialTTS(1.0);
  const speak = useSpeechSynthesis(1.0);
  const { addSentence } = useSentenceCollection();
  const { showToast } = useToast();
  const recordingPlayback = useRecordingPlayback();
  const recording = useRecording(recordingPlayback.storeRecording);

  const isPlayingFull = seq.playState === 'playing' || seq.playState === 'paused';

  const handleSelectSet = useCallback((set: ListeningSet) => {
    seq.stop();
    setSelectedSet(set);
  }, [seq]);

  const handleFullPlay = useCallback(() => {
    if (!selectedSet) return;
    const texts = selectedSet.sentences.map((s) => s.en);
    seq.play(texts, 0);
  }, [selectedSet, seq]);

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
          sets={listeningSets}
          selectedId={selectedSet?.id ?? null}
          onSelect={handleSelectSet}
        />
        <div className="listening-content">
          {selectedSet ? (
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
                {selectedSet.sentences.map((s) => (
                  <SentenceItem
                    key={s.id}
                    sentence={s}
                    isActive={seq.currentIndex >= 0 && selectedSet.sentences[seq.currentIndex]?.id === s.id}
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
