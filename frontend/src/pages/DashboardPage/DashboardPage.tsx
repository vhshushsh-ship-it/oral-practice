import { useEffect, useState } from 'react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  LineChart, Line, AreaChart, Area, PieChart, Pie, Cell, RadarChart, Radar,
  PolarGrid, PolarAngleAxis, PolarRadiusAxis, Legend,
} from 'recharts';
import {
  fetchOverviewStats, fetchSpeakingStats, fetchListeningStats,
  fetchVocabularyStats, fetchStreakStats,
  type OverviewStats, type SpeakingStats, type ListeningStats,
  type VocabularyStats, type StreakStats,
} from '../../services/api';

// ====================== 颜色（匹配复古主题） ======================
const COLORS = [
  '#4a6fa5', '#8b3a3a', '#5a8a6a', '#a0522d', '#6b5d4e',
  '#3a6b8b', '#7a4a5a', '#4a7a6a', '#8a6a3a', '#5a5a8a',
  '#9b8d7e', '#557788', '#886655', '#668866', '#775577',
  '#996644', '#3a5a7a',
];

const SECTION_LABELS: Record<string, string> = {
  news_report: '新闻短篇',
  long_conversation: '长对话',
  passage: '短文理解',
};

// ====================== 子组件 ======================

/** 顶部概览卡片 */
function OverviewCards({ data }: { data: OverviewStats | null }) {
  if (!data) return null;
  const cards = [
    { label: '累计对话', value: data.totalMessages.toLocaleString(), unit: '轮' },
    { label: '练习时长', value: data.practiceMinutes.toLocaleString(), unit: '分钟' },
    { label: '练习场景', value: `${data.sceneCount}`, unit: '/ 17' },
    { label: '单词收藏', value: data.wordCount.toLocaleString(), unit: '词' },
    { label: '模拟考试', value: `${data.examCount}`, unit: '次' },
    { label: '听力均分', value: `${data.avgAccuracy}`, unit: '%' },
  ];
  return (
    <div className="dash-cards">
      {cards.map((c) => (
        <div key={c.label} className="dash-card">
          <span className="dash-card-label">{c.label}</span>
          <span className="dash-card-value">
            {c.value}<small>{c.unit}</small>
          </span>
        </div>
      ))}
    </div>
  );
}

/** 场景分布 - 横向条形图 */
function SceneDistribution({ data }: { data: SpeakingStats | null }) {
  if (!data || data.sceneStats.length === 0) {
    return <div className="dash-empty">暂无口语练习数据，开始对话吧 ✨</div>;
  }
  const top10 = data.sceneStats.slice(0, 10);
  return (
    <div className="dash-chart">
      <h3 className="dash-chart-title">场景练习分布</h3>
      <ResponsiveContainer width="100%" height={280}>
        <BarChart data={top10} layout="vertical" margin={{ left: 10, right: 20 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#d4c5b0" horizontal={false} />
          <XAxis type="number" tick={{ fontSize: 11, fill: '#9b8d7e' }} />
          <YAxis type="category" dataKey="label" tick={{ fontSize: 12, fill: '#6b5d4e' }} width={70} />
          <Tooltip contentStyle={{ background: '#fefcf7', border: '1px solid #dcd5c5', borderRadius: 3 }} />
          <Bar dataKey="messageCount" fill="#4a6fa5" radius={[0, 3, 3, 0]} name="对话轮数" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

/** 每日对话趋势 */
function DailyTrendChart({ data }: { data: SpeakingStats | null }) {
  if (!data || data.dailyTrend.length === 0) {
    return <div className="dash-empty">暂无练习趋势数据 📈</div>;
  }
  return (
    <div className="dash-chart">
      <h3 className="dash-chart-title">每日对话趋势</h3>
      <ResponsiveContainer width="100%" height={220}>
        <AreaChart data={data.dailyTrend}>
          <CartesianGrid strokeDasharray="3 3" stroke="#d4c5b0" />
          <XAxis dataKey="date" tick={{ fontSize: 10, fill: '#9b8d7e' }} />
          <YAxis tick={{ fontSize: 11, fill: '#9b8d7e' }} />
          <Tooltip contentStyle={{ background: '#fefcf7', border: '1px solid #dcd5c5', borderRadius: 3 }} />
          <Area type="monotone" dataKey="count" stroke="#8b3a3a" fill="#8b3a3a" fillOpacity={0.15} name="消息数" />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}

/** 场景覆盖雷达图 */
function SceneRadar({ data }: { data: SpeakingStats | null }) {
  if (!data || data.sceneStats.length === 0) return null;
  const radarData = data.sceneStats.slice(0, 9).map((s) => ({
    scene: s.label.length > 4 ? s.label.slice(0, 4) : s.label,
    count: s.messageCount,
    full: s.label,
  }));
  return (
    <div className="dash-chart">
      <h3 className="dash-chart-title">场景覆盖雷达</h3>
      <ResponsiveContainer width="100%" height={260}>
        <RadarChart data={radarData}>
          <PolarGrid stroke="#d4c5b0" />
          <PolarAngleAxis dataKey="scene" tick={{ fontSize: 10, fill: '#6b5d4e' }} />
          <PolarRadiusAxis tick={{ fontSize: 9, fill: '#9b8d7e' }} />
          <Radar dataKey="count" stroke="#8b3a3a" fill="#8b3a3a" fillOpacity={0.2} name="对话轮数" />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  );
}

/** 听力成绩趋势 */
function ExamTrend({ data }: { data: ListeningStats | null }) {
  if (!data || data.records.length === 0) {
    return <div className="dash-empty">暂无听力考试记录 🎧</div>;
  }
  const chartData = data.records.map((r) => ({
    name: r.setName.length > 12 ? r.setName.slice(0, 12) + '…' : r.setName,
    正确率: r.accuracy,
    date: r.createdAt?.slice(0, 10) || '',
  }));
  return (
    <div className="dash-chart">
      <h3 className="dash-chart-title">听力成绩趋势</h3>
      <ResponsiveContainer width="100%" height={220}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#d4c5b0" />
          <XAxis dataKey="date" tick={{ fontSize: 10, fill: '#9b8d7e' }} />
          <YAxis domain={[0, 100]} tick={{ fontSize: 11, fill: '#9b8d7e' }} />
          <Tooltip contentStyle={{ background: '#fefcf7', border: '1px solid #dcd5c5', borderRadius: 3 }} />
          <Line type="monotone" dataKey="正确率" stroke="#4a6fa5" strokeWidth={2} dot={{ r: 3 }} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

/** 听力级别对比 + 薄弱项 */
function ListeningBreakdown({ data }: { data: ListeningStats | null }) {
  if (!data) return null;
  return (
    <div className="dash-chart">
      <h3 className="dash-chart-title">听力级别分析</h3>
      <div className="dash-level-cards">
        <div className="dash-level-card">
          <span className="dash-level-num">CET-4</span>
          <span>考试 {data.cet4.count} 次</span>
          <span>均分 {data.cet4.avgAccuracy}%</span>
          <span>最佳 {data.cet4.bestAccuracy}%</span>
        </div>
        <div className="dash-level-card">
          <span className="dash-level-num">CET-6</span>
          <span>考试 {data.cet6.count} 次</span>
          <span>均分 {data.cet6.avgAccuracy}%</span>
          <span>最佳 {data.cet6.bestAccuracy}%</span>
        </div>
      </div>
      {data.weakSections.length > 0 && (
        <>
          <h4 className="dash-subtitle">题型正确率</h4>
          <div className="dash-weak-bars">
            {data.weakSections.map((ws) => (
              <div key={ws.type} className="dash-weak-row">
                <span className="dash-weak-label">{ws.label}</span>
                <div className="dash-weak-bar-bg">
                  <div
                    className="dash-weak-bar-fill"
                    style={{ width: `${ws.accuracy}%` }}
                  />
                </div>
                <span className="dash-weak-pct">{ws.accuracy}%</span>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}

/** 词汇增长 + 最近收藏 */
function VocabularyModule({ data }: { data: VocabularyStats | null }) {
  if (!data) return null;
  return (
    <div className="dash-chart">
      <h3 className="dash-chart-title">
        词汇积累 <span className="dash-highlight">{data.totalWords} 词</span>
      </h3>
      {data.weeklyTrend.length > 0 && (
        <ResponsiveContainer width="100%" height={180}>
          <AreaChart data={data.weeklyTrend}>
            <CartesianGrid strokeDasharray="3 3" stroke="#d4c5b0" />
            <XAxis dataKey="week" tick={{ fontSize: 10, fill: '#9b8d7e' }} />
            <YAxis tick={{ fontSize: 11, fill: '#9b8d7e' }} />
            <Tooltip contentStyle={{ background: '#fefcf7', border: '1px solid #dcd5c5', borderRadius: 3 }} />
            <Area type="monotone" dataKey="count" stroke="#5a8a6a" fill="#5a8a6a" fillOpacity={0.15} name="新增单词" />
          </AreaChart>
        </ResponsiveContainer>
      )}
      {data.recentWords.length > 0 && (
        <div className="dash-recent-words">
          <h4 className="dash-subtitle">最近收藏</h4>
          <div className="dash-word-chips">
            {data.recentWords.map((w) => (
              <span key={w.word} className="dash-word-chip" title={`${w.phonetic} ${w.meaning}`}>
                {w.word}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

/** 打卡 & 成就 */
function StreakModule({ data }: { data: StreakStats | null }) {
  if (!data) return null;
  return (
    <div className="dash-streak-wrap">
      <div className="dash-chart">
        <h3 className="dash-chart-title">坚持打卡</h3>
        <div className="dash-streak-hero">
          <span className="dash-streak-num">{data.streak}</span>
          <span className="dash-streak-label">连续天数</span>
          <span className="dash-streak-sub">共 {data.totalActiveDays} 天活跃</span>
        </div>
      </div>
      <div className="dash-chart">
        <h3 className="dash-chart-title">成就徽章</h3>
        <div className="dash-achievements">
          {data.achievements.map((a) => (
            <div key={a.id} className={`dash-ach-item${a.unlocked ? ' unlocked' : ' locked'}`}>
              <span className="dash-ach-icon">{a.icon}</span>
              <span className="dash-ach-name">{a.name}</span>
              {a.unlocked && <span className="dash-ach-check">✓</span>}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// ====================== 主页面 ======================
export default function DashboardPage() {
  const [overview, setOverview] = useState<OverviewStats | null>(null);
  const [speaking, setSpeaking] = useState<SpeakingStats | null>(null);
  const [listening, setListening] = useState<ListeningStats | null>(null);
  const [vocabulary, setVocabulary] = useState<VocabularyStats | null>(null);
  const [streak, setStreak] = useState<StreakStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadAll() {
      try {
        const [ov, sp, li, vo, st] = await Promise.all([
          fetchOverviewStats(),
          fetchSpeakingStats(),
          fetchListeningStats(),
          fetchVocabularyStats(),
          fetchStreakStats(),
        ]);
        setOverview(ov);
        setSpeaking(sp);
        setListening(li);
        setVocabulary(vo);
        setStreak(st);
      } catch (err) {
        console.error('Dashboard load error:', err);
      } finally {
        setLoading(false);
      }
    }
    loadAll();
  }, []);

  if (loading) {
    return (
      <div className="page">
        <div className="dash-loading">加载看板数据中…</div>
      </div>
    );
  }

  return (
    <div className="page">
      <h1>个人数据看板</h1>

      {/* 模块 1：概览卡片 */}
      <OverviewCards data={overview} />

      {/* 模块 2：口语分析 */}
      <div className="dash-section">
        <h2 className="dash-section-title">🗣️ 口语能力分析</h2>
        <div className="dash-grid-2col">
          <SceneDistribution data={speaking} />
          <DailyTrendChart data={speaking} />
        </div>
        <div className="dash-grid-2col">
          <SceneRadar data={speaking} />
          <ListeningBreakdown data={listening} />
        </div>
      </div>

      {/* 模块 3：听力成绩 */}
      <div className="dash-section">
        <h2 className="dash-section-title">🎧 听力成绩分析</h2>
        <ExamTrend data={listening} />
        {listening && listening.records.length > 0 && (
          <div className="dash-exam-table-wrap">
            <table className="dash-exam-table">
              <thead>
                <tr>
                  <th>时间</th>
                  <th>套题</th>
                  <th>正确率</th>
                  <th>正确/总题</th>
                </tr>
              </thead>
              <tbody>
                {listening.records.slice(-10).reverse().map((r) => (
                  <tr key={r.id}>
                    <td>{r.createdAt?.slice(0, 10) || '-'}</td>
                    <td>{r.setName}</td>
                    <td className={r.accuracy >= 60 ? 'good' : 'fair'}>{r.accuracy}%</td>
                    <td>{r.correctCount}/{r.totalQuestions}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* 模块 4：词汇积累 */}
      <div className="dash-section">
        <h2 className="dash-section-title">📝 词汇积累</h2>
        <VocabularyModule data={vocabulary} />
      </div>

      {/* 模块 5：打卡 & 成就 */}
      <div className="dash-section">
        <h2 className="dash-section-title">🎯 打卡 & 成就</h2>
        <StreakModule data={streak} />
      </div>
    </div>
  );
}
