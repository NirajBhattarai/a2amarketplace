'use client';

import { useState, useEffect } from 'react';

interface Agent {
  card: {
    name: string;
    description: string;
    url: string;
    version: string;
    capabilities: {
      streaming: boolean;
      pushNotifications: boolean;
      stateTransitionHistory: boolean;
    };
    skills: Array<{
      id: string;
      name: string;
      description: string;
      tags: string[];
    }>;
  };
  isAvailable: boolean;
}

interface ServerStatusProps {
  className?: string;
}

export function ServerStatus({ className = '' }: ServerStatusProps) {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [backendHealth, setBackendHealth] = useState<{ status: string; timestamp: string; backend?: string; error?: string } | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Check backend health
        const healthResponse = await fetch('/api/health');
        if (healthResponse.ok) {
          const healthData = await healthResponse.json();
          setBackendHealth(healthData);
        }

        // Fetch agents
        const response = await fetch('/api/agents');
        if (response.ok) {
          const data = await response.json();
          setAgents(data.agents || []);
        }
      } catch (error) {
        console.error('Error fetching data:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, []);

  const totalAgents = agents.length;
  const availableAgents = agents.filter(agent => agent.isAvailable).length;
  const unavailableAgents = totalAgents - availableAgents;

  return (
    <div className={`bg-white rounded-lg border border-gray-200 p-6 ${className}`}>
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center">
            <span className="text-white text-sm font-bold">📊</span>
          </div>
          <div>
            <h3 className="text-lg font-semibold text-gray-900">Agent Status</h3>
            <p className="text-sm text-gray-600">Monitor agent availability and health</p>
          </div>
        </div>
        <button
          onClick={() => window.location.reload()}
          className="px-3 py-1 text-sm bg-gray-100 hover:bg-gray-200 rounded-md transition-colors duration-200"
        >
          Refresh
        </button>
      </div>

      {/* Backend Health */}
      {backendHealth && (
        <div className={`mb-6 p-4 rounded-lg border ${
          backendHealth.status === 'healthy' 
            ? 'bg-green-50 border-green-200' 
            : 'bg-red-50 border-red-200'
        }`}>
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <div className={`w-3 h-3 rounded-full ${
                backendHealth.status === 'healthy' ? 'bg-green-500' : 'bg-red-500'
              }`}></div>
              <span className="font-medium text-gray-900">Backend Status</span>
            </div>
            <span className={`text-sm font-medium ${
              backendHealth.status === 'healthy' ? 'text-green-600' : 'text-red-600'
            }`}>
              {backendHealth.status === 'healthy' ? 'Online' : 'Offline'}
            </span>
          </div>
          <div className="text-xs text-gray-600 mt-1">
            {backendHealth.backend} • {backendHealth.timestamp}
          </div>
          {backendHealth.error && (
            <div className="text-xs text-red-600 mt-1">
              Error: {backendHealth.error}
            </div>
          )}
        </div>
      )}

      {/* Statistics */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="text-center p-4 bg-gray-50 rounded-lg">
          <div className="text-2xl font-bold text-gray-900">{totalAgents}</div>
          <div className="text-sm text-gray-600">Total Agents</div>
        </div>
        <div className="text-center p-4 bg-green-50 rounded-lg">
          <div className="text-2xl font-bold text-green-600">{availableAgents}</div>
          <div className="text-sm text-gray-600">Available</div>
        </div>
        <div className="text-center p-4 bg-red-50 rounded-lg">
          <div className="text-2xl font-bold text-red-600">{unavailableAgents}</div>
          <div className="text-sm text-gray-600">Unavailable</div>
        </div>
      </div>

      {/* Agent List */}
      <div className="space-y-3">
        {isLoading ? (
          <div className="text-center py-8">
            <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
            <p className="text-gray-600">Loading agents...</p>
          </div>
        ) : agents.length === 0 ? (
          <div className="text-center py-8">
            <div className="w-12 h-12 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <span className="text-2xl">🔍</span>
            </div>
            <h4 className="text-lg font-medium text-gray-900 mb-2">No Agents Found</h4>
            <p className="text-gray-600 mb-4">No agents are currently registered or available.</p>
            <button
              onClick={() => window.location.reload()}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors duration-200"
            >
              Refresh
            </button>
          </div>
        ) : (
          agents.map((agent) => (
            <div
              key={agent.card.name}
              className={`p-4 rounded-lg border ${
                agent.isAvailable
                  ? 'bg-green-50 border-green-200'
                  : 'bg-red-50 border-red-200'
              }`}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className={`w-3 h-3 rounded-full ${
                    agent.isAvailable ? 'bg-green-500' : 'bg-red-500'
                  }`}></div>
                  <div>
                    <h4 className="font-medium text-gray-900">{agent.card.name}</h4>
                    <p className="text-sm text-gray-600">{agent.card.description}</p>
                  </div>
                </div>
                <div className="text-right">
                  <div className={`text-sm font-medium ${
                    agent.isAvailable ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {agent.isAvailable ? 'Online' : 'Offline'}
                  </div>
                  <div className="text-xs text-gray-500">v{agent.card.version}</div>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}