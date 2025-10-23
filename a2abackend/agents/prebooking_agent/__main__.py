"""
Prebooking Agent Entry Point
Starts the Prebooking Agent server for carbon credit prebooking functionality
"""

import argparse
import logging
from server.server import A2AServer
from models.agent import AgentCard, AgentCapabilities, AgentSkill
from .task_manager import PrebookingTaskManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Main entry point for Prebooking Agent"""
    parser = argparse.ArgumentParser(description="Carbon Credit Prebooking Agent")
    parser.add_argument("--host", default="localhost", help="Host to bind to")
    parser.add_argument("--port", type=int, default=10007, help="Port to bind to")
    parser.add_argument("--iot-agent-url", default="http://localhost:10006", 
                       help="IoT Carbon Agent URL")
    parser.add_argument("--payment-agent-url", default="http://localhost:10005", 
                       help="Payment Agent URL")
    parser.add_argument("--carbon-credit-agent-url", default="http://localhost:10003", 
                       help="Carbon Credit Agent URL")
    
    args = parser.parse_args()
    
    logger.info("🔮 Starting Carbon Credit Prebooking Agent...")
    
    # Define capabilities
    capabilities = AgentCapabilities(streaming=False)
    
    # Define the skill this agent offers
    skill = AgentSkill(
        id="carbon_credit_prebooking",
        name="Carbon Credit Prebooking",
        description="Prebook carbon credits based on IoT predictions with prepayment",
        tags=["carbon", "prebooking", "prediction", "prepayment"],
        examples=[
            "Create a prebooking for 24 hours",
            "Process prebooking request for TechCorp",
            "Get prebooking status",
            "List all prebookings"
        ]
    )
    
    # Create agent card
    agent_card = AgentCard(
        name="PrebookingAgent",
        description="Carbon Credit Prebooking Agent for automated prebooking based on IoT predictions",
        url=f"http://{args.host}:{args.port}/",
        version="1.0.0",
        defaultInputModes=["text"],
        defaultOutputModes=["text"],
        capabilities=capabilities,
        skills=[skill]
    )
    
    # Create task manager
    task_manager = PrebookingTaskManager()
    
    # Create and start server
    server = A2AServer(
        host=args.host,
        port=args.port,
        agent_card=agent_card,
        task_manager=task_manager
    )
    
    logger.info(f"🔮 Carbon Credit Prebooking Agent running on {args.host}:{args.port}")
    logger.info(f"🔮 Agent Card available at: http://{args.host}:{args.port}/.well-known/agent.json")
    
    try:
        server.start()
    except KeyboardInterrupt:
        logger.info("🔮 Prebooking Agent stopped by user")
    except Exception as e:
        logger.error(f"❌ Prebooking Agent error: {e}")
        raise

if __name__ == "__main__":
    main()
