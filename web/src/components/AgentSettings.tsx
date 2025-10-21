'use client';

import { useState, useEffect } from 'react';
import { agentDiscovery } from '../services/AgentDiscovery';

interface AgentSettingsProps {
  className?: string;
}

export function AgentSettings({ className = '' }: AgentSettingsProps) {
  const [customUrl, setCustomUrl] = useState('');
  const [customName, setCustomName] = useState('');
  const [isAdding, setIsAdding] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  const showMessage = (type: 'success' | 'error', text: string) => {
    setMessage({ type, text });
    setTimeout(() => setMessage(null), 3000);
  };

  const handleAddAgent = async () => {
    if (!customUrl.trim()) {
      showMessage('error', 'Please enter a valid URL');
      return;
    }

    setIsAdding(true);
    try {
      const agent = await agentDiscovery.addAgent(customUrl, customName || undefined);
      if (agent) {
        showMessage('success', `Successfully added agent: ${agent.card.name}`);
        setCustomUrl('');
        setCustomName('');
      } else {
        showMessage('error', 'Failed to add agent. Please check the URL and try again.');
      }
    } catch (error) {
      showMessage('error', `Error adding agent: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setIsAdding(false);
    }
  };

  const handleRemoveAgent = async (agentName: string) => {
    const success = agentDiscovery.removeAgent(agentName);
    if (success) {
      showMessage('success', `Removed agent: ${agentName}`);
    } else {
      showMessage('error', `Failed to remove agent: ${agentName}`);
    }
  };

  const handleRefreshAll = async () => {
    try {
      await agentDiscovery.discoverAgents();
      showMessage('success', 'Refreshed all agents');
    } catch (error) {
      showMessage('error', `Failed to refresh agents: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  };

  return (
    <div className={`bg-white rounded-lg shadow-lg p-6 ${className}`}>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-800">Agent Settings</h3>
        <button
          onClick={handleRefreshAll}
          className="px-3 py-1 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          Refresh All
        </button>
      </div>

      {/* Message Display */}
      {message && (
        <div className={`mb-4 p-3 rounded-lg ${
          message.type === 'success' 
            ? 'bg-green-100 text-green-700 border border-green-200' 
            : 'bg-red-100 text-red-700 border border-red-200'
        }`}>
          {message.text}
        </div>
      )}

      {/* Add Custom Agent */}
      <div className="mb-6">
        <h4 className="text-sm font-medium text-gray-700 mb-3">Add Custom Agent</h4>
        <div className="space-y-3">
          <div>
            <label className="block text-sm text-gray-600 mb-1">Agent URL</label>
            <input
              type="url"
              value={customUrl}
              onChange={(e) => setCustomUrl(e.target.value)}
              placeholder="http://localhost:10003"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          <div>
            <label className="block text-sm text-gray-600 mb-1">Custom Name (optional)</label>
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
            className="w-full px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {isAdding ? 'Adding...' : 'Add Agent'}
          </button>
        </div>
      </div>

      {/* Default Ports Configuration */}
      <div className="mb-6">
        <h4 className="text-sm font-medium text-gray-700 mb-3">Default Discovery Ports</h4>
        <div className="text-sm text-gray-600">
          <p>The system automatically discovers agents on these ports:</p>
          <div className="mt-2 flex flex-wrap gap-2">
            {[10000, 10001, 10002].map(port => (
              <span key={port} className="px-2 py-1 bg-gray-100 text-gray-700 rounded-full">
                {port}
              </span>
            ))}
          </div>
        </div>
      </div>

      {/* Connection Settings */}
      <div>
        <h4 className="text-sm font-medium text-gray-700 mb-3">Connection Settings</h4>
        <div className="space-y-2 text-sm text-gray-600">
          <div className="flex justify-between">
            <span>Request Timeout:</span>
            <span className="font-medium">30 seconds</span>
          </div>
          <div className="flex justify-between">
            <span>Discovery Interval:</span>
            <span className="font-medium">30 seconds</span>
          </div>
          <div className="flex justify-between">
            <span>Retry Attempts:</span>
            <span className="font-medium">3</span>
          </div>
        </div>
      </div>
    </div>
  );
}
