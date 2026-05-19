import { useLocation, useNavigate } from 'react-router-dom';

const NAV_ITEMS = [
  { page: 'practice', label: '* SceneTalk' },
  { page: 'notes', label: '— 单词笔记' },
  { page: 'dialogues', label: '— 情景对话' },
  { page: 'linking-rules', label: '— 连读规则' },
  { page: 'sentences', label: '— 句子收藏' },
];

export function Sidebar() {
  const location = useLocation();
  const navigate = useNavigate();

  const currentPage = location.pathname === '/' ? 'practice' : location.pathname.slice(1);

  return (
    <aside className="sidebar">
      {NAV_ITEMS.map((item) => (
        <div
          key={item.page}
          className={`nav-item${currentPage === item.page ? ' active' : ''}`}
          onClick={() => navigate(item.page === 'practice' ? '/' : `/${item.page}`)}
        >
          {item.label}
        </div>
      ))}
    </aside>
  );
}
