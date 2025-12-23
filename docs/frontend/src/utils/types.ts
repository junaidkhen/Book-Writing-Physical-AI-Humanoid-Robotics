// API Configuration Types
export interface APIConfiguration {
  baseUrl: string;
  timeout?: number;
  headers?: Record<string, string>;
}

export interface APIRequest {
  query: string;
  context?: string;
  selected_text?: string;
  stream?: boolean;
}

export interface APIResponse {
  response: string;
  citations?: Citation[];
  sources?: string[];
  timestamp: string;
}

// Data Model Types
export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  citations?: Citation[];
}

export interface Citation {
  id: string;
  title: string;
  url: string;
  text: string;
  page?: number;
  chapter?: string;
}

export interface ChatbotState {
  isOpen: boolean;
  messages: Message[];
  isLoading: boolean;
  error: string | null;
  selectedContext: string | null;
  streamingStatus: 'idle' | 'streaming' | 'paused' | 'cancelled';
}

export interface StreamChunk {
  type: 'content' | 'citation' | 'done' | 'error';
  data: any;
}