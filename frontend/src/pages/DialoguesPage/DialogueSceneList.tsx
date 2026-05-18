import type { DialogueScene } from '../../types';

interface Props {
  dialogues: DialogueScene[];
  selectedScene: DialogueScene | null;
  onSelectScene: (scene: DialogueScene) => void;
}

export function DialogueSceneList({ dialogues, selectedScene, onSelectScene }: Props) {
  return (
    <div className="dialogue-scene-list">
      <h3>对话场景列表</h3>
      <div className="scene-list-wrapper">
        {dialogues.map((scene) => (
          <div
            key={scene.id}
            className={`scene-item${selectedScene?.id === scene.id ? ' active' : ''}`}
            onClick={() => onSelectScene(scene)}
          >
            {scene.name}
          </div>
        ))}
      </div>
    </div>
  );
}
