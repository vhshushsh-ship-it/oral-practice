import { useState, useEffect, useCallback } from 'react';
import type { SentenceAnalysisResult } from '../types';
import { analyzeSentence } from '../services/api';
import { useSpeechSynthesis } from '../hooks/useSpeechSynthesis';
import { useRecording } from '../hooks/useRecording';
import { useRecordingPlayback } from '../hooks/useRecordingPlayback';
import { SpeakerIcon, MicIcon, BookmarkIcon } from '../icons';

const CACHE_PREFIX = 'sa_';

function hashString(s: string): string {
  let hash = 0;
  for (let i = 0; i < s.length; i++) {
    const ch = s.charCodeAt(i);
    hash = ((hash << 5) - hash) + ch;
    hash |= 0;
  }
  return CACHE_PREFIX + Math.abs(hash).toString(36);
}

function getCachedAnalysis(text: string): SentenceAnalysisResult | null {
  try {
    const raw = localStorage.getItem(hashString(text));
    if (raw) return JSON.parse(raw);
  } catch { /* localStorage unavailable or corrupted */ }
  return null;
}

function setCachedAnalysis(text: string, data: SentenceAnalysisResult): void {
  try {
    localStorage.setItem(hashString(text), JSON.stringify(data));
  } catch { /* localStorage full or unavailable */ }
}

interface Props {
  en: string;
  zh?: string;
  showTranslation?: boolean;
  onPlay: () => void;
  onCollect: () => void;
  onBack: () => void;
}

export function SentenceAnalysis({
  en,
  zh,
  showTranslation = true,
  onPlay,
  onCollect,
  onBack,
}: Props) {
  const [result, setResult] = useState<SentenceAnalysisResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const speak = useSpeechSynthesis(1.0);
  const recordingPlayback = useRecordingPlayback();
  const recording = useRecording(recordingPlayback.storeRecording);

  useEffect(() => {
    let cancelled = false;
    setError('');
    setResult(null);

    const cached = getCachedAnalysis(en);
    if (cached) {
      setResult(cached);
      setLoading(false);
      return;
    }

    setLoading(true);

    analyzeSentence(en)
      .then((data) => {
        if (!cancelled) {
          setResult(data);
          setCachedAnalysis(en, data);
        }
      })
      .catch(() => {
        if (!cancelled) setError('分析失败，请返回重试');
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => { cancelled = true; };
  }, [en]);

  const formatTime = useCallback((s: number) => {
    const m = Math.floor(s / 60).toString().padStart(2, '0');
    const sec = (s % 60).toString().padStart(2, '0');
    return `${m}:${sec}`;
  }, []);

  return (
    <div className="sentence-analysis">
      {/* ── Header ── */}
      <div className="sa-header">
        <button className="sa-back-btn" onClick={onBack}>
          &larr; 返回
        </button>
        <span className="sa-title">句子分析</span>
      </div>

      <div className="sa-content">
        {/* ── Sentence reading area ── */}
        <div className="sa-reading-area">
          <div className="sa-sentence-en">
            <span>{en}</span>
            <div className="sa-sentence-actions">
              <button
                className="sentence-action-btn"
                onClick={onPlay}
                title="播放"
              >
                <SpeakerIcon size={13} />
              </button>

              {recording.state.isRecording ? (
                <button className="sentence-action-btn recording" onClick={recording.stop} title="停止录音">
                  <StopSmallIcon size={13} />
                </button>
              ) : (
                <button className="sentence-action-btn" onClick={recording.start} title="录音跟读">
                  <MicIcon size={13} />
                </button>
              )}

              {recordingPlayback.hasRecording && (
                <button
                  className={`sentence-action-btn${recordingPlayback.isPlayingRecording ? ' playing' : ''}`}
                  onClick={recordingPlayback.playRecording}
                  title="回放录音"
                >
                  <PlaySmallIcon size={13} />
                </button>
              )}

              <button className="sentence-action-btn collect" onClick={onCollect} title="收藏">
                <BookmarkIcon size={13} />
              </button>
            </div>
          </div>

          {recording.state.isRecording && (
            <div className="listening-recording-bar">
              <span className="waveform">
                <span className="wave-bar" />
                <span className="wave-bar" />
                <span className="wave-bar" />
                <span className="wave-bar" />
                <span className="wave-bar" />
              </span>
              <span>{formatTime(recording.state.seconds)}</span>
              <span>录音中...</span>
            </div>
          )}

          {showTranslation && zh && (
            <div className="sa-sentence-zh">{zh}</div>
          )}
        </div>

        {/* ── Analysis area ── */}
        <div className="sa-analysis-area">
          {loading && (
            <div className="sa-loading">
              <span className="sa-loading-spinner" />
              <span>正在分析句子发音...</span>
            </div>
          )}

          {error && (
            <div className="sa-error">{error}</div>
          )}

          {result && !loading && (
            <>
              {/* Module 1: Connected Speech */}
              {result.connected_speech && result.connected_speech.length > 0 && (
                <div className="sa-module">
                  <h3 className="sa-module-title">连读现象分析</h3>
                  <ol className="sa-cs-list">
                    {result.connected_speech.map((item, i) => (
                      <li key={i} className="sa-cs-item">
                        <span className="sa-cs-words">{item.words}</span>
                        <span className="sa-cs-phonetic">{item.phonetic}</span>
                        <button
                          className="sa-cs-play-btn"
                          onClick={() => speak(item.words)}
                          title="播放发音"
                        >
                          <SpeakerIcon size={12} />
                        </button>
                        <span className="sa-cs-desc">{item.description}</span>
                      </li>
                    ))}
                  </ol>
                </div>
              )}

              {/* Module 2: Sense Groups */}
              {result.sense_groups && (
                <div className="sa-module">
                  <h3 className="sa-module-title">意群（Sense Group）切分</h3>
                  <div className="sa-sg-segmented">{result.sense_groups.segmented}</div>
                  <div className="sa-sg-explanation">
                    <h4 className="sa-sg-subtitle">划分依据</h4>
                    <p>{result.sense_groups.explanation}</p>
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}

function StopSmallIcon({ size = 13 }: { size?: number }) {
  return (
    <svg viewBox="0 0 24 24" fill="currentColor" stroke="none" width={size} height={size}>
      <rect x="4" y="4" width="16" height="16" rx="2" />
    </svg>
  );
}

function PlaySmallIcon({ size = 13 }: { size?: number }) {
  return (
    <svg viewBox="0 0 24 24" fill="currentColor" stroke="none" width={size} height={size}>
      <polygon points="6 3 20 12 6 21 6 3" />
    </svg>
  );
}
