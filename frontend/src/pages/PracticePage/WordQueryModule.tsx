import { useState, useCallback } from 'react';
import type { WordData, ToastType } from '../../types';
import { queryWord } from '../../services/api';
import { useWordNotes } from '../../hooks/useWordNotes';
import { SpeakerButton } from '../../components/SpeakerButton';

interface Props {
  onSpeak: (text: string) => void;
  onToast: (message: string, type?: ToastType) => void;
}

interface MeaningItemProps {
  meaning: { part_of_speech: string; definition: string; example: string };
  onSpeak: (text: string) => void;
  index: number;
}

function MeaningItem({ meaning, onSpeak, index }: MeaningItemProps) {
  const parts = meaning.example ? meaning.example.split('|') : ['', ''];

  return (
    <div className="meaning-item">
      <div className="part-of-speech">
        {index + 1}. {meaning.part_of_speech}
      </div>
      <div className="definition">释义：{meaning.definition}</div>
      {parts[0] && (
        <div className="example-container">
          <div className="example-en">
            例句：{parts[0]}
            <SpeakerButton onClick={() => onSpeak(parts[0])} size={13} />
          </div>
          {parts[1] && <div className="example-zh">翻译：{parts[1]}</div>}
        </div>
      )}
    </div>
  );
}

export function WordQueryModule({ onSpeak, onToast }: Props) {
  const [wordInput, setWordInput] = useState('');
  const [result, setResult] = useState<WordData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const { addWord } = useWordNotes();

  const handleSearch = useCallback(async () => {
    const word = wordInput.trim().toLowerCase();
    if (!word) {
      setError('请输入英文单词');
      return;
    }
    setLoading(true);
    setError('');
    setResult(null);
    try {
      const data = await queryWord(word);
      if ('error' in data) {
        setError(data.error);
      } else {
        setResult(data);
      }
    } catch {
      setError('查询失败，请检查后端服务');
    } finally {
      setLoading(false);
    }
  }, [wordInput]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') handleSearch();
  };

  const handleAddToNotes = () => {
    if (!result) return;
    const status = addWord(result);
    if (status === 'exists') {
      onToast('该单词已在笔记中！', 'info');
    } else {
      onToast('单词已保存到浏览器本地！', 'success');
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', flex: 1, minHeight: 0 }}>
      <div className="word-input-area">
        <input
          type="text"
          value={wordInput}
          onChange={(e) => setWordInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="输入英文单词"
        />
        <button
          onClick={handleSearch}
          disabled={loading}
          style={{
            padding: '10px 18px',
            background: 'var(--accent-cool)',
            color: '#fff',
            fontSize: 13,
            fontFamily: 'var(--font-mono)',
            letterSpacing: '0.04em',
          }}
        >
          查询
        </button>
      </div>

      <div className="word-result">
        {loading && (
          <p style={{ textAlign: 'center', color: 'var(--ink-muted)' }}>AI查询中...</p>
        )}
        {error && (
          <p style={{ color: 'var(--accent)', textAlign: 'center' }}>{error}</p>
        )}
        {result && (
          <>
            <h3 className="word-title">{result.word}</h3>
            <div
              className="word-phonetic"
              onClick={() => onSpeak(result.word)}
            >
              <SpeakerButton onClick={() => onSpeak(result.word)} size={15} />
              {result.phonetic}
            </div>
            <button className="add-word-btn" onClick={handleAddToNotes}>
              加入单词笔记
            </button>
            {result.meanings.length > 0 && (
              <div className="word-meanings">
                <h4>释义与例句</h4>
                {result.meanings.map((m, i) => (
                  <MeaningItem key={i} meaning={m} onSpeak={onSpeak} index={i} />
                ))}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
