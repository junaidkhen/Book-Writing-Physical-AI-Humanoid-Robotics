import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { useChatbot } from '../RAGChatbot/ChatbotContext';
import clsx from 'clsx';
import styles from './TextSelectionProvider.module.css';

interface TextSelectionContextType {
  selectedText: string | null;
  setSelectedText: (text: string | null) => void;
}

const TextSelectionContext = createContext<TextSelectionContextType | undefined>(undefined);

interface TextSelectionProviderProps {
  children: ReactNode;
}

export const TextSelectionProvider: React.FC<TextSelectionProviderProps> = ({ children }) => {
  const [selectedText, setSelectedText] = useState<string | null>(null);
  const { dispatch } = useChatbot();

  // Handle text selection
  useEffect(() => {
    const handleSelection = () => {
      const selection = window.getSelection();
      const text = selection?.toString().trim() || null;

      if (text && text.length > 0) {
        setSelectedText(text);
        // Set the selected context in the chatbot state
        dispatch({ type: 'SET_SELECTED_CONTEXT', context: text });
      } else {
        setSelectedText(null);
        dispatch({ type: 'SET_SELECTED_CONTEXT', context: null });
      }
    };

    // Add event listeners
    document.addEventListener('mouseup', handleSelection);
    document.addEventListener('keyup', (e) => {
      if (e.key === 'Escape') {
        setSelectedText(null);
        dispatch({ type: 'SET_SELECTED_CONTEXT', context: null });
      }
    });

    // Cleanup
    return () => {
      document.removeEventListener('mouseup', handleSelection);
      document.removeEventListener('keyup', (e) => {
        if (e.key === 'Escape') {
          setSelectedText(null);
          dispatch({ type: 'SET_SELECTED_CONTEXT', context: null });
        }
      });
    };
  }, [dispatch]);

  return (
    <TextSelectionContext.Provider value={{ selectedText, setSelectedText }}>
      {children}
      {selectedText && <AskAIButton selectedText={selectedText} />}
    </TextSelectionContext.Provider>
  );
};

// Ask AI Button component
interface AskAIButtonProps {
  selectedText: string;
}

const AskAIButton: React.FC<AskAIButtonProps> = ({ selectedText }) => {
  const { state, dispatch } = useChatbot();

  const handleClick = () => {
    // Open the chatbot if it's closed
    if (!state.isOpen) {
      dispatch({ type: 'SET_OPEN', isOpen: true });
    }

    // Clear the current selection
    const selection = window.getSelection();
    if (selection) {
      selection.removeAllRanges();
    }

    // Set the selected text as context and focus the input
    dispatch({ type: 'SET_SELECTED_CONTEXT', context: selectedText });
  };

  // Get the position of the selection to place the button near it
  useEffect(() => {
    const selection = window.getSelection();
    if (!selection || selection.rangeCount === 0) return;

    const range = selection.getRangeAt(0);
    const rect = range.getBoundingClientRect();

    const button = document.getElementById('ask-ai-button');
    if (button) {
      // Position the button near the selection
      button.style.top = `${rect.top + window.scrollY - 50}px`;
      button.style.left = `${rect.left + window.scrollX + rect.width / 2}px`;
    }
  }, [selectedText]);

  return (
    <button
      id="ask-ai-button"
      className={clsx(styles.askAIButton)}
      onClick={handleClick}
      title="Ask AI about selected text"
    >
      💬 Ask AI
    </button>
  );
};

// Custom hook to use the text selection context
export const useTextSelection = () => {
  const context = useContext(TextSelectionContext);
  if (!context) {
    throw new Error('useTextSelection must be used within a TextSelectionProvider');
  }
  return context;
};