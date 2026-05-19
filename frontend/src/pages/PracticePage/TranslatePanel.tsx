import { useEffect, useRef } from 'react';
import type { Translation } from '../../types';
import { SpeakerButton } from '../../components/SpeakerButton';

interface Props {
  translations: Translation[];
  onSpeak: (text: string) => void;
}

export function TranslatePanel({ translations, onSpeak }: Props) {
  const boxRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (boxRef.current) {
      boxRef.current.scrollTop = boxRef.current.scrollHeight;
    }
  }, [translations]);

  if (translations.length === 0) {
    return (
      <div className="translate-box" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--ink-muted)' }}>
        翻译内容将在这里显示
      </div>
    );
  }

  return (
    <div className="translate-box" ref={boxRef}>
      {translations.map((t, i) => (
        <div key={i} className="translate-item">
          <div className="source">
            {t.isUser ? 'You: ' : 'AI: '}
            {t.source}
            <SpeakerButton onClick={() => onSpeak(t.source)} size={12} />
          </div>
          <div className="target">{t.target}</div>
        </div>
      ))}
    </div>
  );
}
