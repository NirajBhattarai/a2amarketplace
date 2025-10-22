# Carbon Credit Agent - UI Integration

The Carbon Credit Agent has been fully integrated into the web UI. Here's how to use it:

## 🌱 Quick Start

1. **Start the Carbon Credit Agent**:
   ```bash
   cd a2abackend
   python -m agents.carbon_credit_agent --host localhost --port 10003
   ```

2. **Start the Web UI**:
   ```bash
   cd web
   npm run dev
   ```

3. **Open the browser**: Navigate to [http://localhost:3000](http://localhost:3000)

## 🎯 Features in the UI

### Chat Interface
- **Quick Message Buttons**: 
  - 🌱 "Find Carbon Credits" - Searches for 100 credits at best price
  - 💰 "Negotiate Credits" - Negotiates 500 credits with $15 max price
- **Custom Messages**: Type any carbon credit request like:
  - "Find 200 carbon credits from sustainable companies"
  - "Buy 1000 credits with USDC payment"
  - "Get carbon credits at maximum $20 per credit"

### Agent Discovery
- The Carbon Credit Agent appears in the **Status** tab
- Shows real-time availability status
- Displays agent capabilities and description

### Server Monitoring
- **Status Tab**: Monitor all agents including CarbonCreditAgent
- **Agent Selector**: Choose specific agents for direct communication
- **Real-time Updates**: Automatic discovery and status monitoring

## 🔧 Configuration

The Carbon Credit Agent is configured in:
- `src/config/agent.ts` - Agent endpoints
- `src/services/AgentDiscovery.ts` - Discovery ports
- `src/components/AgentChat.tsx` - Quick message buttons

## 📊 Expected Behavior

When you send carbon credit requests:

1. **Agent Discovery**: The UI automatically discovers the agent at `localhost:10003`
2. **Request Processing**: Messages are sent to the orchestrator which routes to the Carbon Credit Agent
3. **Response Format**: The agent returns structured responses with:
   - Available carbon credit offers
   - Pricing analysis and recommendations
   - Company details and settlement information
   - Best deal calculations

## 🚨 Prerequisites

- **Database**: PostgreSQL with carbon credit schema
- **Environment**: Set `CARBON_MARKETPLACE_DATABASE_URL`
- **Dependencies**: All Python dependencies installed

## 🎨 UI Enhancements

The UI now includes:
- **Carbon Credit Quick Buttons**: Easy access to common requests
- **Agent Status Monitoring**: Real-time status of all agents
- **Enhanced Discovery**: Automatic detection of Carbon Credit Agent
- **Improved Messaging**: Better handling of structured responses

## 🔍 Troubleshooting

If the Carbon Credit Agent doesn't appear:
1. Check that the agent is running on port 10003
2. Verify database connection
3. Check browser console for discovery errors
4. Ensure all dependencies are installed

The Carbon Credit Agent is now fully integrated and ready to handle carbon credit negotiation requests through the beautiful web interface! 🌱
