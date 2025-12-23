import React, { createContext, useContext, useReducer, ReactNode } from 'react';
import { Message, ChatbotState } from '../../utils/types';

// Define action types
type ChatbotAction =
  | { type: 'SET_OPEN'; isOpen: boolean }
  | { type: 'ADD_MESSAGE'; message: Message }
  | { type: 'UPDATE_MESSAGE_CONTENT'; messageId: string; content: string }
  | { type: 'ADD_CITATION_TO_MESSAGE'; messageId: string; citation: any }
  | { type: 'SET_LOADING'; isLoading: boolean }
  | { type: 'SET_ERROR'; error: string | null }
  | { type: 'SET_SELECTED_CONTEXT'; context: string | null }
  | { type: 'SET_STREAMING_STATUS'; status: ChatbotState['streamingStatus'] }
  | { type: 'CLEAR_MESSAGES' };

// Initial state
const initialState: ChatbotState = {
  isOpen: false,
  messages: [],
  isLoading: false,
  error: null,
  selectedContext: null,
  streamingStatus: 'idle',
};

// Create context
const ChatbotContext = createContext<{
  state: ChatbotState;
  dispatch: React.Dispatch<ChatbotAction>;
} | undefined>(undefined);

// Reducer function
const chatbotReducer = (state: ChatbotState, action: ChatbotAction): ChatbotState => {
  switch (action.type) {
    case 'SET_OPEN':
      return { ...state, isOpen: action.isOpen };
    case 'ADD_MESSAGE':
      return { ...state, messages: [...state.messages, action.message] };
    case 'UPDATE_MESSAGE_CONTENT':
      return {
        ...state,
        messages: state.messages.map((msg) =>
          msg.id === action.messageId
            ? { ...msg, content: action.content }
            : msg
        ),
      };
    case 'ADD_CITATION_TO_MESSAGE':
      return {
        ...state,
        messages: state.messages.map((msg) =>
          msg.id === action.messageId
            ? {
                ...msg,
                citations: [...(msg.citations || []), action.citation],
              }
            : msg
        ),
      };
    case 'SET_LOADING':
      return { ...state, isLoading: action.isLoading };
    case 'SET_ERROR':
      return { ...state, error: action.error };
    case 'SET_SELECTED_CONTEXT':
      return { ...state, selectedContext: action.context };
    case 'SET_STREAMING_STATUS':
      return { ...state, streamingStatus: action.status };
    case 'CLEAR_MESSAGES':
      return { ...state, messages: [] };
    default:
      return state;
  }
};

// Provider component
interface ChatbotProviderProps {
  children: ReactNode;
}

export const ChatbotProvider: React.FC<ChatbotProviderProps> = ({ children }) => {
  const [state, dispatch] = useReducer(chatbotReducer, initialState);

  return (
    <ChatbotContext.Provider value={{ state, dispatch }}>
      {children}
    </ChatbotContext.Provider>
  );
};

// Custom hook to use the context
export const useChatbot = () => {
  const context = useContext(ChatbotContext);
  if (!context) {
    throw new Error('useChatbot must be used within a ChatbotProvider');
  }
  return context;
};

// Action creators
export const setOpen = (isOpen: boolean) => ({
  type: 'SET_OPEN' as const,
  isOpen,
});

export const addMessage = (message: Message) => ({
  type: 'ADD_MESSAGE' as const,
  message,
});

export const setLoading = (isLoading: boolean) => ({
  type: 'SET_LOADING' as const,
  isLoading,
});

export const setError = (error: string | null) => ({
  type: 'SET_ERROR' as const,
  error,
});

export const setSelectedContext = (context: string | null) => ({
  type: 'SET_SELECTED_CONTEXT' as const,
  context,
});

export const setStreamingStatus = (status: ChatbotState['streamingStatus']) => ({
  type: 'SET_STREAMING_STATUS' as const,
  status,
});

export const clearMessages = () => ({
  type: 'CLEAR_MESSAGES' as const,
});