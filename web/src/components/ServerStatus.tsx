'use client';

import { useState, useEffect } from 'react';
import { agentDiscovery, DiscoveredAgent } from '../services/AgentDiscovery';

interface ServerStatusProps {
  className?: string;
}

export function ServerStatus({ className = '' }: ServerStatusProps) {
  const [agents, setAgents] = useState<DiscoveredAgent[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());

  useEffect(() => {
    // Start discovery
    agentDiscovery.startDiscovery();
    
    // Initial load
    loadAgents();
    
    // Set up periodic refresh
    const interval = setInterval(() => {
      loadAgents();
    }, 10000); // Refresh every 10 seconds
    
    return () => {
      clearInterval(interval);
      agentDiscovery.stopDiscovery();
    };
  }, []);

  const loadAgents = async () => {
    try {
      await agentDiscovery.refreshAgents();
      setAgents(agentDiscovery.getAllAgents());
      setLastUpdate(new Date());
    } catch (error) {
      console.error('Failed to load agents:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const getStatusColor = (isAvailable: boolean) => {
    return isAvailable ? 'text-green-600' : 'text-red-600';
  };

  const getStatusIcon = (isAvailable: boolean) => {
    return isAvailable ? '🟢' : '🔴';
  };

  const stats = agentDiscovery.getStats();

  return (
    <div className={`bg-white rounded-lg shadow-lg p-6 ${className}`}>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-800">Server Status</h3>
        <div className="flex items-center space-x-2">
          <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
          <span className="text-sm text-gray-500">
            Last updated: {lastUpdate.toLocaleTimeString()}
          </span>
        </div>
      </div>

      {/* Statistics */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="text-center">
          <div className="text-2xl font-bold text-blue-600">{stats.total}</div>
          <div className="text-sm text-gray-500">Total Agents</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-green-600">{stats.available}</div>
          <div className="text-sm text-gray-500">Available</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-red-600">{stats.unavailable}</div>
          <div className="text-sm text-gray-500">Unavailable</div>
        </div>
      </div>

      {/* Agent List */}
      <div className="space-y-3">
        {isLoading ? (
          <div className="text-center py-4">
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600 mx-auto"></div>
            <p className="text-sm text-gray-500 mt-2">Discovering agents...</p>
          </div>
        ) : agents.length === 0 ? (
          <div className="text-center py-4">
            <p className="text-gray-500">No agents discovered</p>
            <button
              onClick={loadAgents}
              className="mt-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Refresh
            </button>
          </div>
        ) : (
          agents.map((agent) => (
            <div
              key={agent.card.name}
              className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
            >
              <div className="flex items-center space-x-3">
                <span className="text-lg">
                  {getStatusIcon(agent.isAvailable)}
                </span>
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
              <div className="text-right">
                <div className={`text-sm font-medium ${getStatusColor(agent.isAvailable)}`}>
                  {agent.isAvailable ? 'Online' : 'Offline'}
                </div>
                <div className="text-xs text-gray-400">
                  {agent.lastChecked.toLocaleTimeString()}
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Capabilities */}
      {agents.length > 0 && (
        <div className="mt-6">
          <h4 className="text-sm font-medium text-gray-700 mb-3">Agent Capabilities</h4>
          <div className="space-y-2">
            {agents.map((agent) => (
              agent.card.capabilities && agent.card.capabilities.length > 0 && (
                <div key={agent.card.name} className="text-sm">
                  <span className="font-medium text-gray-600">{agent.card.name}:</span>
                  <div className="flex flex-wrap gap-1 mt-1">
                    {agent.card.capabilities.map((capability, index) => (
                      <span
                        key={index}
                        className="px-2 py-1 bg-blue-100 text-blue-700 rounded-full text-xs"
                      >
                        {capability}
                      </span>
                    ))}
                  </div>
                </div>
              )
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
