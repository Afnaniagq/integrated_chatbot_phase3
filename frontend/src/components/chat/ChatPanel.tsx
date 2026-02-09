"use client";

import React, { useState } from 'react';
import { useChat } from '@ai-sdk/react';
import MessageList from './MessageList';
import ChatInput from './ChatInput';
import { taskApi } from '../../services/task_api';

const useDashboardRefresh = () => {
  const refreshDashboard = () => {
    console.log('T012: 🔄 Triggering Dashboard Refresh Event');
    const event = new CustomEvent('refresh-dashboard');
    window.dispatchEvent(event);
  };
  return { refreshDashboard };
};

const ChatPanel: React.FC = () => {
  const { refreshDashboard } = useDashboardRefresh();
  const [isOpen, setIsOpen] = useState(false);

  const getAuthToken = () => {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('token') || '';
    }
    return '';
  };

  const { 
    messages, 
    input, 
    handleInputChange, 
    handleSubmit, 
    isLoading, 
    error 
  } = (useChat as any)({
    api: 'http://127.0.0.1:8000/api/chat',
    headers: {
      'Authorization': `Bearer ${getAuthToken()}`,
    },
    maxSteps: 5, 

    async onToolCall({ toolCall }: any) {
      // DEBUG: This alert WILL pop up if the AI correctly identifies the tool
      window.alert("🛠️ AI TOOL TRIGGERED: " + toolCall.toolName);
      console.log("🛠️ Tool Name:", toolCall.toolName, "Args:", toolCall.args);
      
      if (toolCall.toolName === 'create_task') {
        try {
          // 1. Send the request to your backend
          const response = await taskApi.createTask({
            title: toolCall.args.title,
            description: toolCall.args.description || "Added via AI Assistant",
            priority: toolCall.args.priority || "medium",
            category: "General"
          });
          
          console.log("✅ DB Response:", response);
          
          // 2. Refresh the UI
          refreshDashboard();
          
          return { 
            status: "success", 
            message: `Task "${toolCall.args.title}" created successfully!` 
          };
        } catch (err: any) {
          console.error("❌ DB ERROR:", err);
          return { 
            status: "error", 
            message: `Failed to create task: ${err.message}` 
          };
        }
      }
      
      if (toolCall.toolName === 'refresh_dashboard') {
        refreshDashboard();
        return { status: "success" };
      }
    },

    onFinish: (message: any) => {
      console.log("🏁 AI finished sequence:", message);
    },

    onError: (err: any) => {
      console.error("🚨 Chat Connection Error:", err);
    }
  });

  if (!isOpen) {
    return (
      <button 
        onClick={() => setIsOpen(true)}
        className="fixed z-[9999] flex items-center gap-2 p-4 text-white transition-all bg-blue-600 rounded-full shadow-2xl bottom-6 right-6 hover:bg-blue-700 group"
      >
        <span className="overflow-hidden transition-all duration-300 max-w-0 group-hover:max-w-xs">Ask AI</span>
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m3 21 1.9-5.7a8.5 8.5 0 1 1 3.8 3.8z"/></svg>
      </button>
    );
  }

  return (
    <div className="fixed bottom-6 right-6 w-[380px] h-[550px] bg-white border border-gray-200 rounded-2xl shadow-2xl flex flex-col overflow-hidden z-[9999] animate-in fade-in slide-in-from-bottom-4">
      <div className="flex items-center justify-between p-4 text-white bg-blue-600">
        <div className="flex flex-col">
          <h3 className="text-lg font-semibold">AI Assistant</h3>
          <p className="text-xs opacity-80">Connected to Backend</p>
        </div>
        <button onClick={() => setIsOpen(false)} className="p-1 rounded hover:bg-blue-700">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>
        </button>
      </div>

      <div className="flex-1 overflow-y-auto bg-gray-50">
        <MessageList messages={messages} isLoading={isLoading} />
      </div>

      <div className="p-3 bg-white border-t border-gray-100">
        <ChatInput 
          input={input} 
          handleInputChange={handleInputChange} 
          handleSubmit={handleSubmit} 
        />
        {error && <p className="mt-1 text-xs text-center text-red-500">Connection error. Is Python running?</p>}
      </div>
    </div>
  );
};

export default ChatPanel;