import { useWordNotes } from '../../hooks/useWordNotes';
import { useSpeechSynthesis } from '../../hooks/useSpeechSynthesis';
import { useToast } from '../../components/Toast/toastContext';
import { NotesFullscreen } from './NotesFullscreen';
import { NotesDetail } from './NotesDetail';

export function NotesPage() {
  const {
    notes,
    sortType,
    setSortType,
    searchKeyword,
    setSearchKeyword,
    isReciteMode,
    setIsReciteMode,
    selectedWord,
    setSelectedWord,
    viewMode,
    setViewMode,
    deleteWord,
    clearAll,
  } = useWordNotes();

  const speak = useSpeechSynthesis(1.0);
  const { showToast } = useToast();

  const handleDeleteWord = (word: string) => {
    deleteWord(word);
    showToast('删除成功！', 'success');
  };

  const handleClearAll = () => {
    if (!window.confirm('确定要清空所有单词笔记吗？')) return;
    clearAll();
    showToast('已清空所有本地笔记！', 'success');
  };

  if (viewMode === 'detail') {
    return (
      <NotesDetail
        notes={notes}
        selectedWord={selectedWord}
        sortType={sortType}
        onSortChange={setSortType}
        searchKeyword={searchKeyword}
        onSearchChange={setSearchKeyword}
        onSelectWord={setSelectedWord}
        onDeleteWord={handleDeleteWord}
        onSpeak={speak}
        onBack={() => setViewMode('fullscreen')}
      />
    );
  }

  return (
    <NotesFullscreen
      notes={notes}
      sortType={sortType}
      onSortChange={setSortType}
      searchKeyword={searchKeyword}
      onSearchChange={setSearchKeyword}
      isReciteMode={isReciteMode}
      onToggleRecite={() => setIsReciteMode(!isReciteMode)}
      onSelectWord={(word) => {
        setSelectedWord(word);
        setViewMode('detail');
      }}
      onDeleteWord={handleDeleteWord}
      onSpeak={speak}
      onClearAll={handleClearAll}
    />
  );
}
