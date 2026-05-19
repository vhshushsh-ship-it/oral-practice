import type { WordNote } from '../../types';
import { SpeakerButton } from '../../components/SpeakerButton';

interface Props {
  word: WordNote;
  onSpeak: (text: string) => void;
  onDelete: (word: string) => void;
}

export function WordDetail({ word, onSpeak, onDelete }: Props) {
  const { word: w, phonetic, meanings } = word;

  return (
    <div className="detail-content">
      <div className="detail-word-title">{w}</div>
      <div
        className="detail-word-phonetic"
        onClick={() => onSpeak(w)}
      >
        <SpeakerButton onClick={() => onSpeak(w)} size={15} />
        {phonetic}
      </div>
      <h4 className="detail-meanings-title">全词性释义与例句</h4>
      {meanings && meanings.length > 0 ? (
        meanings.map((m, i) => {
          const parts = m.example ? m.example.split('|') : ['', ''];
          return (
            <div className="detail-meaning-item" key={i}>
              <div className="part-of-speech">
                {i + 1}. {m.part_of_speech}
              </div>
              <div className="definition">{m.definition}</div>
              {parts[0] && (
                <div className="detail-example-container">
                  <div className="example-en">
                    例句：{parts[0]}
                    <SpeakerButton onClick={() => onSpeak(parts[0])} size={13} />
                  </div>
                  {parts[1] && (
                    <div className="example-zh">翻译：{parts[1]}</div>
                  )}
                </div>
              )}
            </div>
          );
        })
      ) : (
        <p style={{ color: 'var(--ink-muted)', textAlign: 'center', padding: 20 }}>
          暂无释义
        </p>
      )}
      <div style={{ marginTop: 24 }}>
        <button className="delete-word-btn" onClick={() => onDelete(w)}>
          删除此单词
        </button>
      </div>
    </div>
  );
}
