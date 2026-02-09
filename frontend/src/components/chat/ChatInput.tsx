import React from 'react';

interface ChatInputProps {
  input: string;
  handleInputChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  handleSubmit: (e: React.FormEvent<HTMLFormElement>) => void;
}

const ChatInput: React.FC<ChatInputProps> = ({ input, handleInputChange, handleSubmit }) => {
  return (
    <form onSubmit={handleSubmit} className="p-4 border-t border-gray-200 bg-gray-50 flex items-center">
      <input
        type="text"
        placeholder="Type your message..."
        className="flex-1 p-2 border border-gray-300 rounded-l-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        value={input}
        onChange={handleInputChange}
      />
      <button
        type="submit"
        className="bg-blue-500 hover:bg-blue-600 text-white p-2 rounded-r-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50"
      >
        Send
      </button>
    </form>
  );
};

export default ChatInput;
