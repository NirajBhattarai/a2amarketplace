# 🌱 A2A Carbon Credit Marketplace

A comprehensive **Agent-to-Agent (A2A) Carbon Credit Marketplace** with real-time IoT integration, blockchain payments, and AI-powered agent orchestration.

## 🎯 Overview

This system combines **Google's Agent Development Kit (ADK)** with **real-time IoT carbon sequestration monitoring** to create an intelligent marketplace for carbon credit trading. Features include multi-agent AI orchestration, blockchain payment processing, and comprehensive web interface.

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Frontend  │    │   IoT Devices   │    │   Blockchain    │
│   (Next.js)     │    │   (ESP32)       │    │   Networks      │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          │              ┌───────▼───────┐              │
          │              │ MQTT Broker   │              │
          │              │ (Mosquitto)   │              │
          │              └───────┬───────┘              │
          │                      │                      │
          └──────────────────────▼──────────────────────┘
                        ┌─────────────────┐
                        │ A2A Backend     │
                        │ (Python Agents) │
                        └─────────────────┘
```

### **Data Flow Architecture**

This diagram illustrates the end-to-end data flow and interactions between various components of the A2A Carbon Credit Marketplace, from user request to blockchain transaction and real-time IoT monitoring.

![Data Flow Architecture Diagram](assets/images/data-flow.png)

**Explanation of the Flow:**

*   **User Request:** A user initiates a request for carbon credits via the **Web** interface.
*   **Orchestration:** The **Web** routes the request to the **Orchestrator** agent, which is responsible for coordinating the transaction.
*   **Deal Finding:** The **Orchestrator** queries the **CarbonAgent** to find the best carbon credit deals by querying its internal database. The **CarbonAgent** then returns the available offers.
*   **Payment Processing:** Upon selection, the **Orchestrator** instructs the **PaymentAgent** to process the payment. The **PaymentAgent** executes the transaction on the **Blockchain** and receives a confirmation.
*   **Transaction Confirmation:** Once the payment is successful, the **PaymentAgent** notifies the **Orchestrator**, which then informs the **Web** interface to show a confirmation to the **User**.
*   **Real-time Monitoring:** Concurrently, the **IoTAgent** continuously performs "Real-time monitoring" by processing sensor data and sending updates to the **CarbonAgent** to refine carbon predictions.

## 🚀 Key Features

### 🤖 **AI Agent System**
- **OrchestratorAgent**: Central routing hub using Gemini LLM
- **CarbonCreditAgent**: Marketplace management with PostgreSQL
- **PaymentAgent**: Multi-network blockchain transactions
- **IoTCarbonAgent**: Real-time sensor data processing
- **PrebookingAgent**: Carbon credit prebooking with prepayment
- **WalletBalanceAgent**: Multi-network balance checking

### 💰 **Blockchain Integration**
- **Hedera HBAR** transfers with real transaction execution
- **Ethereum ETH** and **Polygon MATIC** support
- **ERC20 token** compatibility (USDC, USDT)
- **Transaction tracking** and status monitoring
- **Address validation** across networks

### 🌱 **IoT Carbon Monitoring**
- **Real-time MQTT** data from ESP32 devices
- **Carbon sequestration** tracking and prediction
- **Company-based** data segregation
- **Critical alert** processing
- **Carbon credit forecasting**

### 💻 **Modern Web Interface**
- **Real-time chat** with AI agents
- **Agent status monitoring** with live indicators
- **Payment interface** for blockchain transactions
- **Responsive design** with Tailwind CSS
- **Quick action buttons** for common queries

## 📁 Project Structure

```
a2amarketplace/
├── a2abackend/                    # Python A2A Backend
│   ├── agents/                   # Individual agent implementations
│   │   ├── host_agent/          # Orchestrator agent
│   │   ├── carbon_credit_agent/ # Carbon credit marketplace
│   │   ├── payment_agent/       # Blockchain payments
│   │   ├── iot_carbon_agent/   # IoT data processing
│   │   ├── prebooking_agent/   # Carbon credit prebooking
│   │   └── wallet_balance_agent/ # Multi-network balances
│   ├── utilities/               # Shared utilities
│   │   ├── carbon_marketplace/ # Database schema & logic
│   │   └── discovery.py         # Agent discovery
│   └── server/                  # A2A server implementation
├── web/                         # Next.js Frontend
│   ├── src/
│   │   ├── components/          # React components
│   │   ├── services/           # A2A client services
│   │   └── app/                # Next.js app router
├── iot_carbon_sequestration/    # IoT Hardware
│   └── creator/                # ESP32 PlatformIO project
├── docker-compose.yml          # Infrastructure setup
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+** with pip
- **Node.js 18+** with npm
- **Docker & Docker Compose** for infrastructure
- **Google API Key** for Gemini LLM
- **Blockchain credentials** (optional for testing)

### 1. Infrastructure Setup

Start the required services using Docker Compose:

```bash
# Start PostgreSQL, Redis, and MQTT broker
docker-compose up -d

# Verify services are running
docker-compose ps
```

### 2. Backend Setup

```bash
cd a2abackend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -e .

# Configure environment
cp env.example .env
# Edit .env with your credentials:
# - GOOGLE_API_KEY=your_gemini_api_key
# - HEDERA_ACCOUNT_ID=your_hedera_account
# - HEDERA_PRIVATE_KEY=your_hedera_private_key
# - CARBON_MARKETPLACE_DATABASE_URL=postgresql://postgres:password@localhost:5432/carbon_credit_iot

# Start all agents (recommended)
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
```

### 3. Frontend Setup

```bash
cd web

# Install dependencies
npm install

# Start development server
npm run dev

# Open http://localhost:3000
```

### 4. IoT Device Setup (Optional)

```bash
# Simulate IoT data
cd a2abackend
python simulate_iot_data.py

# Or flash ESP32 device
cd iot_carbon_sequestration/creator
pio run -t upload
```

## 💬 Usage Examples

### Web Interface
- Open [http://localhost:3000](http://localhost:3000)
- Use the chat interface to interact with agents
- Try quick suggestions like "What time is it?" or "Buy 10 carbon credits"

### CLI Interface
```bash
# Start CLI interface
python -m app.cmd.cmd --agent http://localhost:10002

# Example interactions:
> What time is it?
> Greet me
> Find 100 carbon credits at best price
> Check balance for wallet 0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6
> Send 0.001 HBAR to account 0.0.123456
> Get carbon credit forecast from IoT devices
> Create a prebooking for TechCorp for 24 hours
```

## 🔧 Technical Stack

### Backend Technologies
- **Python 3.11+** with Google ADK
- **FastAPI/Starlette** for web framework
- **PostgreSQL** for data persistence
- **Redis** for caching and sessions
- **MQTT** for IoT communication
- **JSON-RPC 2.0** for agent communication

### Blockchain Integration
- **Hedera SDK** for HBAR transactions
- **Web3.py** for Ethereum/Polygon
- **Multi-network** wallet support
- **Real transaction** execution (testnet)

### Frontend Technologies
- **Next.js 15** with App Router
- **React 19** with TypeScript
- **Tailwind CSS** for styling
- **Real-time** WebSocket communication

### IoT Hardware
- **ESP32** with PlatformIO
- **MQTT** for data transmission
- **OLED display** for local monitoring
- **Sensor simulation** for testing

## 📊 Agent Capabilities

| Agent | Port | Purpose | Key Features |
|-------|------|---------|--------------|
| **OrchestratorAgent** | 10002 | Central routing | LLM-based task delegation |
| **CarbonCreditAgent** | 10003 | Marketplace | Database integration, pricing |
| **PaymentAgent** | 10005 | Blockchain | Multi-network transactions |
| **IoTCarbonAgent** | 10006 | IoT Processing | Real-time MQTT data |
| **PrebookingAgent** | 10007 | Prebooking | Prepayment with discounts |
| **WalletBalanceAgent** | 10004 | Balance Checking | Multi-network support |

## 🧪 Testing

### Payment Testing
```bash
# Test Hedera transactions
python test_single_hedera.py
python test_hedera_direct.py

# Test payment agent
python test_payment_agent.py
```

### IoT Simulation
```bash
# Simulate IoT data from multiple companies
python simulate_iot_data.py

# Monitor MQTT topics
mosquitto_sub -h localhost -t "carbon_sequestration/+/sensor_data"
```

## 🔌 API Endpoints

- `POST /api/agent` - Send messages to A2A agents
- `GET /.well-known/agent.json` - Agent discovery
- `GET /api/health` - Health check endpoint

## 🐳 Infrastructure

### Docker Services
- **PostgreSQL 15** - Database
- **Redis 7** - Caching
- **Mosquitto 2.0** - MQTT Broker
- **pgAdmin** - Database management

### Environment Variables
```bash
# Required
GOOGLE_API_KEY=your_gemini_api_key

# Database
CARBON_MARKETPLACE_DATABASE_URL=postgresql://postgres:password@localhost:5432/carbon_credit_iot

# Blockchain (optional)
HEDERA_ACCOUNT_ID=your_account_id
HEDERA_PRIVATE_KEY=your_private_key
ETHEREUM_PRIVATE_KEY=your_eth_key
POLYGON_PRIVATE_KEY=your_polygon_key
```

## 🏢 Company Onboarding & Direct Sales

### **Company Registration System**
- **Business Verification**: KYC/AML compliance for carbon credit companies
- **Credential Management**: Secure storage of company certificates and licenses
- **Credit Inventory**: Real-time tracking of available carbon credits
- **Pricing Tools**: Dynamic pricing based on market conditions and credit quality
- **Quality Assurance**: Automated verification of carbon credit authenticity

### **Direct Sales Platform**
- **Company Dashboard**: Comprehensive management interface for carbon credit sellers
- **Inventory Management**: Track available credits, pricing, and sales performance
- **Customer Portal**: Direct B2B sales interface for corporate buyers
- **Transaction Processing**: Secure payment processing with blockchain integration
- **Reporting Suite**: Sales analytics, carbon impact reports, and compliance tracking

### **Marketplace Features**
- **Credit Categories**: Forestry, renewable energy, energy efficiency, waste management
- **Quality Ratings**: AI-powered assessment of carbon credit quality and impact
- **Bulk Trading**: Support for large-scale corporate carbon credit purchases
- **Certification Integration**: Direct connection to certification bodies (VCS, Gold Standard, etc.)
- **Escrow Services**: Secure transaction handling with automated settlement

### **Business Model**
- **Commission Structure**: Transparent fee system for transactions
- **Subscription Tiers**: Premium features for enterprise clients
- **API Access**: Developer-friendly APIs for integration
- **White-label Solutions**: Customizable platform for partners
- **Analytics Dashboard**: Real-time market insights and trends

### **Revenue Streams**
- **Transaction Fees**: 2-5% commission on carbon credit sales
- **Subscription Plans**: Monthly/annual plans for premium features
- **API Licensing**: Usage-based pricing for API access
- **Consulting Services**: Implementation and integration support
- **Data Analytics**: Market insights and carbon impact reports
- **Certification Services**: Quality assurance and verification fees

## 🚀 Deployment

### Production Considerations
- **Environment variables** for all secrets
- **Database migrations** for schema updates
- **Health checks** for all services
- **Logging** and monitoring setup
- **SSL/TLS** for secure communication

### Scaling
- **Horizontal scaling** of agents
- **Load balancing** for high availability
- **Database clustering** for performance
- **MQTT clustering** for IoT scale

## 📈 Performance

### Achieved Results
- ✅ **Real Hedera transactions** executed successfully
- ✅ **Multi-agent orchestration** with <2s response time
- ✅ **IoT data processing** with real-time MQTT
- ✅ **Web interface** with live agent monitoring
- ✅ **Database integration** with PostgreSQL

### Benchmarks
- **Agent response time**: <2 seconds
- **MQTT data processing**: Real-time
- **Blockchain transactions**: 3-5 seconds
- **Web interface**: <1 second load time

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- **Google ADK** for agent framework
- **Hedera** for blockchain infrastructure
- **PlatformIO** for IoT development
- **Next.js** for modern web interface