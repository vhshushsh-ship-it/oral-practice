import type { ListeningLevel } from '../../types';

interface Props {
  selectedLevel: ListeningLevel | null;
  onSelect: (level: ListeningLevel) => void;
  variant?: 'hero' | 'compact';
}

export function LevelTabs({ selectedLevel, onSelect, variant = 'compact' }: Props) {
  if (variant === 'hero') {
    return (
      <div className="level-hero">
        <h2 className="level-hero-title">四六级听力练习</h2>
        <p className="level-hero-sub">选择考试类型，开始专项训练</p>
        <div className="level-hero-tabs">
          <button
            className={`level-hero-btn${selectedLevel === 'cet4' ? ' active' : ''}`}
            onClick={() => onSelect('cet4')}
          >
            <span className="level-hero-num">4</span>
            <span className="level-hero-label">四级真题</span>
            <span className="level-hero-hint">CET-4</span>
          </button>
          <button
            className={`level-hero-btn${selectedLevel === 'cet6' ? ' active' : ''}`}
            onClick={() => onSelect('cet6')}
          >
            <span className="level-hero-num">6</span>
            <span className="level-hero-label">六级真题</span>
            <span className="level-hero-hint">CET-6</span>
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="level-tabs">
      <button
        className={`level-tab${selectedLevel === 'cet4' ? ' active' : ''}`}
        onClick={() => onSelect('cet4')}
      >
        四级真题
      </button>
      <button
        className={`level-tab${selectedLevel === 'cet6' ? ' active' : ''}`}
        onClick={() => onSelect('cet6')}
      >
        六级真题
      </button>
    </div>
  );
}
