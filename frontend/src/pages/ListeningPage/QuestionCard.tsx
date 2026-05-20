import { SpeakerIcon, MicIcon, BookmarkIcon } from '../../icons';
import type { ListeningQuestion } from '../../types';

interface Props {
  question: ListeningQuestion;
  selectedOption: string;
  correctAnswer?: string;
  userAnswer?: string;
  disabled: boolean;
  showResult: boolean;
  highlighted?: boolean;
  readOnly?: boolean;
  practiceMode?: boolean;
  isPlayingFull?: boolean;
  isRecording?: boolean;
  recordingSeconds?: number;
  hasRecording?: boolean;
  isPlayingRecording?: boolean;
  onPlay?: () => void;
  onCollect?: () => void;
  onStartRecord?: () => void;
  onStopRecord?: () => void;
  onPlayRecording?: () => void;
  onSelect: (option: string) => void;
}

const OPTIONS = ['A', 'B', 'C', 'D'] as const;

export function QuestionCard({
  question,
  selectedOption,
  correctAnswer,
  userAnswer,
  disabled,
  showResult,
  highlighted,
  readOnly,
  practiceMode,
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
  onSelect,
}: Props) {
  const hasOptions = question.option_a || question.option_b || question.option_c || question.option_d;
  const optionTexts: Record<string, string> = {
    A: question.option_a,
    B: question.option_b,
    C: question.option_c,
    D: question.option_d,
  };

  const formatTime = (s: number) => {
    const m = Math.floor(s / 60).toString().padStart(2, '0');
    const sec = (s % 60).toString().padStart(2, '0');
    return `${m}:${sec}`;
  };

  if (practiceMode) {
    return (
      <div className={`question-card practice-mode${highlighted ? ' highlighted' : ''}`}>
        <div className="question-card-content">
          <div className="question-number">
            Question {question.question_number}
            {question.item_name && (
              <span style={{ marginLeft: 8, fontWeight: 400 }}>— {question.item_name}</span>
            )}
          </div>
          <div className="question-text">{question.question_text}</div>
          {question.question_text_zh && (
            <div className="question-text-zh">{question.question_text_zh}</div>
          )}
          {hasOptions && (
            <div className="question-options read-only-options">
              {OPTIONS.map((opt) => (
                <div key={opt} className="option-text">
                  <span className="option-label">{opt}.</span> {optionTexts[opt]}
                </div>
              ))}
            </div>
          )}
          {isRecording && (
            <div className="listening-recording-bar">
              <span className="waveform">
                <span className="wave-bar" />
                <span className="wave-bar" />
                <span className="wave-bar" />
                <span className="wave-bar" />
                <span className="wave-bar" />
              </span>
              <span>{formatTime(recordingSeconds ?? 0)}</span>
              <span>录音中...</span>
            </div>
          )}
        </div>
        <div className="listening-sentence-actions">
          <button
            className="sentence-action-btn"
            onClick={onPlay}
            disabled={isPlayingFull}
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
        </div>
      </div>
    );
  }

  return (
    <div className={`question-card${highlighted ? ' highlighted' : ''}${readOnly ? ' read-only' : ''}`}>
      <div className="question-number">
        Question {question.question_number}
        {question.item_name && (
          <span style={{ marginLeft: 8, fontWeight: 400 }}>— {question.item_name}</span>
        )}
      </div>
      <div className="question-text">{question.question_text}</div>
      {question.question_text_zh && (
        <div className="question-text-zh">{question.question_text_zh}</div>
      )}
      {readOnly ? (
        hasOptions ? (
          <div className="question-options read-only-options">
            {OPTIONS.map((opt) => (
              <div key={opt} className="option-text">
                <span className="option-label">{opt}.</span> {optionTexts[opt]}
              </div>
            ))}
          </div>
        ) : null
      ) : (
        <div className="question-options">
          {OPTIONS.map((opt) => {
            let cls = 'option-btn';
            if (showResult && correctAnswer === opt) cls += ' correct';
            if (showResult && userAnswer === opt && userAnswer !== correctAnswer) cls += ' wrong';
            if (!showResult && selectedOption === opt) cls += ' selected';
            return (
              <button
                key={opt}
                className={cls}
                disabled={disabled}
                onClick={() => onSelect(opt)}
              >
                <span className="option-btn-label">{opt}.</span>
                <span className="option-btn-text">{optionTexts[opt]}</span>
              </button>
            );
          })}
        </div>
      )}
    </div>
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
