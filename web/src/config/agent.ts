// A2A Agent Configuration
export const AGENT_CONFIG = {
  // Default A2A backend URL - can be overridden by environment variables
  BACKEND_URL: process.env.NEXT_PUBLIC_A2A_BACKEND_URL || 'http://localhost:10002',
  
  // Available agents and their endpoints
  AGENTS: {
    ORCHESTRATOR: 'http://localhost:10002',
    TELL_TIME: 'http://localhost:10000', 
    GREETING: 'http://localhost:10001',
    CARBON_CREDIT: 'http://localhost:10003',
    WALLET_BALANCE: 'http://localhost:10004',
    PAYMENT: 'http://localhost:10005',
  },
  
  // Default session configuration
  SESSION: {
    TIMEOUT: 30000, // 30 seconds
    RETRY_ATTEMPTS: 3,
  }
};
