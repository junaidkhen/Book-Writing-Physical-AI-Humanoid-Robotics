import React from 'react';
import clsx from 'clsx';
import styles from './ChatMessage.module.css';

interface Citation {
  id: string;
  title: string;
  url: string;
  text: string;
  page?: number;
  chapter?: string;
}

interface ChatMessageProps {
  role: 'user' | 'assistant';
  content: string;
  citations?: Citation[];
  timestamp?: Date;
}

const ChatMessage: React.FC<ChatMessageProps> = ({
  role,
  content,
  citations = [],
  timestamp
}) => {
  const isUser = role === 'user';

  return (
    <div className={clsx(styles.message, isUser ? styles.userMessage : styles.assistantMessage)}>
      <div className={styles.messageContent}>
        {content.split('\n').map((paragraph, index) => (
          <p key={index} className={styles.messageParagraph}>
            {paragraph}
          </p>
        ))}
      </div>

      {citations.length > 0 && (
        <div className={styles.citations}>
          <div className={styles.citationTitle}>Sources:</div>
          {citations.map((citation) => (
            <div key={citation.id} className={styles.citation}>
              <a
                href={citation.url}
                className={styles.citationLink}
                onClick={(e) => {
                  e.preventDefault();
                  // Navigate to citation URL
                  window.location.href = citation.url;
                }}
              >
                {citation.title}
                {citation.chapter && <span className={styles.chapterInfo}> ({citation.chapter})</span>}
                {citation.page && <span className={styles.pageInfo}> [p. {citation.page}]</span>}
              </a>
              <div className={styles.citationText}>{citation.text}</div>
            </div>
          ))}
        </div>
      )}

      {timestamp && (
        <div className={styles.timestamp}>
          {timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </div>
      )}
    </div>
  );
};

export default ChatMessage;