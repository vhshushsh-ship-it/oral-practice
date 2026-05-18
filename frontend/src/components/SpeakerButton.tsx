import { SpeakerIcon } from '../icons';

interface Props {
  onClick: () => void;
  size?: number;
  className?: string;
}

export function SpeakerButton({ onClick, size = 14, className = '' }: Props) {
  return (
    <span
      className={`speak-btn ${className}`}
      onClick={(e) => {
        e.stopPropagation();
        onClick();
      }}
    >
      <SpeakerIcon size={size} />
    </span>
  );
}

export function SpeakerButtonText({ text, onClick }: { text: string; onClick: (text: string) => void }) {
  return (
    <button className="speak-btn-text" onClick={() => onClick(text)}>
      <SpeakerIcon size={13} />
      Play
    </button>
  );
}
