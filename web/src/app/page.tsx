'use client';

import { useState } from 'react';
import { AgentChat } from '../components/AgentChat';
import { ServerStatus } from '../components/ServerStatus';
import { AgentSettings } from '../components/AgentSettings';

export default function Home() {
  const [activeTab] = useState<'chat' | 'status' | 'settings'>('chat');

  return (
    <main className="min-h-screen bg-white">
      <div className="flex h-screen">
        {/* Left Sidebar - Chat Interface */}
        <div className="w-1/3 border-r border-gray-200 flex flex-col">
          {/* Chat Header */}
          <div className="p-6 border-b border-gray-200">
            <h1 className="text-2xl font-bold text-gray-900 mb-2">A2A Agent Interface</h1>
            <p className="text-sm text-gray-600 mb-1">Multi-Agent A2A Demo: 6 Specialized Agents</p>
            <p className="text-sm text-gray-600">Orchestrator-mediated A2A Protocol</p>
          </div>
          
          {/* Chat Area */}
          <div className="flex-1 flex flex-col">
            <AgentChat />
          </div>
        </div>

        {/* Right Content Area */}
        <div className="flex-1 flex flex-col">
          {/* Agents Section - Always at top */}
          <div className="p-4 border-b border-gray-200">
            <h2 className="text-lg font-bold text-gray-900 mb-3">Available Agents</h2>
            <div className="flex flex-wrap gap-3">
              <div className="p-3 bg-blue-50 rounded-lg border border-blue-200 min-w-0 flex-shrink-0">
                <div className="text-xs font-medium text-blue-900">TellTimeAgent</div>
                <div className="text-xs text-blue-600">Time queries</div>
              </div>
              <div className="p-3 bg-green-50 rounded-lg border border-green-200 min-w-0 flex-shrink-0">
                <div className="text-xs font-medium text-green-900">GreetingAgent</div>
                <div className="text-xs text-green-600">Friendly greetings</div>
              </div>
              <div className="p-3 bg-purple-50 rounded-lg border border-purple-200 min-w-0 flex-shrink-0">
                <div className="text-xs font-medium text-purple-900">CarbonCreditAgent</div>
                <div className="text-xs text-purple-600">Carbon credit trading</div>
              </div>
              <div className="p-3 bg-orange-50 rounded-lg border border-orange-200 min-w-0 flex-shrink-0">
                <div className="text-xs font-medium text-orange-900">WalletBalanceAgent</div>
                <div className="text-xs text-orange-600">Balance queries</div>
              </div>
              <div className="p-3 bg-red-50 rounded-lg border border-red-200 min-w-0 flex-shrink-0">
                <div className="text-xs font-medium text-red-900">PaymentAgent</div>
                <div className="text-xs text-red-600">Blockchain payments</div>
              </div>
              <div className="p-3 bg-indigo-50 rounded-lg border border-indigo-200 min-w-0 flex-shrink-0">
                <div className="text-xs font-medium text-indigo-900">OrchestratorAgent</div>
                <div className="text-xs text-indigo-600">Coordination hub</div>
              </div>
            </div>
          </div>

          {/* Enhanced Quick Actions Section */}
          <div className="flex-1 p-6 bg-gradient-to-br from-gray-50 to-blue-50">
            <div className="mb-6">
              <div className="flex items-center space-x-3 mb-2">
                <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-indigo-500 rounded-full flex items-center justify-center">
                  <span className="text-white text-sm">⚡</span>
                </div>
                <div>
                  <h3 className="text-xl font-semibold text-gray-900">Quick Actions</h3>
                  <p className="text-sm text-gray-600">Click any action to start a conversation</p>
                </div>
              </div>
            </div>
            
            <div className="grid grid-cols-1 gap-4">
              {[
                { message: "What time is it?", icon: "🕐", category: "general", description: "Get current time" },
                { message: "Hello there!", icon: "👋", category: "general", description: "Friendly greeting" },
                { message: "Check my wallet balance", icon: "💰", category: "wallet", description: "View account balance" },
                { message: "Tell me about carbon credits", icon: "🌱", category: "carbon", description: "Learn about trading" },
                { message: "Send 0.001 HBAR to account 0.0.123456", icon: "💸", category: "payment", description: "Blockchain transfer" },
                { message: "Find 100 carbon credits at best price", icon: "🔍", category: "carbon", description: "Market search" }
              ].map((action, index) => (
                <button
                  key={index}
                  onClick={() => {
                    const event = new CustomEvent('sendMessage', { detail: action.message });
                    window.dispatchEvent(event);
                  }}
                  className={`group flex items-center space-x-4 p-4 text-left rounded-xl transition-all duration-200 hover:shadow-md hover:scale-[1.02] ${
                    action.category === 'payment' 
                      ? 'bg-gradient-to-r from-red-50 to-pink-50 hover:from-red-100 hover:to-pink-100 border border-red-200' 
                      : action.category === 'wallet'
                      ? 'bg-gradient-to-r from-green-50 to-emerald-50 hover:from-green-100 hover:to-emerald-100 border border-green-200'
                      : action.category === 'carbon'
                      ? 'bg-gradient-to-r from-blue-50 to-cyan-50 hover:from-blue-100 hover:to-cyan-100 border border-blue-200'
                      : 'bg-gradient-to-r from-gray-50 to-slate-50 hover:from-gray-100 hover:to-slate-100 border border-gray-200'
                  }`}
                >
                  <div className={`w-12 h-12 rounded-xl flex items-center justify-center text-xl transition-transform duration-200 group-hover:scale-110 ${
                    action.category === 'payment' 
                      ? 'bg-red-100 text-red-600' 
                      : action.category === 'wallet'
                      ? 'bg-green-100 text-green-600'
                      : action.category === 'carbon'
                      ? 'bg-blue-100 text-blue-600'
                      : 'bg-gray-100 text-gray-600'
                  }`}>
                    {action.icon}
                  </div>
                  <div className="flex-1">
                    <div className={`text-sm font-semibold mb-1 ${
                      action.category === 'payment' 
                        ? 'text-red-700' 
                        : action.category === 'wallet'
                        ? 'text-green-700'
                        : action.category === 'carbon'
                        ? 'text-blue-700'
                        : 'text-gray-700'
                    }`}>
                      {action.message}
                    </div>
                    <div className={`text-xs ${
                      action.category === 'payment' 
                        ? 'text-red-600' 
                        : action.category === 'wallet'
                        ? 'text-green-600'
                        : action.category === 'carbon'
                        ? 'text-blue-600'
                        : 'text-gray-600'
                    }`}>
                      {action.description}
                    </div>
                  </div>
                  <div className={`w-6 h-6 rounded-full flex items-center justify-center transition-all duration-200 group-hover:scale-110 ${
                    action.category === 'payment' 
                      ? 'bg-red-200 text-red-600' 
                      : action.category === 'wallet'
                      ? 'bg-green-200 text-green-600'
                      : action.category === 'carbon'
                      ? 'bg-blue-200 text-blue-600'
                      : 'bg-gray-200 text-gray-600'
                  }`}>
                    <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                    </svg>
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* Tab Content for other sections */}
          {activeTab === 'status' && (
            <div className="flex-1 p-6">
              <ServerStatus />
            </div>
          )}
          {activeTab === 'settings' && (
            <div className="flex-1 p-6">
              <AgentSettings />
            </div>
          )}
        </div>
      </div>
    </main>
  );
}