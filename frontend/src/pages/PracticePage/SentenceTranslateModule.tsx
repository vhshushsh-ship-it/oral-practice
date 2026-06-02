import { useState, useCallback } from 'react';
import { translateToEnglish } from '../../services/api';
import { useToast } from '../../components/Toast/toastContext';

interface Props {
  onSpeak: (text: string) => void;
}

export function SentenceTranslateModule({ onSpeak }: Props) {
  const [input, setInput] = useState('');
  const [result, setResult] = useState('');
  const [loading, setLoading] = useState(false);
  const [showCopy, setShowCopy] = useState(false);
  const { showToast } = useToast();

  // ---- Translate handlers ----
  const handleTranslate = useCallback(async () => {
    const text = input.trim();
    if (!text) {
      showToast('请输入中文句子', 'warning');
      return;
    }
    setLoading(true);
    setResult('翻译中...');
    setShowCopy(false);
    try {
      const translation = await translateToEnglish(text);
      setResult(translation);
      setShowCopy(true);
    } catch {
      setResult('翻译失败，请检查网络连接');
    } finally {
      setLoading(false);
    }
  }, [input, showToast]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') handleTranslate();
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(result).then(
      () => showToast('已复制到剪贴板！', 'success'),
      () => showToast('复制失败，请手动复制', 'warning'),
    );
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', flex: 1, minHeight: 0 }}>
      <div className="translate-input-area" style={{ display: 'flex', gap: 10, marginBottom: 15, flexShrink: 0 }}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="输入中文句子"
          style={{ flex: 1 }}
        />
        <button
          onClick={handleTranslate}
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
          翻译
        </button>
      </div>
      <div className="translate-result-area" style={{ flex: 1, overflowY: 'auto', minHeight: 80, background: 'var(--paper-light)', borderRadius: 3, padding: 15, border: '1px solid var(--line-light)' }}>
        <p style={{ margin: 0, color: 'var(--ink)', lineHeight: 1.6 }}>{result || '翻译结果将在这里显示'}</p>
        {showCopy && (
          <button
            onClick={handleCopy}
            style={{
              marginTop: 10,
              padding: '6px 12px',
              background: 'var(--accent-cool)',
              color: '#fff',
              fontSize: 11,
              fontFamily: 'var(--font-mono)',
            }}
          >
            复制译文
          </button>
        )}
      </div>
    </div>
  );
}
