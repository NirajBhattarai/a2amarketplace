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
    <div className={`glass rounded-2xl shadow-2xl p-8 hover-lift transition-all duration-300 ${className}`}>
      <div className="flex items-center justify-between mb-8">
        <div className="flex items-center space-x-4">
          <div className="w-12 h-12 bg-gradient-to-r from-purple-400 to-pink-500 rounded-full flex items-center justify-center animate-pulse-glow">
            <span className="text-white text-2xl">🎯</span>
          </div>
          <div>
            <h3 className="text-2xl font-bold gradient-text">Select Agent</h3>
            <p className="text-gray-600">Choose an agent to interact with</p>
          </div>
        </div>
        <button
          onClick={loadAgents}
          disabled={isLoading}
          className="px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-2xl hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 transition-all duration-300 hover-lift font-semibold flex items-center space-x-2"
        >
          <span>{isLoading ? '🔄' : '🔄'}</span>
          <span>{isLoading ? 'Refreshing...' : 'Refresh'}</span>
        </button>
      </div>

      {isLoading ? (
        <div className="text-center py-12">
          <div className="w-16 h-16 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center mx-auto mb-4 animate-pulse-glow">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-white"></div>
          </div>
          <p className="text-lg font-semibold text-gray-600">Loading agents...</p>
          <p className="text-sm text-gray-500 mt-1">Please wait while we discover available agents</p>
        </div>
      ) : agents.length === 0 ? (
        <div className="text-center py-12">
          <div className="w-16 h-16 bg-gradient-to-r from-gray-400 to-gray-500 rounded-full flex items-center justify-center mx-auto mb-4">
            <span className="text-white text-2xl">🔍</span>
          </div>
          <p className="text-lg font-semibold text-gray-600 mb-2">No available agents found</p>
          <p className="text-sm text-gray-500">
            Make sure the A2A backend servers are running
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {agents.map((agent, index) => (
            <div
              key={agent.card.name}
              className={`group p-6 rounded-2xl border-2 cursor-pointer transition-all duration-300 hover-lift ${
                selectedAgent === agent.card.name
                  ? 'border-blue-500 bg-gradient-to-r from-blue-50 to-blue-100 shadow-lg'
                  : 'border-gray-200 hover:border-gray-300 hover:bg-gradient-to-r hover:from-gray-50 hover:to-gray-100'
              }`}
              onClick={() => handleAgentSelect(agent.card.name)}
              style={{ animationDelay: `${index * 0.1}s` }}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <div className={`w-12 h-12 rounded-full flex items-center justify-center ${
                    agent.isAvailable 
                      ? 'bg-gradient-to-r from-green-500 to-emerald-500' 
                      : 'bg-gradient-to-r from-red-500 to-pink-500'
                  }`}>
                    <span className="text-white text-xl">
                      {agent.isAvailable ? '🤖' : '⚠️'}
                    </span>
                  </div>
                  <div>
                    <div className="font-bold text-lg text-gray-800 group-hover:text-gray-900 transition-colors">
                      {agent.card.name}
                    </div>
                    <div className="text-sm text-gray-500 font-mono">
                      {agent.card.url}
                    </div>
                    {agent.card.description && (
                      <div className="text-xs text-gray-400 mt-1">
                        {agent.card.description}
                      </div>
                    )}
                  </div>
                </div>
                <div className="flex items-center space-x-3">
                  <div className={`inline-flex items-center space-x-2 px-3 py-1 rounded-full text-sm font-semibold ${
                    agent.isAvailable 
                      ? 'bg-green-100 text-green-700' 
                      : 'bg-red-100 text-red-700'
                  }`}>
                    <div className={`w-2 h-2 rounded-full ${
                      agent.isAvailable ? 'bg-green-500' : 'bg-red-500'
                    }`}></div>
                    <span>{agent.isAvailable ? 'Online' : 'Offline'}</span>
                  </div>
                  {selectedAgent === agent.card.name && (
                    <div className="w-8 h-8 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full flex items-center justify-center animate-pulse-glow">
                      <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                    </div>
                  )}
                </div>
              </div>
              
              {agent.card.capabilities && agent.card.capabilities.length > 0 && (
                <div className="mt-4 pt-4 border-t border-gray-200">
                  <div className="text-sm font-semibold text-gray-600 mb-2">Capabilities:</div>
                  <div className="flex flex-wrap gap-2">
                    {agent.card.capabilities.map((capability, index) => (
                      <span
                        key={index}
                        className="px-3 py-1 bg-gradient-to-r from-gray-100 to-gray-200 text-gray-700 rounded-full text-xs font-medium hover:from-gray-200 hover:to-gray-300 transition-colors"
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
        <div className="mt-6 p-6 bg-gradient-to-r from-blue-50 to-purple-50 rounded-2xl border-2 border-blue-200">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full flex items-center justify-center">
              <span className="text-white text-sm">✓</span>
            </div>
            <div>
              <div className="text-lg font-bold text-blue-800">
                Selected: {selectedAgentData.card.name}
              </div>
              <div className="text-sm text-blue-600 mt-1">
                Ready to receive messages and process requests
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
