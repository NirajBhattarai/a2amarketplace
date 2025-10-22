'use client';

import { useState } from 'react';
import { AgentChat } from '../components/AgentChat';
import { AgentSelector } from '../components/AgentSelector';
import { ServerStatus } from '../components/ServerStatus';
import { AgentSettings } from '../components/AgentSettings';
import { PaymentInterface } from '../components/PaymentInterface';

export default function Home() {
  const [activeTab, setActiveTab] = useState<'chat' | 'status' | 'settings' | 'payments'>('chat');
  const [paymentMessage, setPaymentMessage] = useState<string>('');

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-8">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-4">
            🤖 A2A Agent Interface
          </h1>
          <p className="text-lg text-gray-600 max-w-4xl mx-auto">
            Complete app→client→server architecture implementation. 
            Interact with TellTimeAgent, GreetingAgent, CarbonCreditAgent, WalletBalanceAgent, PaymentAgent, and OrchestratorAgent through the A2A protocol.
            Select an agent, monitor server status, and configure connections. Execute real blockchain transactions across Hedera, Ethereum, and Polygon networks.
          </p>
        </div>

        {/* Navigation Tabs */}
        <div className="max-w-6xl mx-auto mb-6">
          <div className="flex justify-center space-x-1 bg-white rounded-lg p-1 shadow-lg">
            <button
              onClick={() => setActiveTab('chat')}
              className={`px-6 py-2 rounded-md transition-colors ${
                activeTab === 'chat'
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-600 hover:text-gray-800'
              }`}
            >
              💬 Chat
            </button>
            <button
              onClick={() => setActiveTab('status')}
              className={`px-6 py-2 rounded-md transition-colors ${
                activeTab === 'status'
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-600 hover:text-gray-800'
              }`}
            >
              📊 Status
            </button>
            <button
              onClick={() => setActiveTab('settings')}
              className={`px-6 py-2 rounded-md transition-colors ${
                activeTab === 'settings'
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-600 hover:text-gray-800'
              }`}
            >
              ⚙️ Settings
            </button>
            <button
              onClick={() => setActiveTab('payments')}
              className={`px-6 py-2 rounded-md transition-colors ${
                activeTab === 'payments'
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-600 hover:text-gray-800'
              }`}
            >
              💰 Payments
            </button>
          </div>
        </div>

        {/* Tab Content */}
        <div className="max-w-6xl mx-auto">
          {activeTab === 'chat' && (
            <div className="max-w-4xl mx-auto">
              <AgentChat externalMessage={paymentMessage} />
            </div>
          )}

          {activeTab === 'status' && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <ServerStatus />
              <AgentSelector
                selectedAgent={null}
                onAgentSelect={() => {}}
              />
            </div>
          )}

          {activeTab === 'settings' && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <AgentSettings />
              <div className="bg-white rounded-lg shadow-lg p-6">
                <h3 className="text-lg font-semibold text-gray-800 mb-4">Architecture Overview</h3>
                <div className="space-y-4 text-sm text-gray-600">
                  <div className="p-3 bg-blue-50 rounded-lg">
                    <h4 className="font-medium text-blue-800 mb-2">App Layer (Web UI)</h4>
                    <p>React components handling user interactions, agent selection, and message display.</p>
                  </div>
                  <div className="p-3 bg-green-50 rounded-lg">
                    <h4 className="font-medium text-green-800 mb-2">Client Layer (A2AClient)</h4>
                    <p>TypeScript service managing JSON-RPC communication with A2A agents.</p>
                  </div>
                  <div className="p-3 bg-purple-50 rounded-lg">
                    <h4 className="font-medium text-purple-800 mb-2">Server Layer (A2A Backend)</h4>
                    <p>Python agents running on different ports, handling task processing.</p>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'payments' && (
            <div className="max-w-4xl mx-auto">
              <PaymentInterface onSendMessage={(message) => {
                setPaymentMessage(message);
                setActiveTab('chat'); // Switch to chat tab to show the message
                // Clear the message after a short delay to prevent re-sending
                setTimeout(() => setPaymentMessage(''), 100);
              }} />
            </div>
          )}
        </div>
      </div>
    </main>
  );
}