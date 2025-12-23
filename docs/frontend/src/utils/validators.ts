// Validation utilities for the RAG Chatbot
export const validateQuery = (query: string): { isValid: boolean; error?: string } => {
  if (!query || query.trim().length === 0) {
    return { isValid: false, error: 'Query cannot be empty' };
  }

  if (query.trim().length > 2000) {
    return { isValid: false, error: 'Query is too long. Maximum 2000 characters allowed.' };
  }

  return { isValid: true };
};

export const validateContext = (context: string): { isValid: boolean; error?: string } => {
  if (!context) {
    return { isValid: true }; // Context is optional
  }

  if (context.length > 5000) {
    return { isValid: false, error: 'Context is too long. Maximum 5000 characters allowed.' };
  }

  return { isValid: true };
};

export const validateMessage = (message: any): { isValid: boolean; error?: string } => {
  if (!message) {
    return { isValid: false, error: 'Message is required' };
  }

  if (typeof message !== 'object') {
    return { isValid: false, error: 'Message must be an object' };
  }

  if (!message.id || typeof message.id !== 'string') {
    return { isValid: false, error: 'Message must have a valid ID' };
  }

  if (!message.role || !['user', 'assistant'].includes(message.role)) {
    return { isValid: false, error: 'Message must have a valid role (user or assistant)' };
  }

  if (typeof message.content !== 'string') {
    return { isValid: false, error: 'Message content must be a string' };
  }

  return { isValid: true };
};

export const sanitizeQuery = (query: string): string => {
  // Remove excessive whitespace and normalize the query
  return query.trim().replace(/\s+/g, ' ');
};

export const truncateText = (text: string, maxLength: number): string => {
  if (text.length <= maxLength) {
    return text;
  }
  return text.substring(0, maxLength) + '...';
};

export const isValidURL = (url: string): boolean => {
  try {
    new URL(url);
    return true;
  } catch {
    return false;
  }
};