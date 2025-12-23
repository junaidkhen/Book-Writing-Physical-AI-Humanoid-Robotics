import React, { useState, useEffect, useCallback, useRef } from 'react';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import { useChatbot } from './ChatbotContext';
import ChatMessage from './ChatMessage';
import ChatInput from './ChatInput';
import LoadingIndicator from './LoadingIndicator';
import ErrorMessage from './ErrorMessage';
import { APIClient } from '../../utils/apiClient';
import { Message, StreamChunk } from '../../utils/types';
import { handleAPIError } from '../../utils/errorHandler';
import clsx from 'clsx';
import styles from './ChatbotWidget.module.css';

interface ChatbotWidgetProps {
  apiBaseUrl?: string;
}

const ChatbotWidget: React.FC<ChatbotWidgetProps> = ({ apiBaseUrl }) => {
  const { siteConfig } = useDocusaurusContext();
  const resolvedApiBaseUrl =
    apiBaseUrl ||
    (siteConfig.customFields?.apiBaseUrl as string) ||
    'http://localhost:8000';

  const { state, dispatch } = useChatbot();
  const [apiClient, setApiClient] = useState<APIClient | null>(null);
  const [abortController, setAbortController] = useState<AbortController | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Initialize API client
  useEffect(() => {
    const client = new APIClient({ baseUrl: resolvedApiBaseUrl });
    setApiClient(client);

    (async () => {
      try {
        const isHealthy = await client.healthCheck();
        if (!isHealthy) {
          dispatch({
            type: 'SET_ERROR',
            error: 'API is not available. Please check your connection.',
          });
        }
      } catch (err) {
        console.error('Health check failed:', err);
      }
    })();
  }, [resolvedApiBaseUrl, dispatch]);

  // Auto scroll
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [state.messages, state.streamingStatus]);

  const cancelStream = useCallback(() => {
    abortController?.abort();
    setAbortController(null);
    dispatch({ type: 'SET_STREAMING_STATUS', status: 'cancelled' });
    dispatch({ type: 'SET_LOADING', isLoading: false });
  }, [abortController, dispatch]);

  const handleSendMessage = useCallback(
    async (query: string, context?: string) => {
      if (!apiClient) return;

      abortController?.abort();
      const controller = new AbortController();
      setAbortController(controller);

      try {
        dispatch({ type: 'SET_LOADING', isLoading: true });
        dispatch({ type: 'SET_ERROR', error: null });

        const userMessage: Message = {
          id: crypto.randomUUID(),
          role: 'user',
          content: query,
          timestamp: new Date(),
        };

        dispatch({ type: 'ADD_MESSAGE', message: userMessage });

        dispatch({ type: 'SET_STREAMING_STATUS', status: 'streaming' });

        const assistantId = crypto.randomUUID();
        dispatch({
          type: 'ADD_MESSAGE',
          message: {
            id: assistantId,
            role: 'assistant',
            content: '',
            timestamp: new Date(),
            citations: [],
          },
        });

        await apiClient.askStreamWithFetch(
          { query, context, stream: true },
          (chunk: StreamChunk) => {
            if (chunk.type === 'content') {
              dispatch({
                type: 'UPDATE_MESSAGE_CONTENT',
                messageId: assistantId,
                content: chunk.data?.text || chunk.data || '',
              });
            }
          },
          (err) => {
            dispatch({ type: 'SET_ERROR', error: err.message });
          }
        );
      } catch (err) {
        const parsed = handleAPIError(err);
        dispatch({ type: 'SET_ERROR', error: parsed.message });
      } finally {
        dispatch({ type: 'SET_LOADING', isLoading: false });
        dispatch({ type: 'SET_STREAMING_STATUS', status: 'idle' });
        setAbortController(null);
      }
    },
    [apiClient, abortController, dispatch]
  );

  return (
    <div className={clsx(styles.chatbotContainer, state.isOpen && styles.open)}>
      <div className={styles.chatbotHeader}>
        <h2>Textbook Assistant</h2>
        <button onClick={() => dispatch({ type: 'SET_OPEN', isOpen: !state.isOpen })}>
          ×
        </button>
      </div>

      <div className={styles.messagesContainer}>
        {state.messages.map((m) => (
          <ChatMessage key={m.id} {...m} />
        ))}
        {state.isLoading && <LoadingIndicator message="AI is thinking..." inline />}
        <div ref={messagesEndRef} />
      </div>

      <ChatInput
        onSendMessage={handleSendMessage}
        isLoading={state.isLoading}
      />
    </div>
  );
};

export default ChatbotWidget;
