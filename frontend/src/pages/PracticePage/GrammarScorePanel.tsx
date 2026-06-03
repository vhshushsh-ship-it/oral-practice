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

type ErrorBadge = 'spelling' | 'article' | 'word-order' | 'word-choice' | 'grammar';

function getErrorBadge(errorType: string): { type: ErrorBadge; label: string } {
  const t = errorType.toLowerCase();
  if (t.includes('拼写') || t.includes('spell')) {
    return { type: 'spelling', label: '拼写' };
  }
  if (t.includes('冠词') || t.includes('article')) {
    return { type: 'article', label: '冠词' };
  }
  if (t.includes('语序') || t.includes('order') || t.includes('词序')) {
    return { type: 'word-order', label: '语序' };
  }
  if (t.includes('用词') || t.includes('措辞') || t.includes('词汇') || t.includes('word choice')) {
    return { type: 'word-choice', label: '用词' };
  }
  return { type: 'grammar', label: '语法' };
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
      return (
        <p style={{ textAlign: 'center', color: 'var(--ink-muted)', fontFamily: 'var(--font-mono)', fontSize: 14, letterSpacing: '0.04em' }}>
          AI 语法分析中...
        </p>
      );
    }

    if (error) {
      return (
        <p style={{ color: 'var(--accent)', textAlign: 'center', fontFamily: 'var(--font-serif)' }}>{error}</p>
      );
    }

    if (!result) {
      return (
        <p className="grammar-empty-state">
          输入英文句子后点击发送，或点击聊天消息左侧的
          <span style={{ fontFamily: 'var(--font-mono)', color: 'var(--accent-cool)' }}> 🔍 </span>
          按钮进行语法检测
        </p>
      );
    }

    const scoreClass = getScoreClass(result.score);
    const hasErrors = result.error_index && result.error_index.length > 0;

    return (
      <>
        {/* ① Score — matching word title pattern */}
        <div className="grammar-section" style={{ textAlign: 'center' }}>
          <h4 className="grammar-section-heading">日常口语语法得分</h4>
          <div className="grammar-section-body grammar-score-body">
            <div className={`grammar-score-number ${scoreClass}`}>
              {result.score}<span className="grammar-score-unit">/100</span>
            </div>
            <div className="grammar-score-comment">
              {result.score >= 80 ? '表达地道，语法掌握优秀' : result.score >= 60 ? '基本正确，仍有提升空间' : '存在较多语法错误，建议加强练习'}
            </div>
          </div>
        </div>

        {/* ② Error Annotation — matching word meanings pattern */}
        <div className="grammar-section">
          <h4 className="grammar-section-heading">错误标注</h4>
          {hasErrors ? (
            <div className="grammar-section-body" style={{ padding: 0, background: 'none', borderLeft: 'none', boxShadow: 'none' }}>
              <div className="grammar-sentence-display">
                {renderHighlightedSentence(result.source_sent, result.error_index)}
              </div>
              <ul className="grammar-error-list">
                {(result.error_info || []).map((info, i) => {
                  const badge = getErrorBadge(info.error_type);
                  return (
                    <li key={i} className="grammar-error-item">
                      <div className="grammar-error-head">
                        <span className="grammar-error-text">{info.error_text}</span>
                        <span className={`grammar-error-badge grammar-error-badge--${badge.type}`}>
                          {badge.label}
                        </span>
                        <span className="grammar-error-type-label">{info.error_type}</span>
                      </div>
                      <div className="grammar-error-explain">{info.explain}</div>
                    </li>
                  );
                })}
              </ul>
            </div>
          ) : (
            <div className="grammar-section-body grammar-no-error">
              <span className="grammar-no-error-icon">✓</span>
              未发现语法错误，表达地道！
            </div>
          )}
        </div>

        {/* ③ Correction Comparison — matching example-container pattern */}
        <div className="grammar-section">
          <h4 className="grammar-section-heading">修正对比</h4>
          <div className="grammar-section-body" style={{ padding: 0, background: 'none', borderLeft: 'none', boxShadow: 'none' }}>
            <div className="example-container grammar-compare-block">
              <div className="grammar-compare-label">原文</div>
              <div className="grammar-compare-text">
                {hasErrors
                  ? renderHighlightedSentence(result.source_sent, result.error_index)
                  : result.source_sent}
              </div>
            </div>
            <div className="grammar-compare-divider">
              <span className="grammar-compare-arrow">↓ AI 优化 ↓</span>
            </div>
            <div className="example-container grammar-compare-block grammar-compare-block--ai">
              <div className="grammar-compare-label grammar-compare-label--ai">AI 优化</div>
              <div className="grammar-compare-text fixed">{result.fixed_sent}</div>
            </div>
            <div className="grammar-compare-actions">
              <button
                onClick={(e) => { e.stopPropagation(); onSpeak(result.fixed_sent); }}
                className="grammar-action-btn grammar-action-btn--speak"
                title="朗读修正句"
              >
                <SpeakerIcon size={14} />
                朗读
              </button>
              <button
                className="grammar-action-btn grammar-action-btn--fill"
                onClick={() => onFillInput(result.fixed_sent)}
              >
                填入输入框
              </button>
            </div>
          </div>
        </div>
      </>
    );
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', flex: 1, minHeight: 0 }}>
      {/* ---- Input area: matching .word-input-area styling ---- */}
      <div className="grammar-input-row">
        <div className="grammar-voice-input">
          <span className="grammar-voice-label">语音输入</span>

          {recording.state.isRecording && (
            <>
              <div className="waveform">
                <span className="wave-bar" />
                <span className="wave-bar" />
                <span className="wave-bar" />
                <span className="wave-bar" />
                <span className="wave-bar" />
              </div>
              <span className="grammar-recording-time">
                {recording.formatTime(recording.state.seconds)}
              </span>
            </>
          )}

          {!recording.state.isRecording ? (
            <button
              onClick={recording.start}
              className="grammar-voice-btn grammar-voice-btn--start"
            >
              开始录音
            </button>
          ) : (
            <>
              <button
                onClick={recording.stop}
                className="grammar-voice-btn grammar-voice-btn--start"
              >
                结束并发送
              </button>
              <button
                onClick={recording.cancel}
                className="grammar-voice-btn grammar-voice-btn--cancel"
              >
                取消录音
              </button>
            </>
          )}
        </div>
      </div>

      {/* ---- Text input row: 1:1 matching .word-input-area ---- */}
      <div className="grammar-input-row" style={{ marginTop: 10 }}>
        <input
          type="text"
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={loading ? '检测中...' : '输入英文句子...'}
          disabled={loading}
        />
        <button
          onClick={handleSend}
          disabled={loading || !text.trim()}
          style={{ opacity: loading || !text.trim() ? 0.6 : 1 }}
          className="grammar-send-btn"
        >
          发送
        </button>
      </div>

      {/* ---- Result area: matching .word-result container ---- */}
      <div className="grammar-result-container">
        {renderContent()}
      </div>
    </div>
  );
}
