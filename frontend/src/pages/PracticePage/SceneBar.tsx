interface Props {
  sceneChoice: string;
  onSceneChange: (choice: string) => void;
  speechRate: number;
  onSpeechRateChange: (rate: number) => void;
  isTranslateVisible: boolean;
  onToggleTranslate: () => void;
  onClearHistory: () => void;
}

const SCENE_OPTIONS = [
  { value: '0', label: '英语自由交流' },
  { value: '1', label: '餐厅点餐用餐' },
  { value: '2', label: '职场英文面试' },
  { value: '3', label: '酒店入住办理' },
  { value: '4', label: '日常居家交流' },
  { value: '5', label: '出行问路乘车' },
  { value: '6', label: '商场购物逛街' },
  { value: '7', label: '看病就医问诊' },
  { value: '8', label: '校园师生交流' },
  { value: '9', label: '日常社交寒暄' },
  { value: '10', label: '旅游景点沟通' },
  { value: '11', label: '职场工作沟通' },
  { value: '12', label: '生活办事咨询' },
  { value: '13', label: '电话微信沟通' },
  { value: '14', label: '兴趣爱好闲聊' },
  { value: '15', label: '机场高铁出行' },
  { value: '16', label: '租房看房沟通' },
];

export function SceneBar({
  sceneChoice,
  onSceneChange,
  speechRate,
  onSpeechRateChange,
  isTranslateVisible,
  onToggleTranslate,
  onClearHistory,
}: Props) {
  return (
    <div className="scene-bar">
      <select value={sceneChoice} onChange={(e) => onSceneChange(e.target.value)}>
        {SCENE_OPTIONS.map((opt) => (
          <option key={opt.value} value={opt.value}>
            {opt.label}
          </option>
        ))}
      </select>

      <span style={{ marginLeft: 15 }}>语速：</span>
      <select
        value={speechRate}
        onChange={(e) => onSpeechRateChange(parseFloat(e.target.value))}
        id="speechRateSelect"
      >
        <option value={0.7}>慢速</option>
        <option value={1.0}>标准</option>
        <option value={1.5}>快速</option>
      </select>

      <button
        onClick={onToggleTranslate}
        style={{
          padding: '6px 14px',
          background: 'var(--accent-cool)',
          color: '#fff',
          fontSize: 12,
          letterSpacing: '0.04em',
        }}
      >
        {isTranslateVisible ? '隐藏翻译' : '显示翻译'}
      </button>

      <button
        onClick={onClearHistory}
        style={{
          padding: '6px 14px',
          background: 'var(--accent)',
          color: '#fff',
          fontSize: 12,
          letterSpacing: '0.04em',
        }}
      >
        清空记录
      </button>
    </div>
  );
}
