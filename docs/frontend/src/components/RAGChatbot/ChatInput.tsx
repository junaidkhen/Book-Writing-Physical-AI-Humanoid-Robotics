import React, { useState, useRef, KeyboardEvent } from 'react';
import clsx from 'clsx';
import styles from './ChatInput.module.css';

interface ChatInputProps {
  onSendMessage: (message: string, context?: string) => void;
  isLoading: boolean;
  placeholder?: string;
  context?: string;
}

const ChatInput: React.FC<ChatInputProps> = ({
  onSendMessage,
  isLoading = false,
  placeholder = 'Ask a question about the textbook...',
  context
}) => {
  const [inputValue, setInputValue] = useState<string>('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSubmit = () => {
    const trimmedValue = inputValue.trim();
    if (trimmedValue && !isLoading) {
      onSendMessage(trimmedValue, context);
      setInputValue('');
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleInput = () => {
    if (textareaRef.current) {
      // Auto-resize textarea based on content
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 150)}px`;
    }
  };

  return (
    <div className={styles.chatInputContainer}>
      {context && (
        <div className={styles.contextPreview}>
          <div className={styles.contextLabel}>Context:</div>
          <div className={styles.contextText}>{context}</div>
          <button
            className={styles.clearContextButton}
            onClick={() => onSendMessage(inputValue.trim(), '')}
            type="button"
          >
            Clear
          </button>
        </div>
      )}
      <div className={styles.inputArea}>
        <textarea
          ref={textareaRef}
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onInput={handleInput}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          disabled={isLoading}
          className={styles.textarea}
          rows={1}
        />
        <button
          onClick={handleSubmit}
          disabled={isLoading || !inputValue.trim()}
          className={clsx(
            styles.sendButton,
            (isLoading || !inputValue.trim()) ? styles.sendButtonDisabled : ''
          )}
          type="button"
        >
          {isLoading ? (
            <span className={styles.loadingSpinner}>●●●</span>
          ) : (
            'Send'
          )}
        </button>
      </div>
    </div>
  );
};

export default ChatInput;