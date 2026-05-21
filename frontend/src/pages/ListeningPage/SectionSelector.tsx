import type { ListeningSection } from '../../types';

interface Props {
  sections: ListeningSection[];
  setId: string;
  onSelect: (section: ListeningSection) => void;
}

function getSectionProgress(setId: string, sectionId: string | null, sentenceIds: string[]): { played: number; pct: number } {
  try {
    const raw = localStorage.getItem(`listening_progress_${setId}`);
    if (!raw) return { played: 0, pct: 0 };
    const data = JSON.parse(raw);
    const playedSet: Set<string> = new Set(data.played ?? []);
    const played = sentenceIds.filter((id) => playedSet.has(id)).length;
    const total = sentenceIds.length;
    return { played, pct: total > 0 ? Math.round((played / total) * 100) : 0 };
  } catch {
    return { played: 0, pct: 0 };
  }
}

export function SectionSelector({ sections, setId, onSelect }: Props) {
  const realSections = sections.filter((s) => s.id !== null);

  return (
    <div className="section-selector-page">
      <h3 className="section-selector-title">选择练习段落</h3>
      <div className="section-selector">
        {realSections.map((section) => {
          const sentences = section.items && section.items.length > 0
            ? section.items.flatMap((item) => item.sentences)
            : (section.sentences || []);
          const sentIds = sentences.map((s) => s.id);
          const total = sentIds.length;
          const { played, pct } = getSectionProgress(setId, section.id, sentIds);
          const statusLabel = played === 0 ? '未开始' : played >= total ? '已完成' : '进行中';

          return (
            <div
              key={section.id}
              className="section-card"
              onClick={() => onSelect(section)}
            >
              <div className="section-card-header">
                <div className="section-card-title">{section.name}</div>
                <span className="section-card-status">{statusLabel}</span>
              </div>
              <div className="section-card-meta">
                {total} 个句子
                {played > 0 && ` · 已练 ${played} 句`}
              </div>
              <div className="section-card-progress">
                <div className="section-card-progress-bar">
                  <div
                    className="section-card-progress-fill"
                    style={{ width: `${pct}%` }}
                  />
                </div>
                <span className="section-card-progress-text">{pct}%</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
