# Carbon Credit Negotiation Agent

A Python-based AI agent that negotiates carbon credit purchases by finding the best deals from marketplace companies using Google's ADK and Gemini model.

## Features

- **Database Integration**: Connects to PostgreSQL database to fetch available carbon credit offers
- **Intelligent Negotiation**: Uses Gemini LLM to understand user requests and find optimal deals
- **Price Analysis**: Calculates best offers based on user criteria (amount, price limits, payment methods)
- **A2A Protocol**: Fully compatible with Agent-to-Agent communication protocol
- **Streaming Support**: Supports real-time response streaming

## Architecture

The agent follows the same structure as other agents in the system:

- `agent.py`: Core agent logic with Gemini LLM integration
- `task_manager.py`: A2A protocol handler for JSON-RPC requests
- `__main__.py`: Standalone server entry point

## Database Schema

The agent expects a PostgreSQL database with the following tables:

```sql
-- Company table
CREATE TABLE company (
    company_id SERIAL PRIMARY KEY,
    company_name VARCHAR(255) NOT NULL,
    address VARCHAR(255),
    website VARCHAR(255),
    location VARCHAR(255),
    wallet_address VARCHAR(255) UNIQUE
);

-- Company credit table
CREATE TABLE company_credit (
    credit_id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL,
    total_credit DECIMAL(10,2) NOT NULL,
    current_credit DECIMAL(10,2) NOT NULL,
    sold_credit DECIMAL(10,2) NOT NULL DEFAULT '0.00',
    offer_price DECIMAL(10,2)
);
```

## Environment Variables

Set the following environment variable for database connection:

```bash
CARBON_MARKETPLACE_DATABASE_URL=postgresql://username:password@localhost:5432/carbon_credit_iot
```

## Usage

### Running the Agent

```bash
# From the a2abackend directory
python -m agents.carbon_credit_agent --host localhost --port 10003
```

### Example Queries

- "Find 100 carbon credits at best price"
- "Buy 500 carbon credits for maximum $15 per credit"
- "Get carbon credits from sustainable companies"
- "Negotiate carbon credit purchase with USDC payment"

## API Endpoints

- `GET /.well-known/agent.json`: Agent metadata
- `POST /tasks/send`: Process carbon credit negotiation requests
- `GET /health`: Health check endpoint

## Integration with Orchestrator

The agent is automatically registered with the orchestrator when added to the `agent_registry.json` file. The orchestrator can then route carbon credit requests to this agent.

## Tools Available to the LLM

1. **search_carbon_credits**: Searches database for available carbon credit offers
2. **calculate_negotiation**: Calculates the best deal from available offers

## Response Format

The agent returns structured responses including:
- Available offers with company details
- Pricing analysis and recommendations
- Total cost calculations
- Settlement details and payment methods
