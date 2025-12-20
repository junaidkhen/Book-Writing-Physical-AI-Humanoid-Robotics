import React from 'react';
import { ChatbotProvider } from '../components/RAGChatbot/ChatbotContext';
import { TextSelectionProvider } from '../components/TextSelectionContext/TextSelectionProvider';
import ChatbotWidget from '../components/RAGChatbot/ChatbotWidget';

// Default wrapper for the entire Docusaurus site
const Root = ({ children }: { children: React.ReactNode }) => {
  return (
    <ChatbotProvider>
      <TextSelectionProvider>
        {children}
        <ChatbotWidget />
      </TextSelectionProvider>
    </ChatbotProvider>
  );
};

export default Root;