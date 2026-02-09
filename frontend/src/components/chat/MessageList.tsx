import React, { useRef, useEffect } from 'react';
// Assuming Message type is exported from @openai/chatkit-react, or define it locally
interface Message {
  id?: string; // Optional ID for key
  role: 'user' | 'assistant';
  content: string;
}

import ChatMessage from './ChatMessage';
import ThinkingIndicator from './ThinkingIndicator';

interface MessageListProps {
  messages: Message[]; // Array of message objects
  isLoading: boolean; // Indicates if AI is currently thinking/loading
}

const MessageList: React.FC<MessageListProps> = ({ messages, isLoading }) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]); // Scroll to bottom when messages or loading status changes

  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-4">
      {messages.length > 0 ? (
        messages.map((message, index) => (
          <ChatMessage key={message.id || index} message={message} /> // Use message.id if available for key
        ))
      ) : (
        <p className="text-gray-400 text-center">Start a conversation...</p>
      )}
      {isLoading && <ThinkingIndicator />}
      <div ref={messagesEndRef} /> {/* Element to scroll to */}
    </div>
  );
};

export default MessageList;
