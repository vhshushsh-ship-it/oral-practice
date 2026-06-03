import { PlayIcon, PauseIcon, StopIcon, ChevronLeftIcon, ChevronRightIcon } from '../icons';

interface Props {
  playState: 'idle' | 'playing' | 'paused';
  currentIndex: number;
  /** 播放列表中的句子总数（由 useSequentialTTS 管理，仅 play() 后才有值） */
  totalCount: number;
  /** 当前场景是否有对话句子（来自场景数据） — 控制按钮初始可用性 */
  hasContent: boolean;
  onPlayAll: () => void;
  onPause: () => void;
  onResume: () => void;
  onStop: () => void;
  onNext: () => void;
  onPrev: () => void;
}

/**
 * 全局音频控制栏 — 连续播放整套场景对话
 * UI 样式、按钮布局与四六级听力播放器（ListeningPlayer）完全统一
 */
export function GlobalAudioBar({
  playState,
  currentIndex,
  totalCount,
  hasContent,
  onPlayAll,
  onPause,
  onResume,
  onStop,
  onNext,
  onPrev,
}: Props) {
  const isActive = playState === 'playing' || playState === 'paused';
  // 切句控制需要同时满足：有数据 + 播放列表已创建 + 下标在有效范围内
  const canNavigate = hasContent && totalCount > 0;
  const progressText =
    canNavigate && currentIndex >= 0
      ? `第 ${currentIndex + 1} / ${totalCount} 句`
      : hasContent
        ? '准备就绪'
        : '暂无对话';

  return (
    <div className="listening-player">
      {/* 播放全部 / 暂停 — 同按钮切换 */}
      {playState === 'playing' ? (
        <button className="player-control-btn active" onClick={onPause} title="暂停">
          <PauseIcon size={14} />
        </button>
      ) : (
        <button
          className="player-control-btn"
          onClick={playState === 'paused' ? onResume : onPlayAll}
          title="播放全部"
          disabled={!hasContent}
        >
          <PlayIcon size={14} />
        </button>
      )}

      {/* 停止 */}
      <button className="player-control-btn" onClick={onStop} title="停止" disabled={!isActive}>
        <StopIcon size={14} />
      </button>

      <span className="player-control-separator" />

      {/* 上一句 */}
      <button
        className="player-control-btn"
        onClick={onPrev}
        title="上一句"
        disabled={!canNavigate || currentIndex <= 0}
      >
        <ChevronLeftIcon size={14} />
      </button>

      {/* 下一句 */}
      <button
        className="player-control-btn"
        onClick={onNext}
        title="下一句"
        disabled={!canNavigate || currentIndex >= totalCount - 1}
      >
        <ChevronRightIcon size={14} />
      </button>

      <span className="player-control-separator" />

      {/* 进度文本 */}
      <span className="listening-player-progress">{progressText}</span>
    </div>
  );
}
