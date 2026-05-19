import { useSentenceCollection } from '../../hooks/useSentenceCollection';
import { useSpeechSynthesis } from '../../hooks/useSpeechSynthesis';
import { SpeakerButton } from '../../components/SpeakerButton';
import { useToast } from '../../components/Toast/toastContext';

export function SentencesPage() {
  const { collection, deleteSentence, clearAll } = useSentenceCollection();
  const speak = useSpeechSynthesis(1.0);
  const { showToast } = useToast();

  const handleDelete = (index: number) => {
    deleteSentence(index);
    showToast('删除成功！', 'success');
  };

  const handleClearAll = () => {
    if (!window.confirm('确定要清空所有句子收藏吗？')) return;
    clearAll();
    showToast('已清空所有收藏！', 'success');
  };

  return (
    <div className="page" style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <h1>句子收藏</h1>
      <div className="content-centered" style={{ flex: 1, overflowY: 'auto' }}>
        {collection.length === 0 ? (
          <p style={{ textAlign: 'center', color: 'var(--ink-muted)', padding: 40 }}>
            还没有收藏任何句子，快去聊天或情景对话中收藏吧
          </p>
        ) : (
          collection.map((item, index) => (
            <div
              key={index}
              style={{
                padding: '12px 15px',
                borderBottom: '1px dashed var(--line-light)',
              }}
            >
              <div
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  marginBottom: 8,
                }}
              >
                <span style={{ flex: 1, color: 'var(--ink)', lineHeight: 1.5 }}>
                  {item.text}
                </span>
                <div style={{ display: 'flex', gap: 8, marginLeft: 10, flexShrink: 0 }}>
                  <button
                    className="speak-btn-text"
                    onClick={() => speak(item.text)}
                  >
                    <SpeakerButton onClick={() => speak(item.text)} size={11} />
                    Play
                  </button>
                  <button
                    onClick={() => handleDelete(index)}
                    style={{
                      padding: '5px 10px',
                      background: 'var(--accent)',
                      color: '#fff',
                      borderRadius: 2,
                      fontFamily: 'var(--font-mono)',
                      fontSize: 11,
                    }}
                  >
                    Del
                  </button>
                </div>
              </div>
              <div
                style={{
                  color: 'var(--ink-light)',
                  fontSize: 13,
                  lineHeight: 1.4,
                  paddingLeft: 4,
                }}
              >
                {item.translation || '翻译加载中...'}
              </div>
            </div>
          ))
        )}
      </div>
      {collection.length > 0 && (
        <div className="notes-actions">
          <button className="clear-btn" onClick={handleClearAll}>
            清空所有收藏
          </button>
        </div>
      )}
    </div>
  );
}
