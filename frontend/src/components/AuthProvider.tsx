import { createContext, useContext, useState, useEffect, useCallback, type ReactNode } from 'react';
import type { AuthUser } from '../services/api';
import {
  login as apiLogin,
  register as apiRegister,
  sendVerificationCode,
  verifyCodeAndRegister,
  fetchCurrentUser,
} from '../services/api';

interface AuthContextType {
  user: AuthUser | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
  sendCode: (email: string) => Promise<void>;
  registerWithCode: (email: string, code: string, password: string, confirmPassword: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // On mount, try to restore session from stored token
  useEffect(() => {
    fetchCurrentUser().then((u) => {
      setUser(u);
      setIsLoading(false);
    });
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    const res = await apiLogin(email, password);
    sessionStorage.setItem('access_token', res.access_token);
    setUser(res.user);
  }, []);

  const register = useCallback(async (email: string, password: string) => {
    const res = await apiRegister(email, password);
    sessionStorage.setItem('access_token', res.access_token);
    setUser(res.user);
  }, []);

  const sendCode = useCallback(async (email: string) => {
    await sendVerificationCode(email);
  }, []);

  const registerWithCode = useCallback(async (email: string, code: string, password: string, confirmPassword: string) => {
    const res = await verifyCodeAndRegister(email, code, password, confirmPassword);
    sessionStorage.setItem('access_token', res.access_token);
    setUser(res.user);
  }, []);

  const logout = useCallback(() => {
    sessionStorage.removeItem('access_token');
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading,
        isAuthenticated: !!user,
        login,
        register,
        sendCode,
        registerWithCode,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
