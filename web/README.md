# A2A Web Frontend

A Next.js frontend application that provides a web interface for interacting with A2A (Agent-to-Agent) backend services.

## Features

- 🤖 **Multi-Agent Support**: Interact with TellTimeAgent, GreetingAgent, CarbonCreditAgent, WalletBalanceAgent, PaymentAgent, and OrchestratorAgent
- 💬 **Real-time Chat Interface**: Clean, modern chat UI for agent conversations
- 🔄 **Session Management**: Maintain conversation context across messages
- ⚡ **Quick Actions**: Pre-defined buttons for common queries
- 📱 **Responsive Design**: Works on desktop and mobile devices
- 💰 **Blockchain Payments**: Dedicated payment interface for real transactions
- 🔗 **Multi-Network Support**: Hedera HBAR, Ethereum ETH, Polygon MATIC transfers

## Getting Started

### Prerequisites

- Node.js 18+ 
- A2A backend running (see `../a2abackend/README.md`)

### Installation

1. Install dependencies:
   ```bash
   npm install
   ```

2. Start the development server:
   ```bash
   npm run dev
   ```

3. Open [http://localhost:3000](http://localhost:3000) in your browser

### Configuration

The frontend connects to the A2A backend via the `/api/agent` route. By default, it expects the backend to be running on `http://localhost:10002`.

To change the backend URL, set the environment variable:
```bash
NEXT_PUBLIC_A2A_BACKEND_URL=http://your-backend-url:port
```

## Usage

1. **Start the A2A Backend**: Follow the instructions in `../a2abackend/README.md` to start the orchestrator agent
2. **Open the Frontend**: Navigate to `http://localhost:3000`
3. **Start Chatting**: Type messages like:
   - "What time is it?" (calls TellTimeAgent)
   - "Greet me" (calls GreetingAgent)
   - "Find 100 carbon credits at best price" (calls CarbonCreditAgent)
   - "Check balance for wallet 0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6" (calls WalletBalanceAgent)
   - "Send 0.001 HBAR to account 0.0.123456" (calls PaymentAgent)
   - "Hello" (routed by OrchestratorAgent)

4. **Use Payment Interface**: Navigate to the "💰 Payments" tab for:
   - Quick payment templates for Hedera, Ethereum, and Polygon
   - Custom payment forms with network selection
   - Real blockchain transaction execution

## Architecture

```
Frontend (Next.js) → API Route → A2A Backend → Agents
```

- **Frontend**: React components with Tailwind CSS
- **API Route**: `/api/agent` handles communication with A2A backend
- **A2A Backend**: OrchestratorAgent routes requests to appropriate agents
- **Agents**: TellTimeAgent, GreetingAgent, CarbonCreditAgent, WalletBalanceAgent, PaymentAgent handle specific tasks

## Project Structure

```
web/
├── src/
│   ├── app/
│   │   ├── api/agent/route.ts    # API endpoint for A2A communication
│   │   └── page.tsx              # Main page component
│   ├── components/
│   │   ├── AgentChat.tsx        # Chat interface component
│   │   ├── AgentSelector.tsx    # Agent selection component
│   │   ├── ServerStatus.tsx     # Server monitoring component
│   │   ├── AgentSettings.tsx    # Agent configuration component
│   │   └── PaymentInterface.tsx # Blockchain payment interface
│   └── config/
│       └── agent.ts               # Agent configuration
├── package.json
└── README.md
```

## Payment Interface Features

The new "💰 Payments" tab provides:

### Quick Payment Templates
- **Test Hedera Transfer**: `Send 0.001 HBAR to account 0.0.123456`
- **Test Ethereum Transfer**: `Transfer 0.0001 ETH to 0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6`
- **Test Polygon Transfer**: `Send 0.001 MATIC to 0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6`
- **Transaction Status Check**: `Check status of transaction hedera_tx_12345`

### Custom Payment Form
- **Network Selection**: Choose between Hedera (HBAR), Ethereum (ETH), or Polygon (MATIC)
- **Amount Input**: Specify transaction amounts
- **Recipient Address**: Enter account IDs or wallet addresses
- **Memo Support**: Add memos for Hedera transactions
- **Real Transaction Execution**: Execute actual blockchain transactions

### Safety Features
- **Warning Messages**: Clear warnings about real transactions
- **Testnet Focus**: Designed for testnet usage with test funds
- **Input Validation**: Form validation for proper address formats

## Development

- **Framework**: Next.js 14 with App Router
- **Styling**: Tailwind CSS
- **TypeScript**: Full type safety
- **API**: RESTful API routes for backend communication
- **Components**: Modular React components for different interfaces