import { useRef, useLayoutEffect, useCallback } from 'react';
import type { DialogueScene } from '../../types';
import { SpeakerButton } from '../../components/SpeakerButton';
import { CollectButton } from '../../components/CollectButton';
import { StudyIcon } from '../../icons';

interface Props {
  scene: DialogueScene | null;
  savedScrollTop: number;
  onScrollSave: (scrollTop: number) => void;
  onSpeak: (text: string) => void;
  onCollect: (text: string) => void;
  onAnalyze: (en: string, zh: string) => void;
}

export function DialogueContent({ scene, savedScrollTop, onScrollSave, onSpeak, onCollect, onAnalyze }: Props) {
  const contentRef = useRef<HTMLDivElement>(null);

  // Restore scroll position when scene changes (before paint to avoid flash)
  useLayoutEffect(() => {
    if (contentRef.current) {
      contentRef.current.scrollTop = savedScrollTop;
    }
  }, [scene?.id]);

  const handleScroll = useCallback(() => {
    if (contentRef.current) {
      onScrollSave(contentRef.current.scrollTop);
    }
  }, [onScrollSave]);
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
      <div className="dialogue-content" ref={contentRef} onScroll={handleScroll}>
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
              <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                <button
                  className="sentence-action-btn analyze"
                  onClick={(e) => { e.stopPropagation(); onAnalyze(turn.en, turn.zh); }}
                  title="分析发音"
                >
                  <StudyIcon size={13} />
                </button>
                <CollectButton text={turn.en} onCollect={onCollect} />
              </div>
            </div>
            <div className="dialogue-zh">{turn.zh}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
