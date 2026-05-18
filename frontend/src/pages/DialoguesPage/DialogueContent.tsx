import type { DialogueScene } from '../../types';
import { SpeakerButton } from '../../components/SpeakerButton';
import { CollectButton } from '../../components/CollectButton';

interface Props {
  scene: DialogueScene | null;
  onSpeak: (text: string) => void;
  onCollect: (text: string) => void;
}

export function DialogueContent({ scene, onSpeak, onCollect }: Props) {
  if (!scene) {
    return (
      <div className="dialogue-display">
        <div style={{
          flex: 1,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: 'var(--ink-muted)',
        }}>
          请选择一个对话场景
        </div>
      </div>
    );
  }

  return (
    <div className="dialogue-display">
      <div className="dialogue-title">{scene.name}</div>
      <div className="dialogue-content">
        {scene.turns.map((turn, i) => (
          <div className="dialogue-turn" key={i}>
            <div className="dialogue-speaker">
              {turn.speaker}
              <button
                className="speak-btn-text"
                onClick={() => onSpeak(turn.en)}
              >
                <SpeakerButton onClick={() => onSpeak(turn.en)} size={11} />
                Play
              </button>
            </div>
            <div
              className="dialogue-en"
              onClick={() => onSpeak(turn.en)}
              style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}
            >
              <span>{turn.en}</span>
              <CollectButton text={turn.en} onCollect={onCollect} />
            </div>
            <div className="dialogue-zh">{turn.zh}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
