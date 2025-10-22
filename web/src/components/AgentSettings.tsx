'use client';

import { useState } from 'react';

interface AgentSettingsProps {
  className?: string;
}

export function AgentSettings({ className = '' }: AgentSettingsProps) {
  const [customUrl, setCustomUrl] = useState('');
  const [customName, setCustomName] = useState('');
  const [isAdding, setIsAdding] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  const handleAddAgent = async () => {
    if (!customUrl.trim()) return;

    setIsAdding(true);
    setMessage(null);

    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setMessage({
        type: 'success',
        text: `Agent "${customName || 'Custom Agent'}" added successfully!`
      });
      
      setCustomUrl('');
      setCustomName('');
    } catch {
      setMessage({
        type: 'error',
        text: 'Failed to add agent. Please try again.'
      });
    } finally {
      setIsAdding(false);
    }
  };

  return (
    <div className={`bg-white rounded-lg border border-gray-200 p-6 ${className}`}>
      <div className="flex items-center space-x-3 mb-6">
        <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
          <span className="text-white text-sm font-bold">⚙️</span>
        </div>
        <div>
          <h3 className="text-lg font-semibold text-gray-900">Agent Settings</h3>
          <p className="text-sm text-gray-600">Configure and manage your agents</p>
        </div>
      </div>

      {/* Message Display */}
      {message && (
        <div className={`mb-6 p-4 rounded-lg border ${
          message.type === 'success'
            ? 'bg-green-50 border-green-200 text-green-700'
            : 'bg-red-50 border-red-200 text-red-700'
        }`}>
          <div className="flex items-center space-x-2">
            <span>{message.type === 'success' ? '✅' : '❌'}</span>
            <span className="font-medium">{message.text}</span>
          </div>
        </div>
      )}

      {/* Add Custom Agent */}
      <div className="mb-8">
        <h4 className="text-md font-semibold text-gray-900 mb-4">Add Custom Agent</h4>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Agent URL
            </label>
            <input
              type="url"
              value={customUrl}
              onChange={(e) => setCustomUrl(e.target.value)}
              placeholder="http://localhost:9000"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Custom Name (Optional)
            </label>
            <input
              type="text"
              value={customName}
              onChange={(e) => setCustomName(e.target.value)}
              placeholder="My Custom Agent"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          <button
            onClick={handleAddAgent}
            disabled={isAdding || !customUrl.trim()}
            className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200"
          >
            {isAdding ? 'Adding...' : 'Add Agent'}
          </button>
        </div>
      </div>

      {/* Default Ports */}
      <div className="mb-8">
        <h4 className="text-md font-semibold text-gray-900 mb-4">Default Discovery Ports</h4>
        <div className="bg-gray-50 rounded-lg p-4">
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-gray-600">Orchestrator:</span>
                <span className="font-mono text-gray-900">9000</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">TellTimeAgent:</span>
                <span className="font-mono text-gray-900">10000</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">GreetingAgent:</span>
                <span className="font-mono text-gray-900">10001</span>
              </div>
            </div>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-gray-600">CarbonCreditAgent:</span>
                <span className="font-mono text-gray-900">10002</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">WalletBalanceAgent:</span>
                <span className="font-mono text-gray-900">10003</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">PaymentAgent:</span>
                <span className="font-mono text-gray-900">10004</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Connection Settings */}
      <div>
        <h4 className="text-md font-semibold text-gray-900 mb-4">Connection Settings</h4>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
            <div className="text-sm font-medium text-blue-900 mb-1">Timeout</div>
            <div className="text-xs text-blue-600">30 seconds</div>
          </div>
          <div className="p-4 bg-green-50 rounded-lg border border-green-200">
            <div className="text-sm font-medium text-green-900 mb-1">Retry Attempts</div>
            <div className="text-xs text-green-600">3 attempts</div>
          </div>
          <div className="p-4 bg-purple-50 rounded-lg border border-purple-200">
            <div className="text-sm font-medium text-purple-900 mb-1">Health Check</div>
            <div className="text-xs text-purple-600">Every 30s</div>
          </div>
        </div>
      </div>
    </div>
  );
}