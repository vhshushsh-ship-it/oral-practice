import { useState, useRef, useCallback } from 'react';
import { useSceneDialogues } from '../../hooks/useSceneDialogues';
import { useSpeechSynthesis } from '../../hooks/useSpeechSynthesis';
import { useSequentialTTS } from '../../hooks/useSequentialTTS';
import { useSentenceCollection } from '../../hooks/useSentenceCollection';
import { useToast } from '../../components/Toast/toastContext';
import { SentenceAnalysis } from '../../components/SentenceAnalysis';
import { GlobalAudioBar } from '../../components/GlobalAudioBar';
import { DialogueSceneList } from './DialogueSceneList';
import { DialogueContent } from './DialogueContent';
import type { DialogueScene } from '../../types';

export function DialoguesPage() {
  const { dialogues, selectedScene, setSelectedScene } = useSceneDialogues();
  const speak = useSpeechSynthesis(1.0);
  const sequentialTTS = useSequentialTTS(1.0);
  const { addSentence } = useSentenceCollection();
  const { showToast } = useToast();
  const [analyzingTurn, setAnalyzingTurn] = useState<{ en: string; zh: string } | null>(null);

  const scrollPositions = useRef<Record<string, number>>({});
  const currentSceneId = useRef<string | null>(null);

  const handleSelectScene = (scene: DialogueScene) => {
    // 场景切换：清空旧播放列表，重置播放下标
    sequentialTTS.stop();
    setSelectedScene(scene);
  };

  // 全局播放全部对话
  const handlePlayAll = useCallback(() => {
    if (!selectedScene) return;
    const texts = selectedScene.turns.map((t) => t.en);
    if (texts.length === 0) return;
    sequentialTTS.play(texts, Math.max(0, sequentialTTS.currentIndex));
  }, [selectedScene, sequentialTTS]);

  // 单句播放时先停止全局播放器，避免音频重叠
  const handleIndividualSpeak = useCallback(
    (text: string) => {
      sequentialTTS.stop();
      speak(text);
    },
    [sequentialTTS, speak],
  );

  const handleSaveScroll = useCallback((scrollTop: number) => {
    const sceneId = currentSceneId.current;
    if (sceneId) {
      scrollPositions.current[sceneId] = scrollTop;
    }
  }, []);

  const handleCollect = async (text: string) => {
    const result = await addSentence(text);
    if (result === 'exists') {
      showToast('该句子已收藏！', 'info');
    } else {
      showToast('句子收藏成功！', 'success');
    }
  };

  const handleAnalyze = (en: string, zh: string) => {
    setAnalyzingTurn({ en, zh });
  };

  const handleCloseAnalysis = () => {
    setAnalyzingTurn(null);
  };

  // Keep currentSceneId in sync for the scroll save callback
  currentSceneId.current = selectedScene?.id ?? null;

  // Sentence analysis sub-view
  if (analyzingTurn) {
    return (
      <div className="page">
        <SentenceAnalysis
          en={analyzingTurn.en}
          zh={analyzingTurn.zh}
          onPlay={() => handleIndividualSpeak(analyzingTurn.en)}
          onCollect={() => handleCollect(analyzingTurn.en)}
          onBack={handleCloseAnalysis}
        />
      </div>
    );
  }

  return (
    <div className="page" style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <h1>情景对话范本</h1>
      <div className="dialogues-container">
        <DialogueSceneList
          dialogues={dialogues}
          selectedScene={selectedScene}
          onSelectScene={handleSelectScene}
        />
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
          <DialogueContent
            scene={selectedScene}
            savedScrollTop={selectedScene ? scrollPositions.current[selectedScene.id] ?? 0 : 0}
            onScrollSave={handleSaveScroll}
            onSpeak={handleIndividualSpeak}
            onCollect={handleCollect}
            onAnalyze={handleAnalyze}
            playState={sequentialTTS.playState}
            currentIndex={sequentialTTS.currentIndex}
            totalCount={sequentialTTS.totalCount}
            onPlayAll={handlePlayAll}
            onPause={sequentialTTS.pause}
            onResume={sequentialTTS.resume}
            onStop={sequentialTTS.stop}
            onNext={sequentialTTS.next}
            onPrev={sequentialTTS.prev}
          />
        </div>
      </div>
    </div>
  );
}
