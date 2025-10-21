# =============================================================================
# agents/carbon_credit_agent/__main__.py
# =============================================================================
# 🎯 Purpose:
# Entry point to run the CarbonCreditAgent as a standalone A2A server.
# This allows the agent to be discovered and called by the orchestrator.
# =============================================================================

import logging
import click

# A2A server implementation
from server.server import A2AServer

# Agent and task manager
from agents.carbon_credit_agent.agent import CarbonCreditAgent
from agents.carbon_credit_agent.task_manager import CarbonCreditTaskManager

# Agent metadata
from models.agent import AgentCard, AgentCapabilities, AgentSkill

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@click.command()
@click.option(
    "--host", default="localhost",
    help="Host to bind the CarbonCreditAgent server to"
)
@click.option(
    "--port", default=10003,
    help="Port for the CarbonCreditAgent server"
)
def main(host: str, port: int):
    """
    Entry point to start the CarbonCreditAgent A2A server.
    
    Steps performed:
    1. Create CarbonCreditAgent instance
    2. Wrap it in CarbonCreditTaskManager for JSON-RPC handling
    3. Define agent metadata (AgentCard)
    4. Launch the A2AServer to listen for incoming tasks
    """
    logger.info("Starting Carbon Credit Negotiation Agent...")

    # 1) Create the CarbonCreditAgent instance
    agent = CarbonCreditAgent()
    
    # 2) Wrap it in a TaskManager for A2A protocol handling
    task_manager = CarbonCreditTaskManager(agent=agent)

    # 3) Define the agent's metadata for discovery
    capabilities = AgentCapabilities(streaming=True, pushNotifications=False)
    
    skill = AgentSkill(
        id="carbon_credit_negotiation",
        name="Carbon Credit Negotiation",
        description=(
            "Finds and negotiates the best carbon credit deals from marketplace companies. "
            "Searches database for available credits and calculates optimal pricing."
        ),
        tags=["carbon", "credits", "negotiation", "environment", "sustainability"],
        examples=[
            "Find 100 carbon credits at best price",
            "Buy 500 carbon credits for maximum $15 per credit",
            "Get carbon credits from sustainable companies",
            "Negotiate carbon credit purchase with USDC payment"
        ]
    )
    
    agent_card = AgentCard(
        name="CarbonCreditAgent",
        description="Negotiates carbon credit purchases by finding the best deals from marketplace companies.",
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
    
    logger.info(f"Carbon Credit Negotiation Agent running on {host}:{port}")
    logger.info(f"Agent Card available at: http://{host}:{port}/.well-known/agent.json")
    
    server.start()


if __name__ == "__main__":
    main()
