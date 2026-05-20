import { useState } from 'react';
import type { ExamResult } from '../../types';

interface Props {
  result: ExamResult;
  setTitle: string;
  onBack: () => void;
}

export function ExamResultView({ result, setTitle, onBack }: Props) {
  const [expandedId, setExpandedId] = useState<string | null>(null);

  const accuracyClass = result.accuracy >= 80 ? 'good' : result.accuracy >= 60 ? 'fair' : 'poor';

  return (
    <div className="exam-result">
      <div className="result-summary">
        <div className="result-score-text">正确率</div>
        <div className={`result-accuracy ${accuracyClass}`}>
          {result.accuracy}%
        </div>
        <div className="result-score-text">
          答对 {result.correctCount} / {result.totalQuestions} 题
        </div>
        <div className="result-set-name">{setTitle}</div>
      </div>

      <div className="result-detail-list">
        {(result.details ?? []).map((d) => (
          <div
            key={d.questionId}
            className={`result-detail-item${expandedId === d.questionId ? ' expanded' : ''}`}
            onClick={() => setExpandedId(expandedId === d.questionId ? null : d.questionId)}
          >
            <span className="result-q-num">#{d.questionNumber}</span>
            <span className="result-q-answers">
              {d.isCorrect ? (
                <span className="answer-badge correct-badge">{d.userAnswer}</span>
              ) : (
                <>
                  <span className="answer-badge wrong-badge">{d.userAnswer || '-'}</span>
                  <span style={{ fontSize: 11, color: 'var(--ink-muted)' }}>&rarr;</span>
                  <span className="answer-badge correct-badge">{d.correctAnswer}</span>
                </>
              )}
            </span>
            <span className="result-q-text">{d.questionText}</span>
          </div>
        ))}
      </div>

      <button className="result-back-btn" onClick={onBack}>
        返回列表
      </button>
    </div>
  );
}
