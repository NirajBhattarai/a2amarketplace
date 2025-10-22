# =============================================================================
# agents/payment_agent/__main__.py
# =============================================================================
# 🎯 Purpose:
# Entry point to run the PaymentAgent as a standalone A2A server.
# This allows the agent to be discovered and called by the orchestrator.
# =============================================================================

import logging
import click

# A2A server implementation
from server.server import A2AServer

# Agent and task manager
from agents.payment_agent.agent import PaymentAgent
from agents.payment_agent.task_manager import PaymentTaskManager

# Agent metadata
from models.agent import AgentCard, AgentCapabilities, AgentSkill

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@click.command()
@click.option(
    "--host", default="localhost",
    help="Host to bind the PaymentAgent server to"
)
@click.option(
    "--port", default=10005,
    help="Port for the PaymentAgent server"
)
def main(host: str, port: int):
    """
    Entry point to start the PaymentAgent A2A server.
    
    Steps performed:
    1. Create PaymentAgent instance
    2. Wrap it in PaymentTaskManager for JSON-RPC handling
    3. Define agent metadata (AgentCard)
    4. Launch the A2AServer to listen for incoming tasks
    """
    logger.info("Starting Multi-Network Payment Agent...")

    # 1) Create the PaymentAgent instance
    agent = PaymentAgent()
    
    # 2) Wrap it in a TaskManager for A2A protocol handling
    task_manager = PaymentTaskManager(agent=agent)

    # 3) Define the agent's metadata for discovery
    capabilities = AgentCapabilities(streaming=True, pushNotifications=False)
    
    skill = AgentSkill(
        id="payment_transfer",
        name="Multi-Network Payment Transfer",
        description=(
            "Sends payments across Hedera, Ethereum, and Polygon networks. "
            "Supports native currencies (HBAR, ETH, MATIC) and popular tokens (USDC, USDT)."
        ),
        tags=["payment", "transfer", "hedera", "ethereum", "polygon", "multi-chain", "tokens", "hbars"],
        examples=[
            "Send 5 HBAR to account 0.0.123456",
            "Transfer 0.1 ETH to 0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
            "Send 10 MATIC to 0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
            "Transfer 100 USDC to 0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
            "Send 2.5 HBAR to account 0.0.789012 with memo 'Payment for services'"
        ]
    )
    
    agent_card = AgentCard(
        name="PaymentAgent",
        description="Sends payments across Hedera, Ethereum, and Polygon networks with support for native currencies and ERC20 tokens.",
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
    
    logger.info(f"Multi-Network Payment Agent running on {host}:{port}")
    logger.info(f"Agent Card available at: http://{host}:{port}/.well-known/agent.json")
    
    server.start()


if __name__ == "__main__":
    main()
