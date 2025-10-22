// Agent Discovery Service
// Discovers and manages available A2A agents

import { A2AClient, AgentCard } from './A2AClient';

export interface DiscoveredAgent {
  card: AgentCard;
  client: A2AClient;
  isAvailable: boolean;
  lastChecked: Date;
}

export class AgentDiscovery {
  private agents: Map<string, DiscoveredAgent> = new Map();
  private discoveryInterval: NodeJS.Timeout | null = null;
  private readonly checkInterval = 30000; // 30 seconds

  constructor(private defaultPorts: number[] = [10000, 10001, 10002, 10003]) {}

  /**
   * Discover agents on default ports
   */
  async discoverAgents(): Promise<DiscoveredAgent[]> {
    const discovered: DiscoveredAgent[] = [];
    
    for (const port of this.defaultPorts) {
      try {
        const url = `http://localhost:${port}`;
        const client = new A2AClient(url);
        
        // Try to discover the agent
        const card = await client.discoverAgent();
        const isAvailable = await client.isAvailable();
        
        const agent: DiscoveredAgent = {
          card,
          client,
          isAvailable,
          lastChecked: new Date(),
        };
        
        this.agents.set(card.name, agent);
        discovered.push(agent);
        
        console.log(`✅ Discovered agent: ${card.name} at ${url}`);
      } catch (error) {
        console.log(`❌ No agent found at port ${port}:`, error instanceof Error ? error.message : 'Unknown error');
      }
    }
    
    return discovered;
  }

  /**
   * Get a specific agent by name
   */
  getAgent(name: string): DiscoveredAgent | undefined {
    return this.agents.get(name);
  }

  /**
   * Get all discovered agents
   */
  getAllAgents(): DiscoveredAgent[] {
    return Array.from(this.agents.values());
  }

  /**
   * Get available agents only
   */
  getAvailableAgents(): DiscoveredAgent[] {
    return this.getAllAgents().filter(agent => agent.isAvailable);
  }

  /**
   * Add a custom agent
   */
  async addAgent(url: string, name?: string): Promise<DiscoveredAgent | null> {
    try {
      const client = new A2AClient(url);
      const card = await client.discoverAgent();
      const isAvailable = await client.isAvailable();
      
      const agentName = name || card.name;
      const agent: DiscoveredAgent = {
        card: { ...card, name: agentName },
        client,
        isAvailable,
        lastChecked: new Date(),
      };
      
      this.agents.set(agentName, agent);
      return agent;
    } catch (error) {
      console.error(`Failed to add agent at ${url}:`, error);
      return null;
    }
  }

  /**
   * Remove an agent
   */
  removeAgent(name: string): boolean {
    return this.agents.delete(name);
  }

  /**
   * Start periodic discovery
   */
  startDiscovery(): void {
    if (this.discoveryInterval) {
      return;
    }
    
    // Initial discovery
    this.discoverAgents();
    
    // Set up periodic discovery
    this.discoveryInterval = setInterval(async () => {
      await this.refreshAgents();
    }, this.checkInterval);
  }

  /**
   * Stop periodic discovery
   */
  stopDiscovery(): void {
    if (this.discoveryInterval) {
      clearInterval(this.discoveryInterval);
      this.discoveryInterval = null;
    }
  }

  /**
   * Refresh agent availability
   */
  async refreshAgents(): Promise<void> {
    const agents = this.getAllAgents();
    
    for (const agent of agents) {
      try {
        const isAvailable = await agent.client.isAvailable();
        agent.isAvailable = isAvailable;
        agent.lastChecked = new Date();
      } catch (error) {
        agent.isAvailable = false;
        agent.lastChecked = new Date();
      }
    }
  }

  /**
   * Get agent statistics
   */
  getStats(): {
    total: number;
    available: number;
    unavailable: number;
  } {
    const all = this.getAllAgents();
    const available = all.filter(agent => agent.isAvailable);
    
    return {
      total: all.length,
      available: available.length,
      unavailable: all.length - available.length,
    };
  }
}

// Singleton instance
export const agentDiscovery = new AgentDiscovery();
