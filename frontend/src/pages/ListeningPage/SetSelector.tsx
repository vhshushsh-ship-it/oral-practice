import type { ListeningSetMeta, ListeningLevel } from '../../types';

interface Props {
  sets: ListeningSetMeta[];
  loading: boolean;
  level: ListeningLevel;
  onStartPractice: (set: ListeningSetMeta) => void;
  onStartExam: (set: ListeningSetMeta) => void;
}

function getProgress(setId: string): { played: number; total: number } | null {
  try {
    const raw = localStorage.getItem(`listening_progress_${setId}`);
    if (!raw) return null;
    const data = JSON.parse(raw);
    return { played: data.played?.length ?? 0, total: data.total ?? 0 };
  } catch {
    return null;
  }
}

function getStatusLabel(progress: { played: number; total: number } | null): string {
  if (!progress || progress.played === 0) return '未开始';
  if (progress.played >= progress.total) return '已完成';
  return '进行中';
}

function getStatusClass(progress: { played: number; total: number } | null): string {
  if (!progress || progress.played === 0) return '';
  if (progress.played >= progress.total) return 'done';
  return 'active';
}

export function SetSelector({ sets, loading, level, onStartPractice, onStartExam }: Props) {
  const title = level === 'cet4' ? '四级真题列表' : '六级真题列表';

  if (loading) {
    return (
      <div className="set-grid-container">
        <h3 className="set-grid-title">{title}</h3>
        <div className="listening-empty">加载中...</div>
      </div>
    );
  }

  if (sets.length === 0) {
    return (
      <div className="set-grid-container">
        <h3 className="set-grid-title">{title}</h3>
        <div className="listening-empty">暂无真题</div>
      </div>
    );
  }

  return (
    <div className="set-grid-container">
      <h3 className="set-grid-title">{title}</h3>
      <div className="set-grid">
        {sets.map((set) => {
          const progress = getProgress(set.id);
          const statusLabel = getStatusLabel(progress);
          const statusClass = getStatusClass(progress);
          const hasQuestions = (set.question_count ?? 0) > 0;
          const pct = progress && progress.total > 0
            ? Math.round((progress.played / progress.total) * 100)
            : 0;

          return (
            <div key={set.id} className={`set-card ${statusClass}`}>
              <div className="set-card-body">
                <div className="set-card-header">
                  <h4 className="set-card-name">{set.name}</h4>
                  <span className={`set-card-status ${statusClass}`}>{statusLabel}</span>
                </div>
                <div className="set-card-stats">
                  <span>{set.sentence_count} 句</span>
                  {hasQuestions && <span>· {set.question_count} 题</span>}
                </div>
                {progress && progress.total > 0 && (
                  <div className="set-card-progress">
                    <div className="set-card-progress-bar">
                      <div
                        className="set-card-progress-fill"
                        style={{ width: `${pct}%` }}
                      />
                    </div>
                    <span className="set-card-progress-text">{pct}%</span>
                  </div>
                )}
              </div>
              <div className="set-card-actions">
                <button
                  className="set-card-btn practice"
                  onClick={() => onStartPractice(set)}
                >
                  分段精听
                </button>
                {hasQuestions && (
                  <button
                    className="set-card-btn exam"
                    onClick={() => onStartExam(set)}
                  >
                    全真模拟
                  </button>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
