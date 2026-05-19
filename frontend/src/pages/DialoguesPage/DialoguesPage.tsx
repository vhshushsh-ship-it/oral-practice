import { useRef } from 'react';
import { useSceneDialogues } from '../../hooks/useSceneDialogues';
import { useSpeechSynthesis } from '../../hooks/useSpeechSynthesis';
import { useSentenceCollection } from '../../hooks/useSentenceCollection';
import { useToast } from '../../components/Toast/toastContext';
import { DialogueSceneList } from './DialogueSceneList';
import { DialogueContent } from './DialogueContent';
import type { DialogueScene } from '../../types';

export function DialoguesPage() {
  const { dialogues, selectedScene, setSelectedScene } = useSceneDialogues();
  const speak = useSpeechSynthesis(1.0);
  const { addSentence } = useSentenceCollection();
  const { showToast } = useToast();
  const contentRef = useRef<HTMLDivElement>(null);

  const handleSelectScene = (scene: DialogueScene) => {
    setSelectedScene(scene, contentRef.current);
  };

  const handleCollect = async (text: string) => {
    const result = await addSentence(text);
    if (result === 'exists') {
      showToast('该句子已收藏！', 'info');
    } else {
      showToast('句子收藏成功！', 'success');
    }
  };

  return (
    <div className="page" style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <h1>情景对话范本</h1>
      <div className="dialogues-container">
        <DialogueSceneList
          dialogues={dialogues}
          selectedScene={selectedScene}
          onSelectScene={handleSelectScene}
        />
        <div ref={contentRef} style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
          <DialogueContent
            scene={selectedScene}
            onSpeak={speak}
            onCollect={handleCollect}
          />
        </div>
      </div>
    </div>
  );
}
