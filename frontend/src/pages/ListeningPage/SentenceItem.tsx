import { SpeakerIcon, MicIcon, BookmarkIcon } from '../../icons';
import type { ListeningSentence } from '../../types';

interface Props {
  sentence: ListeningSentence;
  isActive: boolean;
  showTranslation: boolean;
  isPlayingFull: boolean;
  isRecording: boolean;
  recordingSeconds: number;
  hasRecording: boolean;
  isPlayingRecording: boolean;
  onPlay: () => void;
  onCollect: () => void;
  onStartRecord: () => void;
  onStopRecord: () => void;
  onPlayRecording: () => void;
  onAnalyze: () => void;
}

export function SentenceItem({
  sentence,
  isActive,
  showTranslation,
  isPlayingFull,
  isRecording,
  recordingSeconds,
  hasRecording,
  isPlayingRecording,
  onPlay,
  onCollect,
  onStartRecord,
  onStopRecord,
  onPlayRecording,
  onAnalyze,
}: Props) {
  const singleDisabled = isPlayingFull;

  const formatTime = (s: number) => {
    const m = Math.floor(s / 60).toString().padStart(2, '0');
    const sec = (s % 60).toString().padStart(2, '0');
    return `${m}:${sec}`;
  };

  return (
    <div className={`listening-sentence-item${isActive ? ' active' : ''}`}>
      <div className="listening-sentence-en">
        <span>{sentence.en}</span>
        <div className="listening-sentence-actions">
          <button
            className="sentence-action-btn"
            onClick={onPlay}
            disabled={singleDisabled}
            title="播放"
          >
            <SpeakerIcon size={13} />
          </button>

          {isRecording ? (
            <button className="sentence-action-btn recording" onClick={onStopRecord} title="停止录音">
              <StopSmallIcon size={13} />
            </button>
          ) : (
            <button className="sentence-action-btn" onClick={onStartRecord} title="录音跟读">
              <MicIcon size={13} />
            </button>
          )}

          {hasRecording && (
            <button
              className={`sentence-action-btn${isPlayingRecording ? ' playing' : ''}`}
              onClick={onPlayRecording}
              title="回放录音"
            >
              <PlaySmallIcon size={13} />
            </button>
          )}

          <button className="sentence-action-btn collect" onClick={onCollect} title="收藏">
            <BookmarkIcon size={13} />
          </button>

          <button className="sentence-action-btn analyze" onClick={onAnalyze} title="分析发音">
            <StudyIcon size={13} />
          </button>
        </div>
      </div>

      {isRecording && (
        <div className="listening-recording-bar">
          <span className="waveform">
            <span className="wave-bar" />
            <span className="wave-bar" />
            <span className="wave-bar" />
            <span className="wave-bar" />
            <span className="wave-bar" />
          </span>
          <span>{formatTime(recordingSeconds)}</span>
          <span>录音中...</span>
        </div>
      )}

      {showTranslation && (
        <div className="listening-sentence-zh">{sentence.zh}</div>
      )}
    </div>
  );
}

function StudyIcon({ size = 13 }: { size?: number }) {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"
         strokeLinecap="round" strokeLinejoin="round" width={size} height={size}>
      <circle cx="11" cy="11" r="7" />
      <line x1="16.5" y1="16.5" x2="21" y2="21" />
      <line x1="9" y1="9" x2="9.01" y2="9" />
      <line x1="13" y1="9" x2="13.01" y2="9" />
      <line x1="9" y1="13" x2="9.01" y2="13" />
      <line x1="13" y1="13" x2="13.01" y2="13" />
    </svg>
  );
}

function StopSmallIcon({ size = 13 }: { size?: number }) {
  return (
    <svg viewBox="0 0 24 24" fill="currentColor" stroke="none" width={size} height={size}>
      <rect x="4" y="4" width="16" height="16" rx="2" />
    </svg>
  );
}

function PlaySmallIcon({ size = 13 }: { size?: number }) {
  return (
    <svg viewBox="0 0 24 24" fill="currentColor" stroke="none" width={size} height={size}>
      <polygon points="6 3 20 12 6 21 6 3" />
    </svg>
  );
}
