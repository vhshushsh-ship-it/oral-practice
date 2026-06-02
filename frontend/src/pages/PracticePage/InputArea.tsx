import { useState, useEffect } from 'react';

interface RecordingState {
  isRecording: boolean;
  seconds: number;
}

interface RecordingAPI {
  state: RecordingState;
  start: () => Promise<void>;
  stop: () => void;
  cancel: () => void;
  formatTime: (s: number) => string;
}

interface Props {
  recording: RecordingAPI;
  onSendText: (text: string) => void;
  isLoading: boolean;
  prefillText?: string | null;
  onPrefillConsumed?: () => void;
}

export function InputArea({ recording, onSendText, isLoading, prefillText, onPrefillConsumed }: Props) {
  const [text, setText] = useState('');

  // Accept prefill text from outside (e.g. grammar correction)
  useEffect(() => {
    if (prefillText) {
      setText(prefillText);
      onPrefillConsumed?.();
    }
  }, [prefillText, onPrefillConsumed]);

  const handleSend = () => {
    if (text.trim()) {
      onSendText(text.trim());
      setText('');
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') handleSend();
  };

  return (
    <div className="input-container">
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
          placeholder={isLoading ? '发送中...' : '输入英文...'}
          disabled={isLoading}
          style={{ flex: 1 }}
        />
        <button
          onClick={handleSend}
          disabled={isLoading || !text.trim()}
          style={{
            padding: '10px 20px',
            background: 'var(--accent-cool)',
            color: '#fff',
            fontSize: 13,
            fontFamily: 'var(--font-mono)',
            letterSpacing: '0.04em',
            opacity: isLoading || !text.trim() ? 0.6 : 1,
          }}
        >
          发送
        </button>
      </div>
    </div>
  );
}
