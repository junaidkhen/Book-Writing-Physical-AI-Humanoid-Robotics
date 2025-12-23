// Error handling utilities for the RAG Chatbot
export class ChatbotError extends Error {
  public type: 'network' | 'validation' | 'api' | 'streaming' | 'timeout';
  public code?: string;
  public details?: any;
  public timestamp: Date;

  constructor(
    type: 'network' | 'validation' | 'api' | 'streaming' | 'timeout',
    message: string,
    code?: string,
    details?: any
  ) {
    super(message);
    this.type = type;
    this.code = code;
    this.details = details;
    this.timestamp = new Date();
    this.name = 'ChatbotError';
  }
}

export const handleAPIError = (error: any): ChatbotError => {
  if (error instanceof ChatbotError) {
    return error;
  }

  // Network errors
  if (error.name === 'TypeError' && error.message.includes('fetch')) {
    return new ChatbotError('network', 'Unable to connect to the API. Please check your connection.', 'NETWORK_ERROR');
  }

  // HTTP errors
  if (error.status) {
    switch (error.status) {
      case 400:
        return new ChatbotError('validation', 'Invalid request parameters.', 'VALIDATION_ERROR', error.body);
      case 401:
        return new ChatbotError('api', 'Authentication required. Please contact the administrator.', 'UNAUTHORIZED');
      case 403:
        return new ChatbotError('api', 'Access forbidden. You do not have permission to perform this action.', 'FORBIDDEN');
      case 404:
        return new ChatbotError('api', 'The requested resource was not found.', 'NOT_FOUND');
      case 429:
        return new ChatbotError('api', 'Rate limit exceeded. Please try again later.', 'RATE_LIMIT');
      case 500:
        return new ChatbotError('api', 'Internal server error. Please try again later.', 'INTERNAL_ERROR');
      case 502:
        return new ChatbotError('api', 'Gateway error. The server is temporarily unavailable.', 'GATEWAY_ERROR');
      case 503:
        return new ChatbotError('api', 'Service unavailable. Please try again later.', 'SERVICE_UNAVAILABLE');
      default:
        return new ChatbotError('api', `API error: ${error.status}`, `HTTP_${error.status}`, error.body);
    }
  }

  // Generic error
  return new ChatbotError('api', error.message || 'An unknown error occurred', 'UNKNOWN_ERROR', error);
};

export const formatErrorMessage = (error: ChatbotError): string => {
  switch (error.type) {
    case 'network':
      return 'Network error: Unable to connect to the server. Please check your internet connection.';
    case 'validation':
      return 'Validation error: The request contains invalid data. Please check your input.';
    case 'api':
      return `API error: ${error.message}`;
    case 'streaming':
      return `Streaming error: ${error.message}`;
    case 'timeout':
      return 'Request timeout: The server took too long to respond. Please try again.';
    default:
      return `Error: ${error.message}`;
  }
};