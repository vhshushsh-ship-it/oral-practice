import { useState, type FormEvent } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../../components/AuthProvider';

export function RegisterPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');

    if (password !== confirmPassword) {
      setError('两次输入的密码不一致');
      return;
    }

    if (password.length < 6) {
      setError('密码长度至少为6位');
      return;
    }

    setIsSubmitting(true);
    try {
      await register(email, password);
      navigate('/', { replace: true });
    } catch (err: any) {
      setError(err.message || 'Registration failed');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="auth-page">
      <form className="auth-form" onSubmit={handleSubmit}>
        <h1>SceneTalk</h1>
        <p className="auth-subtitle">创建新账号</p>
        {error && <div className="auth-error">{error}</div>}
        <div className="auth-field">
          <label htmlFor="reg-email">邮箱</label>
          <input
            id="reg-email"
            type="email"
            placeholder="请输入邮箱地址"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            autoFocus
          />
        </div>
        <div className="auth-field">
          <label htmlFor="reg-password">密码</label>
          <input
            id="reg-password"
            type="password"
            placeholder="请设置密码（至少6位）"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            minLength={6}
          />
        </div>
        <div className="auth-field">
          <label htmlFor="reg-confirm">确认密码</label>
          <input
            id="reg-confirm"
            type="password"
            placeholder="请再次输入密码"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            required
            minLength={6}
          />
        </div>
        <button type="submit" className="auth-btn" disabled={isSubmitting}>
          {isSubmitting ? '注册中...' : '注册'}
        </button>
        <p className="auth-switch">
          已有账号？<Link to="/login">立即登录</Link>
        </p>
      </form>
    </div>
  );
}
