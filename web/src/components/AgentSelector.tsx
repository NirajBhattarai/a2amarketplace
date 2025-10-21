'use client';

import { useState, useEffect } from 'react';
import { agentDiscovery, DiscoveredAgent } from '../services/AgentDiscovery';

interface AgentSelectorProps {
  selectedAgent: string | null;
  onAgentSelect: (agentName: string | null) => void;
  className?: string;
}

export function AgentSelector({ selectedAgent, onAgentSelect, className = '' }: AgentSelectorProps) {
  const [agents, setAgents] = useState<DiscoveredAgent[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadAgents();
    
    // Set up periodic refresh
    const interval = setInterval(loadAgents, 15000); // Refresh every 15 seconds
    
    return () => clearInterval(interval);
  }, []);

  const loadAgents = async () => {
    try {
      await agentDiscovery.refreshAgents();
      setAgents(agentDiscovery.getAvailableAgents());
    } catch (error) {
      console.error('Failed to load agents:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleAgentSelect = (agentName: string) => {
    if (selectedAgent === agentName) {
      onAgentSelect(null); // Deselect if already selected
    } else {
      onAgentSelect(agentName);
    }
  };

  const selectedAgentData = agents.find(agent => agent.card.name === selectedAgent);

  return (
    <div className={`bg-white rounded-lg shadow-lg p-6 ${className}`}>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-800">Select Agent</h3>
        <button
          onClick={loadAgents}
          disabled={isLoading}
          className="px-3 py-1 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
        >
          {isLoading ? 'Refreshing...' : 'Refresh'}
        </button>
      </div>

      {isLoading ? (
        <div className="text-center py-4">
          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600 mx-auto"></div>
          <p className="text-sm text-gray-500 mt-2">Loading agents...</p>
        </div>
      ) : agents.length === 0 ? (
        <div className="text-center py-4">
          <p className="text-gray-500">No available agents found</p>
          <p className="text-sm text-gray-400 mt-1">
            Make sure the A2A backend servers are running
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {agents.map((agent) => (
            <div
              key={agent.card.name}
              className={`p-4 rounded-lg border-2 cursor-pointer transition-all ${
                selectedAgent === agent.card.name
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
              }`}
              onClick={() => handleAgentSelect(agent.card.name)}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className={`w-3 h-3 rounded-full ${
                    agent.isAvailable ? 'bg-green-500' : 'bg-red-500'
                  }`}></div>
                  <div>
                    <div className="font-medium text-gray-800">
                      {agent.card.name}
                    </div>
                    <div className="text-sm text-gray-500">
                      {agent.card.url}
                    </div>
                    {agent.card.description && (
                      <div className="text-xs text-gray-400 mt-1">
                        {agent.card.description}
                      </div>
                    )}
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  {selectedAgent === agent.card.name && (
                    <div className="w-5 h-5 bg-blue-600 rounded-full flex items-center justify-center">
                      <svg className="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                    </div>
                  )}
                </div>
              </div>
              
              {agent.card.capabilities && agent.card.capabilities.length > 0 && (
                <div className="mt-3">
                  <div className="text-xs text-gray-500 mb-1">Capabilities:</div>
                  <div className="flex flex-wrap gap-1">
                    {agent.card.capabilities.map((capability, index) => (
                      <span
                        key={index}
                        className="px-2 py-1 bg-gray-100 text-gray-600 rounded-full text-xs"
                      >
                        {capability}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {selectedAgentData && (
        <div className="mt-4 p-3 bg-blue-50 rounded-lg">
          <div className="text-sm font-medium text-blue-800">
            Selected: {selectedAgentData.card.name}
          </div>
          <div className="text-xs text-blue-600 mt-1">
            Ready to receive messages
          </div>
        </div>
      )}
    </div>
  );
}
