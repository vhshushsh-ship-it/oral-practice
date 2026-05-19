import { BookmarkIcon } from '../icons';

interface Props {
  text: string;
  onCollect: (text: string) => void;
}

export function CollectButton({ text, onCollect }: Props) {
  return (
    <span
      className="collect-btn"
      onClick={(e) => {
        e.stopPropagation();
        onCollect(text);
      }}
    >
      <BookmarkIcon size={14} />
    </span>
  );
}
