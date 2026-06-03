import { useState, type FormEvent } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../../components/AuthProvider';

export function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    setIsSubmitting(true);
    try {
      await login(email.trim(), password);
      navigate('/', { replace: true });
    } catch (err: any) {
      setError(err.message || '登录失败');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-card">
        <h1 className="auth-title">SceneTalk</h1>
        <p className="auth-subtitle">AI 英语口语练习平台</p>

        {error && <div className="auth-error">{error}</div>}

        <form className="auth-form" onSubmit={handleSubmit}>
          <div className="auth-field">
            <label htmlFor="login-email">邮箱地址</label>
            <input
              id="login-email"
              type="email"
              placeholder="请输入注册邮箱"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              autoFocus
            />
          </div>
          <div className="auth-field">
            <label htmlFor="login-password">密码</label>
            <input
              id="login-password"
              type="password"
              placeholder="请输入密码"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              minLength={6}
            />
          </div>
          <button type="submit" className="auth-btn" disabled={isSubmitting}>
            {isSubmitting ? '登录中...' : '登录'}
          </button>
        </form>

        <p className="auth-switch">
          还没有账号？<Link to="/register">立即注册</Link>
        </p>
      </div>
    </div>
  );
}
