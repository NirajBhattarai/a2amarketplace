'use client';

import { useState, useRef, useEffect, useCallback } from 'react';

interface Message {
  id: string;
  content: string;
  role: 'user' | 'agent';
  timestamp: Date;
}

interface ConversationPart {
  type: string;
  text: string;
}

interface ConversationItem {
  role: string;
  parts?: ConversationPart[];
}

// eslint-disable-next-line @typescript-eslint/no-empty-object-type
interface AgentChatProps {
  // No props needed for now, but interface is required for future extensibility
}

export function AgentChat({}: AgentChatProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId] = useState(() => Math.random().toString(36).substring(2, 15));
  const [showHistory, setShowHistory] = useState(false);
  const [conversationHistory, setConversationHistory] = useState<ConversationItem[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = useCallback(async (message: string) => {
    if (!message.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      content: message,
      role: 'user',
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      console.log('📤 Sending message:', message);
      console.log('📤 Session ID:', sessionId);
      
      const response = await fetch('/api/agent', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: message,
          sessionId: sessionId,
        }),
      });

      console.log('📥 Response status:', response.status);
      console.log('📥 Response ok:', response.ok);

      if (!response.ok) {
        const errorText = await response.text();
        console.error('📥 Error response:', errorText);
        throw new Error(`Failed to send message: ${response.status} - ${errorText}`);
      }

      const data = await response.json();
      console.log('📥 API Response:', data);
      
      // Handle conversation history if available
      if (data.history && Array.isArray(data.history)) {
        console.log('📚 Conversation History:', data.history);
        
        // Store the raw history for the history viewer
        setConversationHistory(data.history);
        
        // Convert history to messages format
        const historyMessages: Message[] = data.history.map((item: ConversationItem, index: number) => ({
          id: `history-${index}`,
          content: item.parts?.filter((part: ConversationPart) => part.type === 'text').map((part: ConversationPart) => part.text).join(' ') || '',
          role: item.role === 'user' ? 'user' : 'agent',
          timestamp: new Date(),
        }));
        
        // Replace messages with the full conversation history
        setMessages(historyMessages);
      } else {
        // Fallback to single response
        const agentMessage: Message = {
          id: (Date.now() + 1).toString(),
          content: data.response || data.data?.response || 'No response received',
          role: 'agent',
          timestamp: new Date(),
        };

        setMessages(prev => [...prev, agentMessage]);
      }
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: 'Sorry, I encountered an error. Please try again.',
        role: 'agent',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  }, [isLoading, sessionId]);

  useEffect(() => {
    // Listen for messages from the right side quick actions
    const handleExternalMessage = (event: CustomEvent) => {
      sendMessage(event.detail);
    };

    window.addEventListener('sendMessage', handleExternalMessage as EventListener);
    
    return () => {
      window.removeEventListener('sendMessage', handleExternalMessage as EventListener);
    };
  }, [sendMessage]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    sendMessage(input);
  };


  return (
    <div className="flex flex-col h-full">
      {/* Chat Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 modern-scrollbar">
        {messages.length === 0 && (
          <div className="text-center py-12">
            <div className="relative mb-6">
              <div className="w-20 h-20 bg-gradient-to-r from-blue-500 to-indigo-500 rounded-full flex items-center justify-center mx-auto shadow-floating floating">
                <span className="text-3xl">🤖</span>
              </div>
              <div className="absolute -top-2 -right-2 w-6 h-6 bg-green-400 rounded-full animate-pulse"></div>
            </div>
            <h3 className="text-2xl font-semibold gradient-text mb-3">Welcome to A2A Agent Chat</h3>
            <p className="text-white/80 mb-6">Use the suggestions below to start a conversation</p>
            <div className="flex items-center justify-center space-x-4 text-sm text-white/70">
              <div className="flex items-center space-x-1">
                <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                <span>Online</span>
              </div>
              <div className="flex items-center space-x-1">
                <div className="w-2 h-2 bg-blue-400 rounded-full"></div>
                <span>Ready</span>
              </div>
            </div>
          </div>
        )}

        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'} mb-4`}
          >
            <div className={`message-bubble ${
              message.role === 'user' ? 'message-user' : 'message-agent'
            }`}>
              <div className="flex items-start space-x-2">
                <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs flex-shrink-0 ${
                  message.role === 'user' ? 'bg-white/20' : 'bg-blue-100 text-blue-600'
                }`}>
                  {message.role === 'user' ? '👤' : '🤖'}
                </div>
                <div className="flex-1">
                  <p className="text-sm leading-relaxed">{message.content}</p>
                  <p className={`text-xs mt-1 ${
                    message.role === 'user' ? 'text-blue-100' : 'text-gray-500'
                  }`}>
                    {message.timestamp.toLocaleTimeString()}
                  </p>
                </div>
              </div>
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="flex justify-start">
            <div className="glass-card text-white px-4 py-3 rounded-2xl shadow-modern">
              <div className="flex items-center space-x-3">
                <div className="w-6 h-6 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-xs">
                  🤖
                </div>
                <div className="typing-indicator">
                  <div className="typing-dot"></div>
                  <div className="typing-dot"></div>
                  <div className="typing-dot"></div>
                  <span className="text-sm text-white/80 ml-2">Agent is thinking...</span>
                </div>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>


      {/* Input Area */}
      <form onSubmit={handleSubmit} className="p-4 glass-card border-t border-white/20">
        <div className="flex items-end space-x-3">
          <div className="flex-1 relative">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSubmit(e);
                }
              }}
              placeholder="Ask prompt..."
              className="modern-input w-full px-4 py-3 rounded-xl resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200"
              disabled={isLoading}
              rows={1}
              style={{ minHeight: '44px', maxHeight: '120px' }}
              onInput={(e) => {
                const target = e.target as HTMLTextAreaElement;
                target.style.height = 'auto';
                target.style.height = Math.min(target.scrollHeight, 120) + 'px';
              }}
            />
          </div>
          <button
            type="submit"
            disabled={isLoading || !input.trim()}
            className="modern-btn flex items-center justify-center w-12 h-12 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-xl hover:from-blue-700 hover:to-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 shadow-modern hover:shadow-floating"
          >
            {isLoading ? (
              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
            ) : (
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
            )}
          </button>
        </div>
      </form>
    </div>
  );
}