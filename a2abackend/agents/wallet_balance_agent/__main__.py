# =============================================================================
# agents/wallet_balance_agent/__main__.py
# =============================================================================
# 🎯 Purpose:
# Entry point to run the WalletBalanceAgent as a standalone A2A server.
# This allows the agent to be discovered and called by the orchestrator.
# =============================================================================

import logging
import click

# A2A server implementation
from server.server import A2AServer

# Agent and task manager
from agents.wallet_balance_agent.agent import WalletBalanceAgent
from agents.wallet_balance_agent.task_manager import WalletBalanceTaskManager

# Agent metadata
from models.agent import AgentCard, AgentCapabilities, AgentSkill

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@click.command()
@click.option(
    "--host", default="localhost",
    help="Host to bind the WalletBalanceAgent server to"
)
@click.option(
    "--port", default=10004,
    help="Port for the WalletBalanceAgent server"
)
def main(host: str, port: int):
    """
    Entry point to start the WalletBalanceAgent A2A server.
    
    Steps performed:
    1. Create WalletBalanceAgent instance
    2. Wrap it in WalletBalanceTaskManager for JSON-RPC handling
    3. Define agent metadata (AgentCard)
    4. Launch the A2AServer to listen for incoming tasks
    """
    logger.info("Starting Multi-Network Wallet Balance Agent...")

    # 1) Create the WalletBalanceAgent instance
    agent = WalletBalanceAgent()
    
    # 2) Wrap it in a TaskManager for A2A protocol handling
    task_manager = WalletBalanceTaskManager(agent=agent)

    # 3) Define the agent's metadata for discovery
    capabilities = AgentCapabilities(streaming=True, pushNotifications=False)
    
    skill = AgentSkill(
        id="wallet_balance_check",
        name="Multi-Network Wallet Balance Check",
        description=(
            "Checks wallet balances across Hedera, Ethereum, and Polygon networks. "
            "Supports native currencies (HBAR, ETH, MATIC) and popular tokens (USDC, USDT)."
        ),
        tags=["wallet", "balance", "hedera", "ethereum", "polygon", "multi-chain", "tokens"],
        examples=[
            "Check balance for wallet 0.0.123456",
            "Get balance for Ethereum address 0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
            "Show my wallet balance across all networks",
            "Check Hedera balance for account 0.0.456789",
            "Get Polygon wallet balance for 0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6"
        ]
    )
    
    agent_card = AgentCard(
        name="WalletBalanceAgent",
        description="Checks wallet balances across Hedera, Ethereum, and Polygon networks with support for native currencies and ERC20 tokens.",
        url=f"http://{host}:{port}/",
        version="1.0.0",
        defaultInputModes=["text"],
        defaultOutputModes=["text", "data"],
        capabilities=capabilities,
        skills=[skill]
    )

    # 4) Create and start the A2A server
    server = A2AServer(
        host=host,
        port=port,
        agent_card=agent_card,
        task_manager=task_manager
    )
    
    logger.info(f"Multi-Network Wallet Balance Agent running on {host}:{port}")
    logger.info(f"Agent Card available at: http://{host}:{port}/.well-known/agent.json")
    
    server.start()


if __name__ == "__main__":
    main()
