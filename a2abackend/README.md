# 🌱 Carbon Credit Marketplace & IoT Multi-Agent System – A2A with Google ADK

Welcome to the **Carbon Credit Marketplace & IoT Multi-Agent System** — a comprehensive Agent2Agent (A2A) implementation using Google's [Agent Development Kit (ADK)](https://github.com/google/agent-development-kit) for carbon credit trading with real-time IoT data integration.

This system demonstrates how to build, serve, and interact with seven A2A agents:
1. **TellTimeAgent** – replies with the current time.
2. **GreetingAgent** – fetches the time and generates a poetic greeting.
3. **CarbonCreditAgent** – negotiates carbon credit purchases from marketplace companies.
4. **WalletBalanceAgent** – checks wallet balances across Hedera, Ethereum, and Polygon networks.
5. **PaymentAgent** – executes real blockchain transactions across Hedera, Ethereum, and Polygon networks.
6. **IoTCarbonAgent** – processes real-time IoT carbon sequestration data and provides predictions.
7. **PrebookingAgent** – creates carbon credit prebookings based on IoT predictions with prepayment.
8. **OrchestratorAgent** – routes requests to the appropriate child agent.

All agents work together seamlessly via A2A discovery and JSON-RPC, with real-time IoT data integration for carbon credit forecasting and prebooking.

---

## 📦 Project Structure

```bash
version_3_multi_agent/
├── .env                         # Your GOOGLE_API_KEY (not committed)
├── pyproject.toml              # Dependency config
├── README.md                   # You are reading it!
├── app/
│   └── cmd/
│       └── cmd.py              # CLI to interact with the OrchestratorAgent
├── agents/
│   ├── tell_time_agent/
│   │   ├── __main__.py         # Starts TellTimeAgent server
│   │   ├── agent.py            # Gemini-based time agent
│   │   └── task_manager.py     # In-memory task handler for TellTimeAgent
│   ├── greeting_agent/
│   │   ├── __main__.py         # Starts GreetingAgent server
│   │   ├── agent.py            # Orchestrator that calls TellTimeAgent + LLM greeting
│   │   └── task_manager.py     # Task handler for GreetingAgent
│   ├── carbon_credit_agent/
│   │   ├── __main__.py         # Starts CarbonCreditAgent server
│   │   ├── agent.py            # Carbon credit negotiation agent with database integration
│   │   ├── task_manager.py     # Task handler for CarbonCreditAgent
│   │   └── README.md           # Carbon credit agent documentation
│   ├── wallet_balance_agent/
│   │   ├── __main__.py         # Starts WalletBalanceAgent server
│   │   ├── agent.py            # Multi-network wallet balance checking agent
│   │   └── task_manager.py     # Task handler for WalletBalanceAgent
│   ├── payment_agent/
│   │   ├── __main__.py         # Starts PaymentAgent server
│   │   ├── agent.py            # Multi-network payment execution agent with real blockchain transactions
│   │   ├── task_manager.py     # Task handler for PaymentAgent
│   │   └── test_payment_agent.py # Test script for PaymentAgent
│   ├── iot_carbon_agent/
│   │   ├── __main__.py         # Starts IoTCarbonAgent server
│   │   ├── agent.py            # IoT carbon sequestration data processing and prediction agent
│   │   └── task_manager.py     # Task handler for IoTCarbonAgent
│   ├── prebooking_agent/
│   │   ├── __main__.py         # Starts PrebookingAgent server
│   │   ├── agent.py            # Carbon credit prebooking agent with IoT prediction integration
│   │   └── task_manager.py     # Task handler for PrebookingAgent
│   └── host_agent/
│       ├── entry.py            # CLI to start OrchestratorAgent server
│       ├── orchestrator.py     # LLM router + TaskManager for OrchestratorAgent
│       └── agent_connect.py    # Helper to call child A2A agents
├── server/
│   ├── server.py               # A2A JSON-RPC server implementation
│   └── task_manager.py         # Base in-memory task manager interface
└── utilities/
    ├── discovery.py            # Finds agents via `agent_registry.json`
    └── agent_registry.json     # List of child-agent URLs (one per line)
```

---

## 🛠️ Setup

1. **Clone & navigate**

    ```bash
    git clone https://github.com/theailanguage/a2a_samples.git
    cd a2a_samples/version_3_multi_agent
    ```

2. **Create & activate a venv**

    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3. **Install dependencies**

    Using [`uv`](https://github.com/astral-sh/uv):

    ```bash
    uv pip install .
    ```

    Or with pip directly:

    ```bash
    pip install .
    ```

4. **Set your API key**

    Create `.env` at the project root:
    ```bash
    echo "GOOGLE_API_KEY=your_api_key_here" > .env
    ```

5. **Set up database (for CarbonCreditAgent)**

    Add your PostgreSQL database URL to `.env`:
    ```bash
    echo "CARBON_MARKETPLACE_DATABASE_URL=postgresql://username:password@localhost:5432/carbon_credit_iot" >> .env
    ```

6. **Set up blockchain credentials (for PaymentAgent)**

    Add your blockchain credentials to `.env`:
    ```bash
    echo "HEDERA_ACCOUNT_ID=your_hedera_account_id" >> .env
    echo "HEDERA_PRIVATE_KEY=your_hedera_private_key" >> .env
    echo "ETHEREUM_PRIVATE_KEY=your_ethereum_private_key" >> .env
    echo "POLYGON_PRIVATE_KEY=your_polygon_private_key" >> .env
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
```

---

## 📖 Learn More

- A2A GitHub: https://github.com/google/A2A  
- Google ADK: https://github.com/google/agent-development-kit