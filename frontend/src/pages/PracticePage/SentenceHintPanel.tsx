import { useState, useRef, useCallback, useEffect, useMemo } from 'react';
import { createPortal } from 'react-dom';
import { SCENE_HINTS, type SentenceHintCategory } from '../../data/sentenceHints';
import { generateHints, type HintsResult } from '../../services/api';
import type { ConversationMessage } from '../../types';
import { HintIcon } from '../../icons';

interface Props {
  sceneChoice: string;
  scene: string;
  messages: ConversationMessage[];
  onFillInput: (text: string) => void;
}

type Tab = 'patterns' | 'vocabulary';

export function SentenceHintPanel({ sceneChoice, scene, messages, onFillInput }: Props) {
  const [isOpen, setIsOpen] = useState(false);
  const [activeTab, setActiveTab] = useState<Tab>('patterns');
  const buttonRef = useRef<HTMLButtonElement>(null);
  const panelRef = useRef<HTMLDivElement>(null);
  const [panelPos, setPanelPos] = useState({ top: 0, left: 0 });

  // ---- AI generation state ----
  const [aiHints, setAiHints] = useState<HintsResult | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [genError, setGenError] = useState('');
  const lastMessagesHashRef = useRef<string>('');

  // Static fallback data
  const staticHints: SentenceHintCategory = SCENE_HINTS[sceneChoice] ?? SCENE_HINTS['0'];

  // Compute a fingerprint of the last 10 messages to detect meaningful changes
  const messagesHash = useMemo(() => {
    if (messages.length === 0) return '';
    const lastMessages = messages.slice(-10);
    return JSON.stringify(lastMessages.map(m => ({ r: m.role, c: m.content })));
  }, [messages]);

  // Trigger AI generation when panel opens and messages have changed
  useEffect(() => {
    if (!isOpen) return;
    // No conversation yet — stick with static data
    if (messages.length === 0) return;
    // Cache hit — same conversation, no need to regenerate
    if (aiHints && lastMessagesHashRef.current === messagesHash) return;

    let cancelled = false;

    const fetchHints = async () => {
      setIsGenerating(true);
      setGenError('');
      try {
        const result = await generateHints(scene, sceneChoice, messages);
        if (!cancelled) {
          setAiHints(result);
          lastMessagesHashRef.current = messagesHash;
        }
      } catch (err) {
        if (!cancelled) {
          setGenError(err instanceof Error ? err.message : '生成失败，请重试');
        }
      } finally {
        if (!cancelled) setIsGenerating(false);
      }
    };

    fetchHints();
    return () => { cancelled = true; };
  }, [isOpen, messagesHash, scene, sceneChoice]); // eslint-disable-line react-hooks/exhaustive-deps

  // Use AI hints when available, otherwise fall back to static data
  const hints: SentenceHintCategory = aiHints ?? staticHints;

  // Calculate panel position from button bounding rect
  const updatePosition = useCallback(() => {
    if (!buttonRef.current) return;
    const rect = buttonRef.current.getBoundingClientRect();
    const panelWidth = 340;
    const panelMaxHeight = 420;
    const spaceAbove = rect.top;
    const spaceBelow = window.innerHeight - rect.bottom;
    let top: number;
    if (spaceBelow >= panelMaxHeight || spaceBelow >= spaceAbove) {
      top = rect.bottom + 6;
    } else {
      top = rect.top - panelMaxHeight - 6;
    }
    let left = rect.left;
    if (left + panelWidth > window.innerWidth - 12) {
      left = window.innerWidth - panelWidth - 12;
    }
    if (left < 12) left = 12;
    setPanelPos({ top, left });
  }, []);

  useEffect(() => {
    if (isOpen) {
      updatePosition();
      window.addEventListener('scroll', updatePosition, true);
      window.addEventListener('resize', updatePosition);
      return () => {
        window.removeEventListener('scroll', updatePosition, true);
        window.removeEventListener('resize', updatePosition);
      };
    }
  }, [isOpen, updatePosition]);

  // Close on outside click
  useEffect(() => {
    if (!isOpen) return;
    const handleClick = (e: MouseEvent) => {
      if (
        panelRef.current &&
        !panelRef.current.contains(e.target as Node) &&
        buttonRef.current &&
        !buttonRef.current.contains(e.target as Node)
      ) {
        setIsOpen(false);
      }
    };
    const timer = setTimeout(() => {
      document.addEventListener('mousedown', handleClick);
    }, 0);
    return () => {
      clearTimeout(timer);
      document.removeEventListener('mousedown', handleClick);
    };
  }, [isOpen]);

  // Close on Escape
  useEffect(() => {
    if (!isOpen) return;
    const handleKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setIsOpen(false);
    };
    document.addEventListener('keydown', handleKey);
    return () => document.removeEventListener('keydown', handleKey);
  }, [isOpen]);

  const handleToggle = () => {
    setIsOpen((prev) => !prev);
  };

  const handleSelect = (text: string) => {
    onFillInput(text);
    setIsOpen(false);
  };

  const handleRetry = () => {
    setGenError('');
    lastMessagesHashRef.current = '';
  };

  const items = activeTab === 'patterns' ? hints.patterns : hints.vocabulary;

  const panel = isOpen && createPortal(
    <div
      ref={panelRef}
      className="sentence-hint-panel"
      style={{
        position: 'fixed',
        top: panelPos.top,
        left: panelPos.left,
        width: 340,
        maxHeight: 420,
        zIndex: 10000,
      }}
    >
      {/* Arrow pointing up to the button */}
      <div className="sentence-hint-arrow" />

      {/* Header with tabs */}
      <div className="sentence-hint-header">
        <span className="sentence-hint-title">
          句型提示
          {aiHints && (
            <span className="sentence-hint-ai-badge" title="AI 根据当前对话生成">AI</span>
          )}
        </span>
        <div className="sentence-hint-tabs">
          <button
            className={`sentence-hint-tab${activeTab === 'patterns' ? ' active' : ''}`}
            onClick={() => setActiveTab('patterns')}
          >
            常用句型
          </button>
          <button
            className={`sentence-hint-tab${activeTab === 'vocabulary' ? ' active' : ''}`}
            onClick={() => setActiveTab('vocabulary')}
          >
            核心词汇
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="sentence-hint-body">
        {isGenerating ? (
          <div className="sentence-hint-loading">
            <div className="sentence-hint-skeleton-line" />
            <div className="sentence-hint-skeleton-line" />
            <div className="sentence-hint-skeleton-line" />
            <div className="sentence-hint-skeleton-line" />
            <div className="sentence-hint-skeleton-line" />
            <p className="sentence-hint-loading-text">AI 正在分析对话生成提示…</p>
          </div>
        ) : genError ? (
          <div className="sentence-hint-error">
            <p>{genError}</p>
            <button className="sentence-hint-retry-btn" onClick={handleRetry}>重试</button>
          </div>
        ) : activeTab === 'patterns' ? (
          <ul className="sentence-hint-list">
            {items.map((text, i) => (
              <li key={i}>
                <button
                  className="sentence-hint-item"
                  onClick={() => handleSelect(text)}
                  title="点击填入输入框"
                >
                  {text}
                </button>
              </li>
            ))}
          </ul>
        ) : (
          <div className="sentence-hint-vocab-grid">
            {items.map((word, i) => (
              <button
                key={i}
                className="sentence-hint-vocab-chip"
                onClick={() => handleSelect(word)}
                title="点击填入输入框"
              >
                {word}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Footer hint */}
      <div className="sentence-hint-footer">
        点击任意内容即可填入输入框
      </div>
    </div>,
    document.body,
  );

  return (
    <>
      <button
        ref={buttonRef}
        onClick={handleToggle}
        className={`sentence-hint-btn${isOpen ? ' active' : ''}${isGenerating ? ' loading' : ''}`}
        title="句型提示"
        style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: 4,
          padding: '8px 14px',
          background: isOpen ? 'var(--accent-cool)' : 'var(--paper-dark)',
          color: isOpen ? '#fff' : 'var(--ink)',
          fontSize: 13,
          fontFamily: 'var(--font-mono)',
          letterSpacing: '0.04em',
          border: '1px solid var(--line)',
          borderRadius: 3,
          cursor: 'pointer',
          transition: 'all var(--transition)',
          whiteSpace: 'nowrap',
        }}
      >
        <HintIcon size={14} />
        句型提示
        {isGenerating && <span className="sentence-hint-spinner" />}
      </button>
      {panel}
    </>
  );
}
