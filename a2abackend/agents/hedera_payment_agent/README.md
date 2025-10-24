# Hedera Payment Agent

A TypeScript-based A2A (Agent-to-Agent) Hedera payment agent that provides autonomous HBAR transfer capabilities using the Hedera Agent Kit.

## Features

- **Autonomous HBAR Transfers**: Execute HBAR transfers automatically using Hedera Agent Kit
- **Natural Language Processing**: Understand payment requests in natural language
- **Account Balance Queries**: Check Hedera account balances
- **Transaction Status**: Query transaction status and history
- **A2A Integration**: Compatible with the A2A orchestrator system

## Prerequisites

- Node.js 18+ 
- npm or yarn
- Hedera Testnet account
- Ollama installed and running locally

## Installation

1. Navigate to the hedera-payment-agent directory:
```bash
cd /Users/niraj/Desktop/hackathons/a2amarketplace/a2abackend/agents/hedera_payment_agent
```

2. Install dependencies:
```bash
npm install
```

3. Set up environment variables:
```bash
cp env.example .env
```

4. Edit `.env` file with your credentials:
```env
HEDERA_ACCOUNT_ID=0.0.xxxxx
HEDERA_PRIVATE_KEY=0x...
PORT=10009
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
```

## Getting Credentials

### Hedera Testnet Account
1. Go to [Hedera Portal](https://portal.hedera.com/dashboard)
2. Create a testnet account
3. Copy your Account ID and Private Key to your `.env` file

### Ollama Setup
1. Install Ollama from [ollama.com](https://ollama.com)
2. Pull the llama3.2 model: `ollama pull llama3.2`
3. Start Ollama service: `ollama serve`
4. The agent will connect to Ollama automatically

## Usage

### Development Mode
```bash
npm run dev
```

### Production Mode
```bash
npm run build
npm start
```

### A2A Agent Mode
```bash
npm run a2a:hedera-payment
```

The agent will start on `http://localhost:10009` by default.

## Agent Capabilities

### Autonomous HBAR Transfers
- Execute HBAR transfers automatically
- Support for various amount formats (HBAR, tinybars)
- Automatic transaction confirmation

### Account Management
- Check account balances
- Query transaction history
- Validate account IDs

### Natural Language Processing
- Understand payment requests in natural language
- Parse amounts and recipient addresses
- Provide transaction confirmations

## Integration with Orchestrator

This agent is designed to work with the A2A orchestrator. The orchestrator can delegate Hedera payment requests to this agent, which will:

1. Process the user's payment request
2. Use Hedera Agent Kit to execute the transaction autonomously
3. Provide transaction confirmation and details
4. Return structured data for other agents

## API Endpoints

- `GET /.well-known/agent.json` - Agent card information
- `GET /health` - Health check endpoint
- `POST /` - Main A2A communication endpoint

## Example Queries

- "Send 0.001 HBAR to account 0.0.123456"
- "Transfer 1.5 HBAR to 0.0.789012"
- "Make a payment of 0.5 HBAR to recipient 0.0.345678"
- "Check my account balance"
- "What's the status of my last transaction?"

## Architecture

The agent is built using:
- **TypeScript** for type safety
- **Hedera Agent Kit** for autonomous Hedera operations
- **LangChain** for AI prompt management
- **Ollama (Llama 3.2)** for local natural language processing
- **Express.js** for HTTP server
- **A2A Protocol** for agent-to-agent communication

## Security Features

- **Autonomous Mode**: Uses Hedera Agent Kit's autonomous execution
- **Transaction Validation**: Verifies recipient accounts and amounts
- **Error Handling**: Comprehensive error handling for failed transactions
- **Balance Checks**: Ensures sufficient balance before transfers

## Error Handling

The agent includes comprehensive error handling for:
- Insufficient account balance
- Invalid recipient accounts
- Network connectivity issues
- Invalid transaction parameters
- Missing credentials

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is part of the A2A marketplace system and follows the same licensing terms.
