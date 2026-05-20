import type { ListeningSetMeta } from '../../types';

interface Props {
  sets: ListeningSetMeta[];
  selectedId: string | null;
  onSelect: (set: ListeningSetMeta) => void;
  loading?: boolean;
  error?: string | null;
}

export function SetSelector({ sets, selectedId, onSelect, loading, error }: Props) {
  return (
    <div className="listening-set-list">
      <h3>真题集列表</h3>
      <div className="listening-set-list-wrapper">
        {loading ? (
          <div className="listening-set-item" style={{ justifyContent: 'center' }}>加载中...</div>
        ) : error ? (
          <div className="listening-set-item" style={{ justifyContent: 'center', color: 'var(--accent)' }}>加载失败</div>
        ) : (
          sets.map((set) => (
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
          ))
        )}
      </div>
    </div>
  );
}
