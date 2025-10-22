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
    <div className="flex flex-col h-full bg-gradient-to-br from-gray-50 to-white">
      {/* Enhanced Chat Header */}
      <div className="p-6 border-b border-gray-200 bg-gradient-to-r from-blue-50 to-indigo-50">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="relative">
              <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-indigo-500 rounded-full flex items-center justify-center">
                <span className="text-white text-sm">🤖</span>
              </div>
              <div className="absolute -top-1 -right-1 w-3 h-3 bg-green-400 rounded-full animate-pulse"></div>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900">A2A Agent Chat</h3>
              <p className="text-xs text-gray-600">Real-time communication</p>
            </div>
          </div>
          {conversationHistory.length > 0 && (
            <button
              onClick={() => setShowHistory(!showHistory)}
              className="px-4 py-2 text-sm bg-white/80 backdrop-blur-sm text-blue-700 rounded-full hover:bg-white hover:shadow-md transition-all duration-200 border border-blue-200"
            >
              <span className="flex items-center space-x-2">
                <span>📚</span>
                <span>{showHistory ? 'Hide' : 'Show'} History</span>
                <span className="bg-blue-100 text-blue-600 px-2 py-0.5 rounded-full text-xs">
                  {conversationHistory.length}
                </span>
              </span>
            </button>
          )}
        </div>
      </div>

      {/* Enhanced Conversation History Panel */}
      {showHistory && conversationHistory.length > 0 && (
        <div className="p-4 bg-gradient-to-r from-gray-50 to-blue-50 border-b border-gray-200 max-h-40 overflow-y-auto">
          <div className="flex items-center space-x-2 mb-3">
            <span className="text-lg">📚</span>
            <h4 className="text-sm font-semibold text-gray-800">Conversation History</h4>
            <span className="bg-blue-100 text-blue-600 px-2 py-0.5 rounded-full text-xs">
              {conversationHistory.length} messages
            </span>
          </div>
          <div className="space-y-3">
            {conversationHistory.map((item: ConversationItem, index: number) => (
              <div key={index} className="flex items-start space-x-3 p-2 bg-white/60 rounded-lg border border-gray-200">
                <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs ${
                  item.role === 'user' ? 'bg-blue-100 text-blue-600' : 'bg-green-100 text-green-600'
                }`}>
                  {item.role === 'user' ? '👤' : '🤖'}
                </div>
                <div className="flex-1">
                  <div className="text-xs font-medium text-gray-700 mb-1">
                    {item.role === 'user' ? 'User' : 'Agent'}
                  </div>
                  <div className="text-xs text-gray-600 leading-relaxed">
                    {item.parts?.filter((part: ConversationPart) => part.type === 'text').map((part: ConversationPart) => part.text).join(' ') || 'No content'}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-center py-12">
            <div className="relative mb-6">
              <div className="w-16 h-16 bg-gradient-to-r from-blue-500 to-indigo-500 rounded-full flex items-center justify-center mx-auto shadow-lg">
                <span className="text-2xl">🤖</span>
              </div>
              <div className="absolute -top-2 -right-2 w-6 h-6 bg-green-400 rounded-full animate-pulse"></div>
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-3">Welcome to A2A Agent Chat</h3>
            <p className="text-gray-600 mb-6">Use the Quick Actions on the right to start a conversation</p>
            <div className="flex items-center justify-center space-x-4 text-sm text-gray-500">
              <div className="flex items-center space-x-1">
                <div className="w-2 h-2 bg-green-400 rounded-full"></div>
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
            <div className={`max-w-xs lg:max-w-md px-4 py-3 rounded-2xl shadow-sm ${
              message.role === 'user'
                ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white'
                : 'bg-white border border-gray-200 text-gray-800'
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
            <div className="bg-white border border-gray-200 text-gray-800 px-4 py-3 rounded-2xl shadow-sm">
              <div className="flex items-center space-x-3">
                <div className="w-6 h-6 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-xs">
                  🤖
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                  <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  <span className="text-sm text-gray-600">Agent is thinking...</span>
                </div>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Enhanced Input Area */}
      <form onSubmit={handleSubmit} className="p-6 bg-gradient-to-r from-gray-50 to-blue-50 border-t border-gray-200">
        <div className="flex items-end space-x-4 max-w-4xl mx-auto">
          <div className="flex-1 relative">
            <div className="relative">
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleSubmit(e);
                  }
                }}
                placeholder="Message A2A Agent..."
                className="w-full px-6 py-4 pr-16 border border-gray-300 rounded-2xl resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 bg-white shadow-sm"
                disabled={isLoading}
                rows={1}
                style={{ minHeight: '48px', maxHeight: '120px' }}
                onInput={(e) => {
                  const target = e.target as HTMLTextAreaElement;
                  target.style.height = 'auto';
                  target.style.height = Math.min(target.scrollHeight, 120) + 'px';
                }}
              />
              <div className="absolute right-4 bottom-4 flex items-center space-x-2">
                <span className="text-gray-400 text-sm">↵</span>
                <div className="w-1 h-1 bg-gray-300 rounded-full"></div>
              </div>
            </div>
          </div>
          <button
            type="submit"
            disabled={isLoading || !input.trim()}
            className="flex items-center justify-center w-12 h-12 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-full hover:from-blue-700 hover:to-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 shadow-lg hover:shadow-xl transform hover:scale-105"
          >
            {isLoading ? (
              <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
            ) : (
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
            )}
          </button>
        </div>
        {isLoading && (
          <div className="mt-4 text-center">
            <div className="inline-flex items-center space-x-3 text-sm text-gray-600 bg-white/80 px-4 py-2 rounded-full">
              <div className="flex space-x-1">
                <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
              </div>
            </div>
          </div>
        )}
      </form>
    </div>
  );
}