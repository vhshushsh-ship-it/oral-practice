import { useState, useEffect, useRef, type FormEvent } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../../components/AuthProvider';

export function RegisterPage() {
  const [email, setEmail] = useState('');
  const [code, setCode] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSending, setIsSending] = useState(false);
  const [countdown, setCountdown] = useState(0);
  const [codeSent, setCodeSent] = useState(false);
  const codeInputRef = useRef<HTMLInputElement>(null);

  const { registerWithCode } = useAuth();
  const navigate = useNavigate();

  // ---- 使用 sendVerificationCode 直接调用 API ----
  const { sendCode } = useAuth();

  // Countdown timer
  useEffect(() => {
    if (countdown <= 0) return;
    const timer = setTimeout(() => setCountdown((c) => c - 1), 1000);
    return () => clearTimeout(timer);
  }, [countdown]);

  // Focus code input when codeSent becomes true
  useEffect(() => {
    if (codeSent) {
      codeInputRef.current?.focus();
    }
  }, [codeSent]);

  // ---- 发送验证码 ----
  const handleSendCode = async () => {
    setError('');
    if (!email.trim()) {
      setError('请输入邮箱地址');
      return;
    }
    setIsSending(true);
    try {
      await sendCode(email.trim());
      setCodeSent(true);
      setCountdown(60);
      setError('');
    } catch (err: any) {
      setError(err.message || '发送验证码失败');
    } finally {
      setIsSending(false);
    }
  };

  // ---- 提交注册 ----
  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');

    // 前端强制校验两次密码一致
    if (password !== confirmPassword) {
      setError('两次输入的密码不一致');
      return;
    }

    if (password.length < 6) {
      setError('密码长度至少为6位');
      return;
    }

    if (!code.trim() || code.trim().length !== 6) {
      setError('请输入6位数字验证码');
      return;
    }

    setIsSubmitting(true);
    try {
      await registerWithCode(email.trim(), code.trim(), password, confirmPassword);
      navigate('/', { replace: true });
    } catch (err: any) {
      setError(err.message || '注册失败');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-card">
        <h1 className="auth-title">SceneTalk</h1>
        <p className="auth-subtitle">创建新账号</p>

        {error && <div className="auth-error">{error}</div>}

        <form className="auth-form" onSubmit={handleSubmit}>
          {/* Step 1: 邮箱 + 获取验证码 */}
          <div className="auth-field">
            <label htmlFor="reg-email">邮箱地址</label>
            <input
              id="reg-email"
              type="email"
              placeholder="请输入邮箱地址"
              value={email}
              onChange={(e) => { setEmail(e.target.value); setCodeSent(false); }}
              required
              autoFocus
            />
          </div>

          {!codeSent ? (
            <button
              type="button"
              className="auth-btn"
              disabled={isSending || !email.trim()}
              onClick={handleSendCode}
            >
              {isSending ? '发送中...' : '获取验证码'}
            </button>
          ) : (
            <>
              {/* Step 2: 验证码 */}
              <div className="auth-field">
                <label htmlFor="reg-code">验证码</label>
                <div className="code-input-row">
                  <input
                    ref={codeInputRef}
                    id="reg-code"
                    type="text"
                    inputMode="numeric"
                    maxLength={6}
                    placeholder="请输入6位数字验证码"
                    value={code}
                    onChange={(e) => setCode(e.target.value.replace(/\D/g, ''))}
                    className="code-input"
                    required
                    autoComplete="one-time-code"
                  />
                  <button
                    type="button"
                    className="code-resend-btn"
                    disabled={countdown > 0 || isSending}
                    onClick={handleSendCode}
                  >
                    {countdown > 0 ? `${countdown}s` : '重新发送'}
                  </button>
                </div>
              </div>

              {/* Step 3: 密码 + 确认密码 */}
              <div className="auth-field">
                <label htmlFor="reg-password">设置密码</label>
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

              <button
                type="submit"
                className="auth-btn"
                disabled={isSubmitting || code.length !== 6 || password.length < 6 || confirmPassword.length < 6}
              >
                {isSubmitting ? '注册中...' : '注册'}
              </button>
            </>
          )}
        </form>

        <p className="auth-switch">
          已有账号？<Link to="/login">立即登录</Link>
        </p>
      </div>
    </div>
  );
}
