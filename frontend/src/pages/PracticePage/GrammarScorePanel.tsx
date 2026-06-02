import { useState } from 'react';
import type { GrammarCheckResult } from '../../types';
import { SpeakerIcon } from '../../icons';

interface RecordingState {
  isRecording: boolean;
  seconds: number;
}

interface GrammarRecordingAPI {
  state: RecordingState;
  start: () => Promise<void>;
  stop: () => void;
  cancel: () => void;
  formatTime: (s: number) => string;
}

interface Props {
  sourceText: string;
  result: GrammarCheckResult | null;
  loading: boolean;
  error: string;
  onFillInput: (text: string) => void;
  onSpeak: (text: string) => void;
  recording: GrammarRecordingAPI;
  onSendText: (text: string) => void;
}

function getScoreClass(score: number): string {
  if (score >= 80) return 'score-excellent';
  if (score >= 60) return 'score-good';
  return 'score-poor';
}

/** Render source_sent with error_index ranges highlighted in red */
function renderHighlightedSentence(text: string, errorIndex: [number, number][]) {
  if (!errorIndex || errorIndex.length === 0) {
    return <span>{text}</span>;
  }

  // Sort and deduplicate error ranges
  const sorted = [...errorIndex]
    .filter(([s, e]) => s >= 0 && e > s && s < text.length)
    .sort((a, b) => a[0] - b[0]);

  const parts: React.ReactNode[] = [];
  let cursor = 0;

  for (const [start, end] of sorted) {
    if (start < cursor) continue; // skip overlapping
    // Text before this error
    if (start > cursor) {
      parts.push(<span key={`txt-${cursor}`}>{text.slice(cursor, start)}</span>);
    }
    // Error fragment
    const errText = text.slice(start, Math.min(end, text.length));
    parts.push(
      <span key={`err-${start}`} className="grammar-error-highlight">
        {errText}
      </span>,
    );
    cursor = Math.min(end, text.length);
  }

  // Remaining text after last error
  if (cursor < text.length) {
    parts.push(<span key={`txt-${cursor}`}>{text.slice(cursor)}</span>);
  }

  return <>{parts}</>;
}

export function GrammarScorePanel({ sourceText, result, loading, error, onFillInput, onSpeak, recording, onSendText }: Props) {
  const [text, setText] = useState('');

  const handleSend = () => {
    if (text.trim()) {
      onSendText(text.trim());
      setText('');
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') handleSend();
  };

  const renderContent = () => {
    if (loading) {
      return <div className="grammar-loading">AI语法分析中...</div>;
    }

    if (error) {
      return <div className="grammar-loading" style={{ color: 'var(--accent)' }}>{error}</div>;
    }

    if (!result) {
      return (
        <div className="grammar-empty">
          输入英文句子后点击发送，或点击聊天消息左侧的
          <span style={{ fontFamily: 'var(--font-mono)', color: 'var(--accent-cool)' }}> 🔍 </span>
          按钮进行语法检测
        </div>
      );
    }

    const scoreClass = getScoreClass(result.score);
    const hasErrors = result.error_index && result.error_index.length > 0;

    return (
      <>
        {/* Section A: Score Header */}
        <div className="grammar-score-header">
          <div className="score-label">日常口语语法得分</div>
          <div className={`score-value ${scoreClass}`}>
            {result.score}<span style={{ fontSize: 18 }}>/100</span>
          </div>
        </div>

        {/* Section B: Error Annotation */}
        <div className="grammar-section">
          <div className="grammar-section-title">错误标注</div>
          <div
            className="grammar-compare-text"
            style={{
              padding: '10px 12px',
              background: 'var(--paper-light)',
              borderRadius: 3,
              border: '1px solid var(--line-light)',
              lineHeight: 1.8,
              marginBottom: 12,
            }}
          >
            {hasErrors
              ? renderHighlightedSentence(result.source_sent, result.error_index)
              : result.source_sent}
          </div>

          {hasErrors && (
            <ul className="grammar-error-list">
              {(result.error_info || []).map((info, i) => (
                <li key={i} className="grammar-error-item">
                  <span className="grammar-error-text">{info.error_text}</span>
                  <span className="grammar-error-type">{info.error_type}</span>
                  <div className="grammar-error-explain">{info.explain}</div>
                </li>
              ))}
            </ul>
          )}

          {!hasErrors && (
            <div style={{ padding: '10px 12px', color: 'var(--accent-cool)', fontSize: 13 }}>
              ✓ 未发现语法错误，表达地道！
            </div>
          )}
        </div>

        {/* Section C: Correction Comparison */}
        <div className="grammar-section">
          <div className="grammar-section-title">修正对比</div>
          <div className="grammar-compare-row">
            <div className="grammar-compare-col">
              <div className="grammar-compare-label">原文</div>
              <div className="grammar-compare-text">
                {hasErrors
                  ? renderHighlightedSentence(result.source_sent, result.error_index)
                  : result.source_sent}
              </div>
            </div>
            <div className="grammar-compare-col">
              <div className="grammar-compare-label">AI 优化</div>
              <div className="grammar-compare-text fixed">{result.fixed_sent}</div>
              <span
                onClick={(e) => { e.stopPropagation(); onSpeak(result.fixed_sent); }}
                style={{ cursor: 'pointer', display: 'inline-flex', marginTop: 6, color: 'var(--accent-cool)' }}
                title="朗读修正句"
              >
                <SpeakerIcon size={13} />
              </span>
            </div>
          </div>

          <button
            className="grammar-fill-btn"
            onClick={() => onFillInput(result.fixed_sent)}
          >
            填入输入框
          </button>
        </div>
      </>
    );
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', flex: 1, minHeight: 0 }}>
      {/* ---- Custom input area (matching InputArea style) ---- */}
      <div className="input-container" style={{ flexShrink: 0, marginBottom: 12 }}>
        {/* Voice input */}
        <div className="voice-input">
          <span>语音输入</span>

          {recording.state.isRecording && (
            <>
              <div className="waveform">
                <span className="wave-bar" />
                <span className="wave-bar" />
                <span className="wave-bar" />
                <span className="wave-bar" />
                <span className="wave-bar" />
              </div>
              <span style={{ color: 'var(--accent)', fontWeight: 'bold', margin: '0 8px', fontFamily: 'var(--font-mono)' }}>
                {recording.formatTime(recording.state.seconds)}
              </span>
            </>
          )}

          {!recording.state.isRecording ? (
            <button
              onClick={recording.start}
              style={{
                padding: '8px 18px',
                background: 'var(--accent)',
                color: '#fff',
                fontSize: 13,
                fontFamily: 'var(--font-mono)',
                letterSpacing: '0.04em',
              }}
            >
              开始录音
            </button>
          ) : (
            <>
              <button
                onClick={recording.stop}
                style={{
                  padding: '8px 18px',
                  background: 'var(--accent)',
                  color: '#fff',
                  fontSize: 13,
                  fontFamily: 'var(--font-mono)',
                  letterSpacing: '0.04em',
                }}
              >
                结束并发送
              </button>
              <button
                onClick={recording.cancel}
                style={{
                  padding: '8px 14px',
                  background: 'var(--ink-muted)',
                  color: '#fff',
                  fontSize: 13,
                  fontFamily: 'var(--font-mono)',
                  letterSpacing: '0.04em',
                }}
              >
                取消录音
              </button>
            </>
          )}
        </div>

        {/* Text input */}
        <div className="text-input">
          <span style={{ display: 'flex', alignItems: 'center', padding: '0 8px', fontSize: 13, color: 'var(--ink-light)', whiteSpace: 'nowrap' }}>
            键盘输入
          </span>
          <input
            type="text"
            value={text}
            onChange={(e) => setText(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={loading ? '检测中...' : '输入英文句子...'}
            disabled={loading}
            style={{ flex: 1 }}
          />
          <button
            onClick={handleSend}
            disabled={loading || !text.trim()}
            style={{
              padding: '10px 20px',
              background: 'var(--accent-cool)',
              color: '#fff',
              fontSize: 13,
              fontFamily: 'var(--font-mono)',
              letterSpacing: '0.04em',
              opacity: loading || !text.trim() ? 0.6 : 1,
            }}
          >
            发送
          </button>
        </div>
      </div>

      {/* ---- Result area ---- */}
      <div style={{ flex: 1, overflowY: 'auto', minHeight: 0 }}>
        {renderContent()}
      </div>
    </div>
  );
}
