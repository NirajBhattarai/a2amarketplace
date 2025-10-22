// A2A Client Service - TypeScript implementation of the Python A2AClient
// This service handles communication with A2A agents using JSON-RPC protocol

export interface AgentCard {
  name: string;
  description: string;
  url: string;
  capabilities: string[];
  version?: string;
}

export interface MessagePart {
  type: 'text';
  text: string;
}

export interface Message {
  role: 'user' | 'agent';
  parts: MessagePart[];
}

export interface Task {
  id: string;
  sessionId: string;
  history: Message[];
  status: 'pending' | 'completed' | 'error';
  createdAt: string;
  updatedAt: string;
}

export interface TaskSendParams {
  id: string;
  sessionId: string;
  message: Message;
}

export interface SendTaskRequest {
  jsonrpc: '2.0';
  id: string;
  method: 'tasks/send';
  params: TaskSendParams;
}

export interface GetTaskRequest {
  jsonrpc: '2.0';
  id: string;
  method: 'tasks/get';
  params: {
    id: string;
    sessionId: string;
  };
}

export interface JSONRPCResponse<T = unknown> {
  jsonrpc: '2.0';
  id: string;
  result?: T;
  error?: {
    code: number;
    message: string;
  };
}

export class A2AClientError extends Error {
  constructor(message: string, public statusCode?: number) {
    super(message);
    this.name = 'A2AClientError';
  }
}

export class A2AClient {
  private url: string;
  private timeout: number;

  constructor(url: string, timeout: number = 30000) {
    this.url = url;
    this.timeout = timeout;
  }

  /**
   * Send a task to the A2A agent via the web API
   */
  async sendTask(payload: {
    id: string;
    sessionId: string;
    message: {
      role: 'user';
      parts: MessagePart[];
    };
  }): Promise<Task> {
    console.log('📤 Sending task via web API:', JSON.stringify(payload, null, 2));

    try {
      const response = await fetch('/api/agent', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: payload.message.parts[0].text,
          sessionId: payload.sessionId,
          agentUrl: this.url,
        }),
      });

      if (!response.ok) {
        throw new A2AClientError(`HTTP ${response.status}: ${response.statusText}`, response.status);
      }

      const result = await response.json();
      
      if (!result.success) {
        throw new A2AClientError(result.error || 'API request failed');
      }

      // Extract the task from the A2A response
      if (result.data?.result) {
        return result.data.result as Task;
      } else {
        throw new A2AClientError('No task result in response');
      }
    } catch (error) {
      if (error instanceof A2AClientError) {
        throw error;
      }
      throw new A2AClientError(`Failed to send task: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Get task status or history
   */
  async getTask(taskId: string, sessionId: string): Promise<Task> {
    const request: GetTaskRequest = {
      jsonrpc: '2.0',
      id: this.generateId(),
      method: 'tasks/get',
      params: {
        id: taskId,
        sessionId: sessionId,
      },
    };

    try {
      const response = await this.makeRequest(request);
      
      if (response.error) {
        throw new A2AClientError(response.error.message, response.error.code);
      }

      return response.result as Task;
    } catch (error) {
      if (error instanceof A2AClientError) {
        throw error;
      }
      throw new A2AClientError(`Failed to get task: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Discover agent capabilities
   */
  async discoverAgent(): Promise<AgentCard> {
    try {
      const response = await fetch(`${this.url}/.well-known/agent.json`, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
        },
        signal: AbortSignal.timeout(this.timeout),
      });

      if (!response.ok) {
        throw new A2AClientError(`Agent discovery failed: ${response.status} ${response.statusText}`, response.status);
      }

      return await response.json();
    } catch (error) {
      if (error instanceof A2AClientError) {
        throw error;
      }
      throw new A2AClientError(`Failed to discover agent: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Check if the agent is available
   */
  async isAvailable(): Promise<boolean> {
    try {
      await this.discoverAgent();
      return true;
    } catch {
      return false;
    }
  }

  /**
   * Make a JSON-RPC request to the agent
   */
  private async makeRequest(request: SendTaskRequest | GetTaskRequest): Promise<JSONRPCResponse> {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.timeout);

    try {
      const response = await fetch(this.url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        throw new A2AClientError(`HTTP ${response.status}: ${response.statusText}`, response.status);
      }

      const result = await response.json();
      return result;
    } catch (error) {
      clearTimeout(timeoutId);
      
      if (error instanceof A2AClientError) {
        throw error;
      }
      
      if (error instanceof Error && error.name === 'AbortError') {
        throw new A2AClientError('Request timeout');
      }
      
      throw new A2AClientError(`Network error: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Generate a unique ID for requests
   */
  private generateId(): string {
    return Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);
  }
}
