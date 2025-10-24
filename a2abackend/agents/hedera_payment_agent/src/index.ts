import express from "express";
import { v4 as uuidv4 } from 'uuid';
import dotenv from 'dotenv';
import cors from 'cors';
import { ChatPromptTemplate } from '@langchain/core/prompts';
import { AgentExecutor, createToolCallingAgent } from 'langchain/agents';
import { Client, PrivateKey } from '@hashgraph/sdk';
import { ChatOpenAI } from '@langchain/openai';
import { HederaLangchainToolkit, coreQueriesPlugin, coreAccountPlugin, coreHTSPlugin, AgentMode } from 'hedera-agent-kit';
import { TransferTransaction, Hbar } from '@hashgraph/sdk';

// Load environment variables
dotenv.config();

// Agent Card definition
const hederaPaymentAgentCard = {
  name: "Hedera Payment Agent",
  description: "An autonomous Hedera payment agent that can execute HBAR transfers using Hedera Agent Kit",
  version: "1.0.0",
  protocolVersion: "1.0.0",
  url: "http://localhost:10009",
  capabilities: {
    streaming: false,
    pushNotifications: false,
    stateTransitionHistory: false
  },
  skills: [
    {
      id: "hedera_payment",
      name: "Hedera Payment Processing", 
      description: "Execute autonomous HBAR transfers on Hedera network",
      tags: ["payment", "hedera", "hbar", "blockchain"],
      examples: [
        "Send 0.001 HBAR to account 0.0.123456",
        "Transfer 1.5 HBAR to 0.0.789012", 
        "Make a payment of 0.5 HBAR to recipient 0.0.345678"
      ]
    }
  ]
};

// Create Express app with A2A-compatible endpoints
const expressApp = express();

// Middleware
expressApp.use(cors());
expressApp.use(express.json());

// Initialize Hedera client
let hederaClient: Client;
let hederaAgentToolkit: HederaLangchainToolkit;
let agentExecutor: AgentExecutor;

// Note: Direct SDK functions removed - using Hedera Agent Kit tools instead

async function initializeHederaAgent() {
  try {
    // Initialize Hedera client
    const privateKey = process.env.HEDERA_PRIVATE_KEY!;
    console.log(`[HederaPaymentAgent] 🔑 Using account: ${process.env.HEDERA_ACCOUNT_ID}`);
    console.log(`[HederaPaymentAgent] 🔑 Private key format: ${privateKey.substring(0, 10)}...`);
    
    // Parse private key using ED25519 format as per Hedera Agent Kit docs
    let parsedPrivateKey;
    try {
      // Use ED25519 format as recommended in the documentation
      parsedPrivateKey = PrivateKey.fromString(privateKey);
      console.log(`[HederaPaymentAgent] ✅ ED25519 private key parsed successfully`);
    } catch (error) {
      console.error(`[HederaPaymentAgent] ❌ Failed to parse private key:`, error);
      throw new Error(`Invalid private key format: ${error.message}`);
    }
    
    hederaClient = Client.forTestnet().setOperator(
      process.env.HEDERA_ACCOUNT_ID!,
      parsedPrivateKey,
    );

    // Initialize AI model (OpenAI - better function calling support)
    const llm = new ChatOpenAI({ 
      model: 'gpt-4o-mini',
      temperature: 0.1, // Lower temperature for more deterministic tool usage
      openAIApiKey: process.env.OPENAI_API_KEY
    });

    // Initialize Hedera Agent Kit with AUTONOMOUS mode
    hederaAgentToolkit = new HederaLangchainToolkit({
      client: hederaClient,
      configuration: {
        plugins: [coreQueriesPlugin, coreAccountPlugin, coreHTSPlugin],
        mode: AgentMode.AUTONOMOUS // Enable autonomous execution for automatic payments
      },
    });

    // Load the structured chat prompt template
    const prompt = ChatPromptTemplate.fromMessages([
      ['system', `You are a Hedera Payment Agent that executes AUTONOMOUS HBAR transfers on the Hedera network.

      CRITICAL INSTRUCTIONS:
      - You are configured in AUTONOMOUS mode and MUST execute transactions immediately
      - You have access to Hedera Agent Kit tools that can execute real blockchain transactions
      - When users request payments, you MUST use the transfer_hbar_tool to execute the transfer
      - When users request balance checks, you MUST use the get_hbar_balance_query_tool
      - Do NOT provide code examples, explanations, or guidance - EXECUTE the tools directly
      
      Your account details:
      - Account ID: ${process.env.HEDERA_ACCOUNT_ID}
      - Network: Hedera Testnet
      - Mode: AUTONOMOUS (transactions execute automatically)
      
      Available tools you MUST use:
      - transfer_hbar_tool: Execute HBAR transfers autonomously (use this for payments)
      - get_hbar_balance_query_tool: Check account balances (use this for balance queries)
      - transfer_hbar_with_allowance_tool: Transfer with allowances
      
      EXAMPLES of what you MUST do:
      - User: "Send 10 HBAR to account 0.0.123456" → IMMEDIATELY call transfer_hbar_tool with amount=10, recipient=0.0.123456
      - User: "Check my balance" → IMMEDIATELY call get_hbar_balance_query_tool with accountId=${process.env.HEDERA_ACCOUNT_ID}
      - User: "What's my balance" → IMMEDIATELY call get_hbar_balance_query_tool with accountId=${process.env.HEDERA_ACCOUNT_ID}
      
      You are authorized to execute transactions autonomously. Execute tools immediately when requested.`],
      ['placeholder', '{chat_history}'],
      ['human', '{input}'],
      ['placeholder', '{agent_scratchpad}'],
    ]);

    // Fetch tools from toolkit
    const tools = hederaAgentToolkit.getTools();
    console.log(`[HederaPaymentAgent] 🔧 Available tools:`, tools.map(tool => tool.name));
    console.log(`[HederaPaymentAgent] 🔧 Tool details:`, tools.map(tool => ({
      name: tool.name,
      description: tool.description,
      args: tool.args
    })));

    // Create the underlying agent
    const agent = createToolCallingAgent({
      llm,
      tools,
      prompt,
    });
    
    // Wrap everything in an executor that will maintain memory
    agentExecutor = new AgentExecutor({
      agent,
      tools,
    });

    console.log('[HederaPaymentAgent] ✅ Hedera Agent Kit initialized successfully');
  } catch (error) {
    console.error('[HederaPaymentAgent] ❌ Failed to initialize Hedera Agent Kit:', error);
    throw error;
  }
}

// A2A-compatible JSON-RPC endpoint
expressApp.post('/', async (req, res) => {
  try {
    const { jsonrpc, id, method, params } = req.body;

    if (jsonrpc !== '2.0' || method !== 'tasks/send') {
      return res.status(400).json({
        jsonrpc: '2.0',
        id,
        error: { code: -32601, message: 'Method not found' }
      });
    }

    const { id: taskId, sessionId, message } = params;
    const userMessage = message.parts[0].text;

    console.log(`[HederaPaymentAgent] Processing: "${userMessage}"`);

    // Use the Hedera Agent Kit with AUTONOMOUS mode for all requests
    console.log(`[HederaPaymentAgent] 🤖 Processing with Hedera Agent Kit (AUTONOMOUS mode)`);
    console.log(`[HederaPaymentAgent] 📝 User message: "${userMessage}"`);
    
    const response = await agentExecutor.invoke({ 
      input: userMessage,
      chat_history: [] // Could be enhanced to maintain conversation history
    });
    
    console.log(`[HederaPaymentAgent] 📤 Agent response:`, JSON.stringify(response, null, 2));

    // Create a proper Task object response that matches the orchestrator's expectations
    const taskResponse = {
      id: taskId,
      status: {
        state: "completed",
        timestamp: new Date().toISOString()
      },
      history: [
        {
          role: "user",
          parts: [{ type: "text", text: userMessage }]
        },
        {
          role: "agent", 
          parts: [{ type: "text", text: response.output }]
        }
      ]
    };

    res.json({
      jsonrpc: '2.0',
      id,
      result: taskResponse
    });
  } catch (error) {
    console.error('[HederaPaymentAgent] Error handling request:', error);
    res.status(500).json({
      jsonrpc: '2.0',
      id: req.body.id,
      error: { code: -32603, message: 'Internal error' }
    });
  }
});

// Agent card endpoints
expressApp.get('/.well-known/agent.json', (req, res) => {
  res.json(hederaPaymentAgentCard);
});

expressApp.get('/.well-known/agent-card.json', (req, res) => {
  res.json(hederaPaymentAgentCard);
});

// Health check endpoint
expressApp.get('/health', (req, res) => {
  res.json({ 
    status: 'healthy', 
    agent: 'Hedera Payment Agent',
    timestamp: new Date().toISOString()
  });
});

// Start the server
const PORT = process.env.PORT || 10009;

async function startServer() {
  try {
    // Initialize Hedera Agent Kit
    await initializeHederaAgent();
    
    expressApp.listen(PORT, () => {
      console.log(`[HederaPaymentAgent] 🚀 Server started on http://localhost:${PORT}`);
      console.log(`[HederaPaymentAgent] 📋 Agent Card: http://localhost:${PORT}/.well-known/agent.json`);
      console.log(`[HederaPaymentAgent] 🔧 Health Check: http://localhost:${PORT}/health`);
      console.log('[HederaPaymentAgent] Press Ctrl+C to stop the server');
    });
  } catch (error) {
    console.error('[HederaPaymentAgent] ❌ Failed to start server:', error);
    process.exit(1);
  }
}

startServer();
