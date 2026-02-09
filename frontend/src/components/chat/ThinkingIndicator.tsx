import React from 'react';

const ThinkingIndicator: React.FC = () => {
  return (
    <div className="flex justify-start">
      <div className="max-w-[70%] p-2 rounded-lg bg-gray-200 text-gray-800 self-start">
        <div className="flex space-x-1">
          <span className="sr-only">AI is thinking</span>
          <div className="h-2 w-2 bg-gray-500 rounded-full animate-bounce [animation-delay:-0.3s]"></div>
          <div className="h-2 w-2 bg-gray-500 rounded-full animate-bounce [animation-delay:-0.15s]"></div>
          <div className="h-2 w-2 bg-gray-500 rounded-full animate-bounce"></div>
        </div>
      </div>
    </div>
  );
};

export default ThinkingIndicator;
