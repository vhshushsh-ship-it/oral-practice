import type { WordNote, SortType } from '../../types';
import { SpeakerButton } from '../../components/SpeakerButton';
import { WordDetail } from './WordDetail';

interface Props {
  notes: WordNote[];
  selectedWord: WordNote | null;
  sortType: SortType;
  onSortChange: (type: SortType) => void;
  searchKeyword: string;
  onSearchChange: (kw: string) => void;
  onSelectWord: (word: WordNote) => void;
  onDeleteWord: (word: string) => void;
  onSpeak: (text: string) => void;
  onBack: () => void;
}

export function NotesDetail({
  notes,
  selectedWord,
  sortType,
  onSortChange,
  searchKeyword,
  onSearchChange,
  onSelectWord,
  onDeleteWord,
  onSpeak,
  onBack,
}: Props) {
  return (
    <div className="detail-layout">
      {/* Left: word list */}
      <div className="detail-left-panel">
        <div className="detail-header" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <button className="back-btn" onClick={onBack}>
            ← 返回全屏
          </button>
        </div>
        <div className="sort-area">
          <label className="sort-label">
            <input
              type="radio"
              name="detailSortType"
              value="time"
              checked={sortType === 'time'}
              onChange={() => onSortChange('time')}
            />
            时间
          </label>
          <label className="sort-label">
            <input
              type="radio"
              name="detailSortType"
              value="alphabet"
              checked={sortType === 'alphabet'}
              onChange={() => onSortChange('alphabet')}
            />
            字母
          </label>
          <input
            type="text"
            placeholder="搜索..."
            value={searchKeyword}
            onChange={(e) => onSearchChange(e.target.value)}
            style={{ maxWidth: 140, padding: '6px 10px', fontSize: 12 }}
          />
        </div>
        <div className="word-notes-list">
          {notes.length === 0 ? (
            <p style={{ textAlign: 'center', color: 'var(--ink-muted)', padding: 20 }}>
              暂无单词笔记
            </p>
          ) : (
            notes.map((item) => (
              <div
                key={item.word}
                className={`word-note-item${selectedWord?.word === item.word ? ' active' : ''}`}
                onClick={() => onSelectWord(item)}
              >
                <div className="word-info">
                  <div className="word-row" style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <span className="word">{item.word}</span>
                    <span className="phonetic" style={{ color: 'var(--ink-light)', fontSize: 12 }}>
                      {item.phonetic || ''}
                    </span>
                    <SpeakerButton onClick={() => onSpeak(item.word)} size={12} />
                  </div>
                  <div className="meaning">{item.meaning}</div>
                </div>
                <button
                  className="delete-word-btn"
                  onClick={(e) => {
                    e.stopPropagation();
                    onDeleteWord(item.word);
                  }}
                >
                  删除
                </button>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Right: word detail */}
      <div className="detail-right-panel">
        {selectedWord ? (
          <WordDetail word={selectedWord} onSpeak={onSpeak} onDelete={onDeleteWord} />
        ) : (
          <div className="empty-detail">
            <p>请点击左侧单词，查看完整详情</p>
          </div>
        )}
      </div>
    </div>
  );
}
