import type { ListeningSet } from '../../types';

interface Props {
  sets: ListeningSet[];
  selectedId: string | null;
  onSelect: (set: ListeningSet) => void;
}

export function SetSelector({ sets, selectedId, onSelect }: Props) {
  return (
    <div className="listening-set-list">
      <h3>真题集列表</h3>
      <div className="listening-set-list-wrapper">
        {sets.map((set) => (
          <div
            key={set.id}
            className={`listening-set-item${selectedId === set.id ? ' active' : ''}`}
            onClick={() => onSelect(set)}
          >
            <div className="listening-set-name">{set.name}</div>
            <span className={`listening-set-badge ${set.type}`}>
              {set.type.toUpperCase()}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
