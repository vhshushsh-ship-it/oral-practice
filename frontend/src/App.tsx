import { Routes, Route } from 'react-router-dom';
import { ToastProvider } from './components/Toast/toastContext';
import { Sidebar } from './components/Sidebar';
import { PracticePage } from './pages/PracticePage/PracticePage';
import { NotesPage } from './pages/NotesPage/NotesPage';
import { DialoguesPage } from './pages/DialoguesPage/DialoguesPage';
import { SentencesPage } from './pages/SentencesPage/SentencesPage';
import { LinkingRulesPage } from './pages/LinkingRulesPage/LinkingRulesPage';

export default function App() {
  return (
    <ToastProvider>
      <div className="app-wrapper">
        <Sidebar />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<PracticePage />} />
            <Route path="/notes" element={<NotesPage />} />
            <Route path="/dialogues" element={<DialoguesPage />} />
            <Route path="/sentences" element={<SentencesPage />} />
            <Route path="/linking-rules" element={<LinkingRulesPage />} />
          </Routes>
        </main>
      </div>
    </ToastProvider>
  );
}
