# =============================================================================
# agents/iot_carbon_agent/__main__.py
# =============================================================================
# 🎯 Purpose:
# Standalone server entry point for IoT Carbon Sequestration Agent
# =============================================================================

import click
import logging
from .agent import IoTCarbonAgent
from .task_manager import IoTCarbonTaskManager
from server.server import A2AServer
from models.agent import AgentCard, AgentCapabilities, AgentSkill

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@click.command()
@click.option(
    "--host", default="localhost",
    help="Host to bind the IoT Carbon Agent server to"
)
@click.option(
    "--port", default=10006,
    help="Port for the IoT Carbon Agent server"
)
@click.option(
    "--mqtt-broker", default="localhost",
    help="MQTT broker host for IoT device data"
)
@click.option(
    "--mqtt-port", default=1883,
    help="MQTT broker port"
)
def main(host: str, port: int, mqtt_broker: str, mqtt_port: int):
    """
    🚀 Start the IoT Carbon Sequestration Agent server
    
    This agent listens to MQTT from IoT devices, predicts carbon credit generation
    in real-time, and helps companies prepare for carbon credit needs.
    """
    logger.info(f"🌱 Starting IoT Carbon Sequestration Agent on {host}:{port}")
    logger.info(f"📡 MQTT Broker: {mqtt_broker}:{mqtt_port}")

    # Define the IoT Carbon Agent's capabilities and skills
    capabilities = AgentCapabilities(streaming=False)
    skill = AgentSkill(
        id="iot_carbon_sequestration",     # Unique skill identifier
        name="IoT Carbon Sequestration",   # Human-friendly name
        description=(
            "Monitors real-time IoT device data via MQTT to predict carbon credit "
            "generation and help companies prepare for carbon credit needs"
        ),
        tags=["iot", "carbon", "sequestration", "mqtt", "prediction"],  # Keywords for discovery
        examples=[                          # Sample user queries
            "Show me current IoT device data",
            "Predict carbon credits for next 24 hours",
            "Get device status and performance",
            "Analyze carbon sequestration trends",
            "Help me prepare for carbon credit needs"
        ]
    )
    
    # Create agent card for discovery
    agent_card = AgentCard(
        name="IoTCarbonAgent",
        description="Real-time IoT carbon sequestration monitoring and prediction",
        url=f"http://{host}:{port}/",        # Public endpoint
        version="1.0.0",
        defaultInputModes=["text"],          # Supported input modes
        defaultOutputModes=["text"],         # Supported output modes
        capabilities=capabilities,
        skills=[skill]
    )

    # Create the IoT Carbon Agent and its TaskManager
    iot_agent = IoTCarbonAgent(mqtt_broker=mqtt_broker, mqtt_port=mqtt_port)
    task_manager = IoTCarbonTaskManager(agent=iot_agent)

    # Create and start the A2A server
    server = A2AServer(
        host=host,
        port=port,
        agent_card=agent_card,
        task_manager=task_manager
    )
    
    logger.info("🌱 IoT Carbon Sequestration Agent server started successfully!")
    logger.info(f"📡 Agent available at: http://{host}:{port}/")
    logger.info("🔧 Capabilities: Real-time MQTT monitoring, carbon credit prediction, company preparation advice")
    logger.info(f"📊 MQTT Topics: carbon_credit/sensor_data, carbon_credit/commands")
    
    server.start()


if __name__ == "__main__":
    main()
