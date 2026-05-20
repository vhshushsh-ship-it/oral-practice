import { PlayIcon, PauseIcon, StopIcon, ChevronLeftIcon, ChevronRightIcon, EyeIcon, EyeOffIcon } from '../../icons';

interface Props {
  playState: 'idle' | 'playing' | 'paused';
  currentIndex: number;
  totalCount: number;
  showTranslations: boolean;
  hasSelectedSet: boolean;
  variant?: 'practice' | 'exam';
  onPlay: () => void;
  onPause: () => void;
  onResume: () => void;
  onStop: () => void;
  onNext: () => void;
  onPrev: () => void;
  onToggleTranslations: () => void;
}

export function ListeningPlayer({
  playState,
  currentIndex,
  totalCount,
  showTranslations,
  hasSelectedSet,
  variant = 'practice',
  onPlay,
  onPause,
  onResume,
  onStop,
  onNext,
  onPrev,
  onToggleTranslations,
}: Props) {
  const isActive = playState === 'playing' || playState === 'paused';
  const canNavigate = hasSelectedSet && totalCount > 0;
  const progressText = canNavigate && currentIndex >= 0
    ? `第 ${currentIndex + 1} / ${totalCount} 句`
    : hasSelectedSet
      ? '准备就绪'
      : '';

  return (
    <div className="listening-player">
      {playState === 'playing' ? (
        <button className="player-control-btn active" onClick={onPause} title="暂停">
          <PauseIcon size={14} />
        </button>
      ) : (
        <button className="player-control-btn" onClick={playState === 'paused' ? onResume : onPlay} title="播放全部" disabled={!hasSelectedSet}>
          <PlayIcon size={14} />
        </button>
      )}

      <button className="player-control-btn" onClick={onStop} title="停止" disabled={!isActive}>
        <StopIcon size={14} />
      </button>

      <span className="player-control-separator" />

      <button className="player-control-btn" onClick={onPrev} title="上一句" disabled={!canNavigate || currentIndex <= 0}>
        <ChevronLeftIcon size={14} />
      </button>

      <button className="player-control-btn" onClick={onNext} title="下一句" disabled={!canNavigate || currentIndex >= totalCount - 1}>
        <ChevronRightIcon size={14} />
      </button>

      <span className="player-control-separator" />

      <span className="listening-player-progress">{progressText}</span>

      {variant === 'practice' && (
        <>
          <span className="player-control-separator" />
          <button className="player-control-btn" onClick={onToggleTranslations} title={showTranslations ? '隐藏翻译' : '显示翻译'}>
            {showTranslations ? <EyeIcon size={14} /> : <EyeOffIcon size={14} />}
          </button>
        </>
      )}
    </div>
  );
}
