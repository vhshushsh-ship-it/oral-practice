import { Routes, Route, Navigate } from 'react-router-dom';
import { ToastProvider } from './components/Toast/toastContext';
import { AuthProvider } from './components/AuthProvider';
import { ProtectedRoute } from './components/ProtectedRoute';
import { Sidebar } from './components/Sidebar';
import { LoginPage } from './pages/LoginPage/LoginPage';
import { RegisterPage } from './pages/RegisterPage/RegisterPage';
import { PracticePage } from './pages/PracticePage/PracticePage';
import { NotesPage } from './pages/NotesPage/NotesPage';
import { DialoguesPage } from './pages/DialoguesPage/DialoguesPage';
import { SentencesPage } from './pages/SentencesPage/SentencesPage';
import { LinkingRulesPage } from './pages/LinkingRulesPage/LinkingRulesPage';
import { ListeningPage } from './pages/ListeningPage/ListeningPage';

export default function App() {
  return (
    <AuthProvider>
      <ToastProvider>
        <Routes>
          {/* Public routes — no sidebar */}
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />

          {/* Protected routes — with sidebar */}
          <Route
            path="/*"
            element={
              <ProtectedRoute>
                <div className="app-wrapper">
                  <Sidebar />
                  <main className="main-content">
                    <Routes>
                      <Route path="/" element={<PracticePage />} />
                      <Route path="/notes" element={<NotesPage />} />
                      <Route path="/dialogues" element={<DialoguesPage />} />
                      <Route path="/sentences" element={<SentencesPage />} />
                      <Route path="/linking-rules" element={<LinkingRulesPage />} />
                      <Route path="/listening" element={<ListeningPage />} />
                      <Route path="*" element={<Navigate to="/" replace />} />
                    </Routes>
                  </main>
                </div>
              </ProtectedRoute>
            }
          />
        </Routes>
      </ToastProvider>
    </AuthProvider>
  );
}
