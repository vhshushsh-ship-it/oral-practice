import { useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from './AuthProvider';

const NAV_ITEMS = [
  { page: 'practice', label: '* SceneTalk' },
  { page: 'dashboard', label: '— 数据看板' },
  { page: 'notes', label: '— 单词笔记' },
  { page: 'dialogues', label: '— 情景对话' },
  { page: 'linking-rules', label: '— 连读规则' },
  { page: 'listening', label: '— 四六级听力练习' },
  { page: 'sentences', label: '— 句子收藏' },
];

export function Sidebar() {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuth();

  const currentPage = location.pathname === '/' ? 'practice' : location.pathname.slice(1);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

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
      <div className="sidebar-footer">
        {user && <div className="sidebar-user">{user.email}</div>}
        <div className="nav-item logout-btn" onClick={handleLogout}>
          — 退出登录
        </div>
      </div>
    </aside>
  );
}
