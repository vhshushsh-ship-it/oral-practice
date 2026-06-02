import { useEffect, useRef } from 'react';
import type { ConversationMessage } from '../../types';
import { SpeakerButton } from '../../components/SpeakerButton';
import { CollectButton } from '../../components/CollectButton';
import { StudyIcon } from '../../icons';
import { useToast } from '../../components/Toast/toastContext';
import { useSentenceCollection } from '../../hooks/useSentenceCollection';

interface Props {
  messages: ConversationMessage[];
  onSpeak: (text: string) => void;
  onGrammarCheck: (text: string) => void;
}

export function ChatBox({ messages, onSpeak, onGrammarCheck }: Props) {
  const boxRef = useRef<HTMLDivElement>(null);
  const { showToast } = useToast();
  const { addSentence } = useSentenceCollection();

  useEffect(() => {
    if (boxRef.current) {
      boxRef.current.scrollTop = boxRef.current.scrollHeight;
    }
  }, [messages]);

  const handleCollect = async (text: string) => {
    const result = await addSentence(text);
    if (result === 'exists') {
      showToast('该句子已收藏！', 'info');
    } else {
      showToast('句子收藏成功！', 'success');
    }
  };

  return (
    <div className="chat-box" ref={boxRef}>
      {messages.map((msg, i) => (
        <div
          key={i}
          className={msg.role === 'user' ? 'user-msg' : 'ai-msg'}
          onClick={() => onSpeak(msg.content)}
        >
          {msg.role === 'user' && (
            <span
              className="grammar-check-btn"
              onClick={(e) => { e.stopPropagation(); onGrammarCheck(msg.content); }}
              title="语法检测"
            >
              <StudyIcon size={13} />
            </span>
          )}
          <SpeakerButton onClick={() => onSpeak(msg.content)} />
          <span style={{ flex: 1 }}>{msg.content}</span>
          <CollectButton text={msg.content} onCollect={handleCollect} />
        </div>
      ))}
    </div>
  );
}
