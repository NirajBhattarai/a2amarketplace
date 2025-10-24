# 💻 A2A Web Frontend

A modern Next.js frontend for the **A2A Carbon Credit Marketplace** featuring real-time chat interface, agent monitoring, and blockchain payment processing.

## 🎯 Overview

This frontend provides a comprehensive web interface for interacting with the A2A multi-agent system, featuring:
- **Real-time chat** with AI agents
- **Live agent monitoring** with status indicators
- **Blockchain payment interface** for real transactions
- **Responsive design** optimized for all devices

## ✨ Key Features

### 🤖 **Multi-Agent Interface**
- **Real-time Chat**: Seamless conversation with all 8 AI agents
- **Agent Status Monitoring**: Live indicators for agent availability
- **Session Management**: Context-aware conversations across agents
- **Quick Actions**: Pre-defined buttons for common queries

### 💰 **Blockchain Integration**
- **Payment Interface**: Dedicated UI for blockchain transactions
- **Multi-Network Support**: Hedera HBAR, Ethereum ETH, Polygon MATIC
- **Transaction Tracking**: Real-time status monitoring
- **Address Validation**: Smart validation for different networks

### 🎨 **Modern UI/UX**
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Tailwind CSS**: Modern, clean styling
- **Real-time Updates**: Live agent status and chat
- **Intuitive Navigation**: Easy access to all features

### 🏢 **Company Onboarding Interface**
- **Registration Portal**: Streamlined company signup process
- **Document Upload**: Secure file management for certificates and licenses
- **Credit Management**: Inventory tracking and pricing tools
- **Sales Dashboard**: Comprehensive analytics and reporting
- **Customer Portal**: B2B interface for corporate buyers

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