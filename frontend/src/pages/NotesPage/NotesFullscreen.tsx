import type { WordNote, SortType } from '../../types';
import { SpeakerButton } from '../../components/SpeakerButton';

interface Props {
  notes: WordNote[];
  sortType: SortType;
  onSortChange: (type: SortType) => void;
  searchKeyword: string;
  onSearchChange: (kw: string) => void;
  isReciteMode: boolean;
  onToggleRecite: () => void;
  onSelectWord: (word: WordNote) => void;
  onDeleteWord: (word: string) => void;
  onSpeak: (text: string) => void;
  onClearAll: () => void;
}

export function NotesFullscreen({
  notes,
  sortType,
  onSortChange,
  searchKeyword,
  onSearchChange,
  isReciteMode,
  onToggleRecite,
  onSelectWord,
  onDeleteWord,
  onSpeak,
  onClearAll,
}: Props) {
  return (
    <div className="page" style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <h1>单词笔记</h1>
      <div className="sort-area">
        <label className="sort-label">
          <input
            type="radio"
            name="sortType"
            value="time"
            checked={sortType === 'time'}
            onChange={() => onSortChange('time')}
          />
          按时间排序
        </label>
        <label className="sort-label">
          <input
            type="radio"
            name="sortType"
            value="alphabet"
            checked={sortType === 'alphabet'}
            onChange={() => onSortChange('alphabet')}
          />
          按字母排序
        </label>
        <input
          type="text"
          placeholder="搜索单词..."
          value={searchKeyword}
          onChange={(e) => onSearchChange(e.target.value)}
          style={{ maxWidth: 200 }}
        />
        <button
          onClick={onToggleRecite}
          className="toggle-btn"
          style={{
            background: isReciteMode ? 'var(--accent)' : 'var(--paper-light)',
            color: isReciteMode ? '#fff' : 'var(--ink)',
            borderColor: isReciteMode ? 'var(--accent)' : 'var(--line)',
            flex: 'none',
            padding: '8px 16px',
          }}
        >
          {isReciteMode ? '退出背诵模式' : '隐藏释义背诵模式'}
        </button>
      </div>

      <div className={`word-notes-list${isReciteMode ? ' recite-mode' : ''}`}>
        {notes.length === 0 ? (
          <p style={{ textAlign: 'center', color: 'var(--ink-muted)', padding: 20 }}>
            还没有单词笔记，快去查询单词并添加吧
          </p>
        ) : (
          notes.map((item) => (
            <div
              key={item.word}
              className="word-note-item"
              onClick={() => onSelectWord(item)}
            >
              <div className="word-info">
                <div className="word-row" style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <span className="word">{item.word}</span>
                  <span className="phonetic" style={{ color: 'var(--ink-light)', fontSize: 13 }}>
                    {item.phonetic || ''}
                  </span>
                  <SpeakerButton onClick={() => onSpeak(item.word)} size={13} />
                </div>
                <div className="meaning" onClick={(e) => { if (isReciteMode) { e.stopPropagation(); (e.target as HTMLElement).style.display = 'none'; } }}>
                  {item.meaning}
                </div>
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

      {notes.length > 0 && (
        <div className="notes-actions">
          <button className="clear-btn" onClick={onClearAll}>
            清空所有笔记
          </button>
        </div>
      )}
    </div>
  );
}
