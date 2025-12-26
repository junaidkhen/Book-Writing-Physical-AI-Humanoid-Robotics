// API client utility for the RAG Chatbot
import { APIRequest, APIResponse, StreamChunk } from './types';
import { handleAPIError, ChatbotError } from './errorHandler';
import { validateQuery, validateContext } from './validators';

export class APIClient {
  private baseUrl: string;
  private timeout: number;

  constructor(config: { baseUrl: string; timeout?: number } = {
    baseUrl: process.env.REACT_APP_API_URL || 'https://junaidkh84-python-backend.hf.space',
    timeout: 30000
  }) {
    // Validate and potentially adjust the base URL based on environment
    this.baseUrl = this.validateAndAdjustBaseUrl(config.baseUrl);
    this.timeout = config.timeout || 30000; // 30 seconds default
  }

  private validateAndAdjustBaseUrl(baseUrl: string): string {
    // For production environments, ensure HTTPS is used
    if (process.env.NODE_ENV === 'production' && !baseUrl.startsWith('https://')) {
      console.warn('Production environment detected but API URL is not HTTPS. This may cause issues with CORS.');
      // In a real implementation, you might want to enforce HTTPS in production
      // For now, we'll just log a warning
    }

    return baseUrl;
  }

  // Check if the API connection is secure (HTTPS)
  private isSecureConnection(): boolean {
    return this.baseUrl.startsWith('https://');
  }

  // Regular API request (non-streaming)
  async ask(request: APIRequest): Promise<APIResponse> {
    try {
      // Validate request
      const queryValidation = validateQuery(request.query);
      if (!queryValidation.isValid) {
        throw new ChatbotError('validation', queryValidation.error || 'Invalid query');
      }

      const contextValidation = validateContext(request.context || '');
      if (!contextValidation.isValid) {
        throw new ChatbotError('validation', contextValidation.error || 'Invalid context');
      }

      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), this.timeout);

      const response = await fetch(`${this.baseUrl}/api/v1/ask`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        throw new ChatbotError('api', `HTTP ${response.status}: ${response.statusText}`, `HTTP_${response.status}`);
      }

      const data: APIResponse = await response.json();
      return data;
    } catch (error) {
      if (error.name === 'AbortError') {
        throw new ChatbotError('timeout', 'Request timed out', 'TIMEOUT_ERROR');
      }
      throw handleAPIError(error);
    }
  }

  // Streaming API request using Server-Sent Events
  async askStream(
    request: APIRequest,
    onChunk: (chunk: StreamChunk) => void,
    onError?: (error: ChatbotError) => void
  ): Promise<void> {
    // Use the fetch-based streaming implementation instead of EventSource
    // since EventSource doesn't properly support POST requests with bodies
    return this.askStreamWithFetch(request, onChunk, onError);
  }

  // Alternative streaming implementation using fetch with ReadableStream
  async askStreamWithFetch(
    request: APIRequest,
    onChunk: (chunk: StreamChunk) => void,
    onError?: (error: ChatbotError) => void
  ): Promise<void> {
    try {
      // Validate request
      const queryValidation = validateQuery(request.query);
      if (!queryValidation.isValid) {
        throw new ChatbotError('validation', queryValidation.error || 'Invalid query');
      }

      const contextValidation = validateContext(request.context || '');
      if (!contextValidation.isValid) {
        throw new ChatbotError('validation', contextValidation.error || 'Invalid context');
      }

      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), this.timeout);

      const response = await fetch(`${this.baseUrl}/api/v1/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        throw new ChatbotError('api', `HTTP ${response.status}: ${response.statusText}`, `HTTP_${response.status}`);
      }

      if (!response.body) {
        throw new ChatbotError('streaming', 'No response body', 'NO_BODY');
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      let buffer = '';

      try {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });

          // Process complete lines (SSE format)
          const lines = buffer.split('\n');
          buffer = lines.pop() || ''; // Keep last incomplete line in buffer

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const dataStr = line.slice(6); // Remove 'data: ' prefix
                if (dataStr.trim()) {
                  const chunk: StreamChunk = JSON.parse(dataStr);
                  onChunk(chunk);

                  if (chunk.type === 'done') {
                    reader.releaseLock();
                    return;
                  }
                }
              } catch (parseError) {
                const error = new ChatbotError('streaming', 'Failed to parse stream chunk', 'PARSE_ERROR', parseError);
                if (onError) onError(error);
                reader.releaseLock();
                throw error;
              }
            }
          }
        }
      } finally {
        reader.releaseLock();
      }
    } catch (error) {
      if (error.name === 'AbortError') {
        throw new ChatbotError('timeout', 'Stream request timed out', 'TIMEOUT_ERROR');
      }
      throw handleAPIError(error);
    }
  }

  // Health check to verify backend availability
  async healthCheck(): Promise<boolean> {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000); // 5 second timeout for health check

      const response = await fetch(`${this.baseUrl}/api/v1/health`, {
        method: 'GET',
        signal: controller.signal,
      });

      clearTimeout(timeoutId);
      return response.ok;
    } catch (error) {
      return false;
    }
  }
}

// Note: For POST requests with streaming, we'll rely on the fetch-based streaming implementation
// EventSource only supports GET requests, so we'll use the fetch-based approach for streaming