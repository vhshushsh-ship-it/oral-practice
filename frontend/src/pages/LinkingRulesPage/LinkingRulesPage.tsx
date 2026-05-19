import { useSpeechSynthesis } from '../../hooks/useSpeechSynthesis';
import { SpeakerButton } from '../../components/SpeakerButton';
import { linkingRules } from '../../data/linkingRules';

export function LinkingRulesPage() {
  const speak = useSpeechSynthesis(1.0);

  return (
    <div className="page" style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <h1>英语连读规则</h1>
      <div className="content-centered" style={{ flex: 1, overflowY: 'auto' }}>
        <p className="linking-intro">
          掌握连读是地道发音的关键。以下为英语中最核心的 8 条连读规则，每条搭配典型例句示范。点击
          <SpeakerButton onClick={() => {}} size={13} />图标可听标准发音。
        </p>
        <div className="linking-rules-list">
          {linkingRules.map((rule) => (
            <div key={rule.id} className="linking-rule-card">
              <div className="linking-rule-name">
                {rule.name}
                <span className="linking-rule-name-en"> · {rule.nameEn}</span>
              </div>
              <p className="linking-rule-desc">{rule.description}</p>
              <div className="linking-examples">
                {rule.examples.map((ex, i) => (
                  <div key={i} className="linking-example">
                    <div className="linking-example-linked">{ex.linked}</div>
                    <div className="linking-example-original">
                      <span>{ex.original}</span>
                      <button
                        className="speak-btn-text"
                        onClick={() => speak(ex.original)}
                      >
                        <SpeakerButton onClick={() => speak(ex.original)} size={11} />
                        Play
                      </button>
                    </div>
                    <div className="linking-example-zh">{ex.translation}</div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
