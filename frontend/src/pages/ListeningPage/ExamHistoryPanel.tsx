import type { ExamHistoryItem } from '../../types';
import { TrashIcon } from '../../icons';

interface Props {
  history: ExamHistoryItem[];
  onSelectRecord: (record: ExamHistoryItem) => void;
  onDeleteRecord: (record: ExamHistoryItem) => void;
  onClearAll: () => void;
  loading: boolean;
  visible: boolean;
}

export function ExamHistoryPanel({ history, onSelectRecord, onDeleteRecord, onClearAll, loading, visible }: Props) {
  if (!visible) return null;

  const handleDelete = (e: React.MouseEvent, record: ExamHistoryItem) => {
    e.stopPropagation();
    if (!window.confirm('确定删除该条模考记录吗？删除后无法恢复')) return;
    onDeleteRecord(record);
  };

  const handleClearAll = () => {
    if (!window.confirm('确定清空所有模考记录吗？删除后无法恢复')) return;
    onClearAll();
  };

  return (
    <div className="exam-history">
      <div className="exam-history-title-row">
        <span className="exam-history-title">模考记录</span>
        {history.length > 0 && (
          <button className="exam-history-clear-btn" onClick={handleClearAll}>
            清空所有记录
          </button>
        )}
      </div>
      {loading ? (
        <div style={{ fontSize: 12, color: 'var(--ink-muted)', padding: '8px 0' }}>
          加载中...
        </div>
      ) : history.length === 0 ? (
        <div style={{ fontSize: 12, color: 'var(--ink-muted)', padding: '8px 0' }}>
          暂无模考记录
        </div>
      ) : (
        <div className="exam-history-list">
          {history.map((r) => (
            <div
              key={r.id}
              className="history-item"
              onClick={() => onSelectRecord(r)}
            >
              <span className="history-item-date">
                {r.createdAt ? new Date(r.createdAt).toLocaleString('zh-CN', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' }) : ''}
              </span>
              <span className="history-item-name">{r.set_name}</span>
              <span className={`history-item-score${r.accuracy >= 60 ? ' good' : ' fair'}`}>
                {r.accuracy}% ({r.correctCount}/{r.totalQuestions})
              </span>
              <button
                className="history-item-delete"
                onClick={(e) => handleDelete(e, r)}
                title="删除记录"
              >
                <TrashIcon size={12} />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
