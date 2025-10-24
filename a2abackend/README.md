# 🤖 A2A Backend - Multi-Agent System

The Python backend for the **A2A Carbon Credit Marketplace** featuring 8 specialized AI agents powered by Google's Agent Development Kit (ADK) and Gemini LLM.

## 🎯 Overview

This backend implements a sophisticated **Agent-to-Agent (A2A) system** with:
- **8 Specialized Agents** for different carbon credit marketplace functions
- **Real-time IoT Integration** for carbon sequestration monitoring
- **Blockchain Payment Processing** across multiple networks
- **Intelligent Orchestration** using Gemini LLM for task routing

## 🤖 Agent Ecosystem

| Agent | Port | Purpose | Key Capabilities |
|-------|------|---------|------------------|
| **OrchestratorAgent** | 10002 | Central routing hub | LLM-based task delegation, agent discovery |
| **TellTimeAgent** | 10000 | Time service | Current time queries |
| **GreetingAgent** | 10001 | Poetic greetings | Time-aware greeting generation |
| **CarbonCreditAgent** | 10003 | Marketplace | Database integration, pricing, negotiations |
| **WalletBalanceAgent** | 10004 | Balance checking | Multi-network wallet support |
| **PaymentAgent** | 10005 | Blockchain payments | Real HBAR/ETH/MATIC transactions |
| **IoTCarbonAgent** | 10006 | IoT processing | Real-time MQTT data, carbon predictions |
| **PrebookingAgent** | 10007 | Prebooking | IoT-based prebooking with prepayment |
| **HederaPaymentAgent** | 10009 | Hedera payments | Autonomous HBAR transfers using Hedera Agent Kit |

## 🏗️ Architecture

### Agent Communication Flow
```
User Request → OrchestratorAgent → Specialized Agent → Response
     ↓              ↓                    ↓              ↓
  Web/CLI    →  LLM Routing    →   Task Processing  →  JSON-RPC
```

### Core Components
- **OrchestratorAgent**: Central hub using Gemini LLM for intelligent routing
- **Specialized Agents**: Domain-specific agents for carbon credits, payments, IoT
- **JSON-RPC 2.0**: Standardized agent-to-agent communication
- **Session Management**: Context-aware conversations across agents

## 📁 Project Structure

```
a2abackend/
├── agents/                     # Individual agent implementations
│   ├── host_agent/            # Orchestrator agent (central hub)
│   │   ├── orchestrator.py    # LLM routing logic
│   │   ├── agent_connect.py   # Agent communication helpers
│   │   └── entry.py          # Server entry point
│   ├── carbon_credit_agent/   # Carbon credit marketplace
│   ├── payment_agent/         # Blockchain payment processing
│   ├── iot_carbon_agent/      # IoT data processing
│   ├── prebooking_agent/      # Carbon credit prebooking
│   ├── wallet_balance_agent/  # Multi-network balance checking
│   ├── greeting_agent/        # Poetic greeting generation
│   └── tell_time_agent/       # Time service
├── server/                   # A2A server infrastructure
│   ├── server.py             # JSON-RPC server implementation
│   └── task_manager.py       # Base task management
├── utilities/                # Shared utilities
│   ├── discovery.py          # Agent discovery service
│   ├── agent_registry.json   # Agent registry configuration
│   └── carbon_marketplace/   # Database schema and logic
├── app/                      # CLI application
│   └── cmd/                  # Command-line interface
├── models/                   # Data models and schemas
├── client/                   # A2A client library
└── pyproject.toml           # Dependencies and configuration
```

## 🚀 Quick Start

### Prerequisites
- **Python 3.11+** with pip
- **PostgreSQL** database (via Docker Compose)
- **Google API Key** for Gemini LLM
- **Blockchain credentials** (optional for testing)

### 1. Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate     # On Windows
```

### 2. Install Dependencies

```bash
# Install all dependencies
pip install -e .

# Or install specific dependencies
pip install fastapi starlette uvicorn google-adk google-genai httpx psycopg2-binary pydantic python-dotenv hedera-sdk-py web3 eth-account requests paho-mqtt
```

### 3. Environment Configuration

```bash
# Copy environment template
cp env.example .env

# Edit .env with your credentials:
# GOOGLE_API_KEY=your_gemini_api_key
# CARBON_MARKETPLACE_DATABASE_URL=postgresql://postgres:password@localhost:5432/carbon_credit_iot
# HEDERA_ACCOUNT_ID=your_hedera_account
# HEDERA_PRIVATE_KEY=your_hedera_private_key
```

### 4. Start Infrastructure

```bash
# Start PostgreSQL, Redis, MQTT broker
docker-compose up -d

# Verify services
docker-compose ps
```

### 5. Start All Agents

```bash
# Start all agents at once (recommended)
./start_all_agents.sh

# Or start individually (make sure venv is activated):
python -m agents.tell_time_agent --host localhost --port 10000
python -m agents.greeting_agent --host localhost --port 10001
python -m agents.carbon_credit_agent --host localhost --port 10003
python -m agents.wallet_balance_agent --host localhost --port 10004
python -m agents.payment_agent --host localhost --port 10005
python -m agents.iot_carbon_agent --host localhost --port 10006
python -m agents.prebooking_agent --host localhost --port 10007
python -m agents.host_agent.entry --host localhost --port 10002
cd agents/hedera_payment_agent && npm run a2a:hedera-payment
```

## 🔧 Manual Setup (Step by Step)

### Complete Setup Process

```bash
# 1. Navigate to backend directory
cd a2abackend

# 2. Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# 3. Install dependencies
pip install -e .

# 4. Set up environment variables
cp env.example .env
# Edit .env file with your API keys

# 5. Start infrastructure (in another terminal)
docker-compose up -d

# 6. Start agents
./start_all_agents.sh
```

---

## 🎬 Demo Walkthrough

### Quick Start (All Agents)
```bash
# Start all agents at once
./start_all_agents.sh
```

### Manual Start (Individual Agents)

**Start the TellTimeAgent**
```bash
python3 -m agents.tell_time_agent \
  --host localhost --port 10000
```

**Start the GreetingAgent**
```bash
python3 -m agents.greeting_agent \
  --host localhost --port 10001
```

**Start the Orchestrator (Host) Agent**
```bash
python3 -m agents.host_agent.entry \
  --host localhost --port 10002
```

**Start the Carbon Credit Agent**
```bash
python3 -m agents.carbon_credit_agent \
  --host localhost --port 10003
```

**Start the Wallet Balance Agent**
```bash
python3 -m agents.wallet_balance_agent \
  --host localhost --port 10004
```

**Start the Payment Agent**
```bash
python3 -m agents.payment_agent \
  --host localhost --port 10005
```

**Start the IoT Carbon Agent**
```bash
python3 -m agents.iot_carbon_agent \
  --host localhost --port 10006
```

**Start the Prebooking Agent**
```bash
python3 -m agents.prebooking_agent \
  --host localhost --port 10007
```

**Start the Hedera Payment Agent**
```bash
cd agents/hedera_payment_agent
npm install
npm run a2a:hedera-payment
```

**Launch the CLI (cmd.py)**
```bash
python3 -m app.cmd.cmd --agent http://localhost:10002
```

**Try it out!**
```bash
> What time is it?
Agent says: The current time is: 2025-05-05 14:23:10

> Greet me
Agent says: Good afternoon, friend! The golden sun dips low...

> Find 100 carbon credits at best price
Agent says: I found several carbon credit offers for you...

> Check balance for wallet 0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6
Agent says: Here's your wallet balance across networks...

> Send 0.001 HBAR to account 0.0.123456
Agent says: Executing HBAR transfer to account 0.0.123456...

> Transfer 1.5 HBAR to 0.0.789012
Agent says: Processing autonomous HBAR transfer using Hedera Agent Kit...
```

## 🏢 Company Onboarding System

### **Company Registration Features**
- **KYC/AML Verification**: Automated business verification process
- **Document Management**: Secure storage of company certificates and licenses
- **Credit Inventory**: Real-time tracking of available carbon credits
- **Pricing Engine**: Dynamic pricing based on market conditions
- **Quality Assurance**: Automated verification of carbon credit authenticity

### **Direct Sales Platform**
- **Company Dashboard**: Management interface for carbon credit sellers
- **Inventory Management**: Track credits, pricing, and sales performance
- **Customer Portal**: B2B sales interface for corporate buyers
- **Transaction Processing**: Secure payment with blockchain integration
- **Reporting Suite**: Sales analytics and compliance tracking

### **Marketplace Integration**
- **Credit Categories**: Forestry, renewable energy, energy efficiency
- **Quality Ratings**: AI-powered assessment of carbon credit quality
- **Bulk Trading**: Large-scale corporate purchases
- **Certification Integration**: VCS, Gold Standard, etc.
- **Escrow Services**: Secure transaction handling

> Get carbon credit forecast from IoT devices
Agent says: Based on real-time IoT data, I predict 150 carbon credits will be generated in the next 24 hours...

> Create a prebooking for TechCorp for 24 hours
Agent says: I'll create a prebooking for TechCorp based on IoT predictions with 5% prepayment discount...
```

---

## 🔍 How It Works

1. **Discovery**: OrchestratorAgent reads `utilities/agent_registry.json`, fetches each agent’s `/​.well-known/agent.json`.
2. **Routing**: Based on intent, the Orchestrator’s LLM calls its tools:
   - `list_agents()` → lists child-agent names
   - `delegate_task(agent_name, message)` → forwards tasks
3. **Child Agents**:
   - TellTimeAgent returns the current time.
   - GreetingAgent calls TellTimeAgent then crafts a poetic greeting.
   - CarbonCreditAgent negotiates carbon credit purchases from database marketplace.
   - WalletBalanceAgent checks wallet balances across Hedera, Ethereum, and Polygon networks.
   - PaymentAgent executes real blockchain transactions across Hedera, Ethereum, and Polygon networks.
   - HederaPaymentAgent provides autonomous HBAR transfers using Hedera Agent Kit with natural language processing.
   - IoTCarbonAgent processes real-time MQTT data from IoT devices and provides carbon credit predictions.
   - PrebookingAgent creates carbon credit prebookings based on IoT predictions with prepayment functionality.
4. **JSON-RPC**: All communication uses A2A JSON-RPC 2.0 over HTTP via Starlette & Uvicorn.

---

## 🌱 IoT Integration & Company-Based System

### **Real-Time IoT Data Processing**
The system integrates with IoT carbon sequestration devices that publish data via MQTT:

- **Company-Based Registration**: Devices register by company name (e.g., "TechCorp", "GreenEnergy", "EcoSolutions")
- **MQTT Topics**: `carbon_sequestration/{company_name}/{message_type}`
  - `sensor_data` - Real-time CO2, humidity, and carbon credit data
  - `alerts` - Critical alerts for high CO2 levels
  - `heartbeat` - Device status and connectivity
  - `commands` - Remote device control

### **IoT Carbon Agent Features**
- **Real-Time Processing**: Listens to MQTT data from multiple companies
- **Carbon Credit Predictions**: Analyzes trends and forecasts future carbon credit generation
- **Company Identification**: Tracks data by company for targeted predictions
- **Alert Processing**: Handles critical alerts and device status monitoring

### **Prebooking Agent Features**
- **IoT Prediction Integration**: Uses IoT Carbon Agent predictions for prebooking decisions
- **Prepayment Processing**: Handles prepayments with 5% discount for early booking
- **Company-Specific Prebookings**: Creates prebookings for specific companies
- **Confidence-Based Validation**: Only creates prebookings when prediction confidence > 70%

### **Instant Carbon Agent Features**
- **Immediate Purchases**: Processes carbon credit purchases instantly without approval
- **Real Blockchain Transactions**: Uses Hedera Payment Agent for actual HBAR transfers
- **Company Validation**: Validates companies through IoT Carbon Agent before purchase
- **Transaction Tracking**: Records all purchases with real blockchain transaction IDs
- **Purchase History**: Maintains complete purchase history with status tracking

### **Simulation & Testing**
```bash
# Simulate IoT data from 3 companies
python simulate_iot_data.py

# Test IoT Carbon Agent directly
curl -X POST http://localhost:10006/ -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "id": "test", "method": "tasks/send", 
       "params": {"id": "test", "sessionId": "test", 
                 "message": {"role": "user", "parts": [{"type": "text", "text": "Get carbon credit forecast"}]}}}'

# Test Prebooking Agent
curl -X POST http://localhost:10007/ -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "id": "test", "method": "tasks/send", 
       "params": {"id": "test", "sessionId": "test", 
                 "message": {"role": "user", "parts": [{"type": "text", "text": "Create prebooking for TechCorp"}]}}}'

# Test Instant Carbon Agent
curl -X POST http://localhost:10008/ -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "id": "test", "method": "tasks/send", 
       "params": {"id": "test", "sessionId": "test", 
                 "message": {"role": "user", "parts": [{"type": "text", "text": "Buy 10 credits from EcoFuture Corp"}]}}}'
```

---

## 📖 Learn More

- A2A GitHub: https://github.com/google/A2A  
- Google ADK: https://github.com/google/agent-development-kit