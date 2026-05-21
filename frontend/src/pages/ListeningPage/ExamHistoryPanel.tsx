import type { ExamHistoryItem } from '../../types';

interface Props {
  history: ExamHistoryItem[];
  onSelectRecord: (record: ExamHistoryItem) => void;
  loading: boolean;
  visible: boolean;
}

export function ExamHistoryPanel({ history, onSelectRecord, loading, visible }: Props) {
  if (!visible) return null;

  return (
    <div className="exam-history">
      <div className="exam-history-title">模考记录</div>
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
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
