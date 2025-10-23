'use client';

import { useState } from 'react';
import { AgentChat } from '../components/AgentChat';
import '../styles/modern-chat.css';

export default function Home() {
  return (
    <main className="min-h-screen modern-bg">
      <div className="flex h-screen">
        {/* Left Sidebar - Agent Registration */}
        <div className="w-80 glass-sidebar flex flex-col shadow-floating">
          {/* Enhanced Agent Registration Header */}
          <div className="p-6 border-b border-white/20 relative overflow-hidden">
            {/* Background decoration */}
            <div className="absolute top-0 right-0 w-20 h-20 bg-gradient-to-bl from-white/10 to-transparent rounded-full -translate-y-10 translate-x-10"></div>
            
            <div className="flex items-center space-x-4 mb-4 relative z-10">
              <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-500 rounded-xl flex items-center justify-center shadow-floating floating">
                <span className="text-white text-xl">🤖</span>
              </div>
                <div>
                  <h1 className="text-xl font-bold text-white">Agent Registry</h1>
                  <p className="text-xs text-white/90">Active A2A Agents</p>
                  <div className="flex items-center space-x-2 mt-1">
                    <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                    <span className="text-xs text-white/80">All Systems Operational</span>
                  </div>
                </div>
            </div>
          </div>
          
          {/* Agent List */}
          <div className="flex-1 p-4 space-y-3 modern-scrollbar overflow-y-auto">
            <div className="flex items-center space-x-3 p-4 glass-card rounded-xl hover-lift hover-glow">
              <div className="agent-status w-3 h-3 bg-green-400 rounded-full"></div>
              <div className="flex-1">
                <div className="font-medium text-gray-900">Time Agent</div>
                <div className="text-xs text-gray-600">TellTimeAgent</div>
              </div>
            </div>
            
            <div className="flex items-center space-x-3 p-4 glass-card rounded-xl hover-lift hover-glow">
              <div className="agent-status w-3 h-3 bg-green-400 rounded-full"></div>
              <div className="flex-1">
                <div className="font-medium text-gray-900">Wallet Agent</div>
                <div className="text-xs text-gray-600">WalletBalanceAgent</div>
              </div>
            </div>

            <div className="flex items-center space-x-3 p-4 glass-card rounded-xl hover-lift hover-glow">
              <div className="agent-status w-3 h-3 bg-green-400 rounded-full"></div>
              <div className="flex-1">
                <div className="font-medium text-gray-900">Carbon Agent</div>
                <div className="text-xs text-gray-600">CarbonCreditAgent</div>
              </div>
            </div>

            <div className="flex items-center space-x-3 p-4 glass-card rounded-xl hover-lift hover-glow">
              <div className="agent-status w-3 h-3 bg-green-400 rounded-full"></div>
              <div className="flex-1">
                <div className="font-medium text-gray-900">Payment Agent</div>
                <div className="text-xs text-gray-600">PaymentAgent</div>
              </div>
            </div>

            <div className="flex items-center space-x-3 p-4 glass-card rounded-xl hover-lift hover-glow">
              <div className="agent-status w-3 h-3 bg-green-400 rounded-full"></div>
              <div className="flex-1">
                <div className="font-medium text-gray-900">IoT Carbon Agent</div>
                <div className="text-xs text-gray-600">IoTCarbonAgent</div>
              </div>
            </div>
          </div>
        </div>

        {/* Main Content Area - Chat Section */}
        <div className="flex-1 flex flex-col chat-bg">
          {/* Enhanced Chat Header */}
          <div className="p-6 border-b border-white/20 glass-card header-decoration relative overflow-hidden">
            {/* Background overlay for better text contrast */}
            <div className="absolute inset-0 bg-black/20 backdrop-blur-sm"></div>
            {/* Background decoration */}
            <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-white/10 to-transparent rounded-full -translate-y-16 translate-x-16"></div>
            <div className="absolute bottom-0 left-0 w-24 h-24 bg-gradient-to-tr from-white/5 to-transparent rounded-full translate-y-12 -translate-x-12"></div>
            
            <div className="flex items-center justify-between relative z-10">
              <div className="flex items-center space-x-4">
                <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-500 rounded-xl flex items-center justify-center shadow-floating floating header-icon">
                  <span className="text-2xl">🌱</span>
                </div>
                <div>
                  <h2 className="text-3xl font-bold text-white mb-1 header-text">Carbon Credit Marketplace</h2>
                  <p className="text-white text-sm header-subtitle">Multi-Agent A2A Communication Platform</p>
                  <div className="flex items-center space-x-2 mt-2">
                    <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                    <span className="text-xs text-white header-small">Real-time AI Agents</span>
                  </div>
                </div>
              </div>
              
              <div className="flex items-center space-x-4">
                <div className="status-indicator">
                  <div className="status-dot bg-green-400"></div>
                  <span className="text-sm text-white/90 font-medium">System Online</span>
                </div>
                <div className="status-indicator">
                  <div className="status-dot bg-blue-400"></div>
                  <span className="text-sm text-white/90 font-medium">6 Agents Active</span>
                </div>
                <div className="status-indicator">
                  <div className="status-dot bg-purple-400"></div>
                  <span className="text-sm text-white/90 font-medium">IoT Connected</span>
                </div>
              </div>
            </div>
          </div>

          {/* Chat Area */}
          <div className="flex-1 flex flex-col">
            <AgentChat />
          </div>

          {/* Suggestions - Above Ask Prompt */}
          <div className="p-4 glass-card border-t border-white/20">
            <div className="mb-4">
              <h3 className="text-sm font-medium text-white mb-3">💡 Quick Suggestions</h3>
              <div className="flex flex-wrap gap-2">
                <button
                  onClick={() => {
                    const event = new CustomEvent('sendMessage', { detail: 'What time is it?' });
                    window.dispatchEvent(event);
                  }}
                  className="suggestion-pill time modern-btn"
                >
                  🕐 What time it is
                </button>
                <button
                  onClick={() => {
                    const event = new CustomEvent('sendMessage', { detail: 'Buy 10 carbon credits' });
                    window.dispatchEvent(event);
                  }}
                  className="suggestion-pill carbon modern-btn"
                >
                  🌱 Buy 10 carbon credit
                </button>
                <button
                  onClick={() => {
                    const event = new CustomEvent('sendMessage', { detail: 'Show current IoT device data' });
                    window.dispatchEvent(event);
                  }}
                  className="suggestion-pill iot modern-btn"
                >
                  📡 IoT Device Status
                </button>
                <button
                  onClick={() => {
                    const event = new CustomEvent('sendMessage', { detail: 'Predict carbon credits for next 24 hours' });
                    window.dispatchEvent(event);
                  }}
                  className="suggestion-pill forecast modern-btn"
                >
                  📊 Carbon Forecast
                </button>
                <button
                  onClick={() => {
                    const event = new CustomEvent('sendMessage', { detail: 'List automation rules' });
                    window.dispatchEvent(event);
                  }}
                  className="suggestion-pill automation modern-btn"
                >
                  🤖 Automation Rules
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}