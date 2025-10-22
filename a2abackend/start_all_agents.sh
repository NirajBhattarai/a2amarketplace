#!/bin/bash

# A2A Multi-Agent Startup Script
# This script starts all A2A agents in the correct order

echo "🚀 Starting A2A Multi-Agent System..."

# Function to start an agent in the background
start_agent() {
    local agent_name=$1
    local port=$2
    echo "Starting $agent_name on port $port..."
    python3 -m $agent_name --host localhost --port $port &
    sleep 2  # Give each agent time to start
}

# Start all agents
echo "📡 Starting individual agents..."
start_agent "agents.tell_time_agent" "10000"
start_agent "agents.greeting_agent" "10001"
start_agent "agents.carbon_credit_agent" "10003"
start_agent "agents.wallet_balance_agent" "10004"
start_agent "agents.payment_agent" "10005"

echo "🎯 Starting Orchestrator Agent..."
start_agent "agents.host_agent.entry" "10002"

echo "✅ All agents started!"
echo ""
echo "🌐 Available endpoints:"
echo "  - Orchestrator: http://localhost:10002"
echo "  - TellTime: http://localhost:10000"
echo "  - Greeting: http://localhost:10001"
echo "  - Carbon Credit: http://localhost:10003"
echo "  - Wallet Balance: http://localhost:10004"
echo "  - Payment: http://localhost:10005"
echo ""
echo "💸 Payment Agent Features:"
echo "  - Multi-network support (Hedera, Ethereum, Polygon)"
echo "  - Native currency transfers (HBAR, ETH, MATIC)"
echo "  - ERC20 token support (USDC, USDT)"
echo "  - Transaction status checking"
echo "  - Address validation"
echo ""
echo "💬 To interact with the system:"
echo "  python3 -m app.cmd.cmd --agent http://localhost:10002"
echo ""
echo "🌐 Or use the web interface at: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop all agents"
