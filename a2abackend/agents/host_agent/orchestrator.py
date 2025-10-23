# =============================================================================
# agents/host_agent/orchestrator.py
# =============================================================================
# 🎯 Purpose:
# Defines the OrchestratorAgent that uses a Gemini-based LLM to interpret user
# queries and delegate them to any child A2A agent discovered at startup.
# Also defines OrchestratorTaskManager to expose this logic via JSON-RPC.
# =============================================================================

import os                           # Standard library for interacting with the operating system
import uuid                         # For generating unique identifiers (e.g., session IDs)
import logging                      # Standard library for configurable logging
import json                         # For persisting session history to disk
from pathlib import Path            # Cross-platform path utilities
from dotenv import load_dotenv      # Utility to load environment variables from a .env file

# Load the .env file so that environment variables like GOOGLE_API_KEY
# are available to the ADK client when creating LLMs
load_dotenv()

# -----------------------------------------------------------------------------
# Google ADK / Gemini imports
# -----------------------------------------------------------------------------
from google.adk.agents.llm_agent import LlmAgent
# LlmAgent: core class to define a Gemini-powered AI agent

from google.adk.tools.function_tool import FunctionTool
# FunctionTool: wraps Python functions as LLM tools

from google.adk.sessions import InMemorySessionService
# InMemorySessionService: stores session state in memory (for simple demos)

from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
# InMemoryMemoryService: optional conversation memory stored in RAM

from google.adk.artifacts import InMemoryArtifactService
# InMemoryArtifactService: handles file/blob artifacts (unused here)

from google.adk.runners import Runner
# Runner: orchestrates agent, sessions, memory, and tool invocation

from google.adk.agents.readonly_context import ReadonlyContext
# ReadonlyContext: passed to system prompt function to read context

from google.adk.tools.tool_context import ToolContext
# ToolContext: passed to tool functions for state and actions

from google.genai import types           
# types.Content & types.Part: used to wrap user messages for the LLM

# -----------------------------------------------------------------------------
# A2A server-side infrastructure
# -----------------------------------------------------------------------------
from server.task_manager import InMemoryTaskManager
# InMemoryTaskManager: base class providing in-memory task storage and locking

from models.request import SendTaskRequest, SendTaskResponse
# Data models for incoming task requests and outgoing responses

from models.task import Message, TaskStatus, TaskState, TextPart
# Message: encapsulates role+parts; TaskStatus/State: status enums; TextPart: text payload

# -----------------------------------------------------------------------------
# Connector to child A2A agents
# -----------------------------------------------------------------------------
from agents.host_agent.agent_connect import AgentConnector
# AgentConnector: lightweight wrapper around A2AClient to call other agents

from models.agent import AgentCard
# AgentCard: metadata structure for agent discovery results

# Set up module-level logger for debug/info messages
logger = logging.getLogger(__name__)


class OrchestratorAgent:
    """
    🤖 Uses a Gemini LLM to route incoming user queries,
    calling out to any discovered child A2A agents via tools.
    """

    # Define supported MIME types for input/output
    SUPPORTED_CONTENT_TYPES = ["text", "text/plain"]

    def __init__(self, agent_cards: list[AgentCard]):
        # Build one AgentConnector per discovered AgentCard
        # agent_cards is a list of AgentCard objects returned by discovery
        self.connectors = {
            card.name: AgentConnector(card.name, card.url)
            for card in agent_cards
        }

        # Build the internal LLM agent with our custom tools and instructions
        self._agent = self._build_agent()

        # Static user ID for session tracking across calls
        self._user_id = "orchestrator_user"

        # Runner wires up sessions, memory, artifacts, and handles agent.run()
        self._runner = Runner(
            app_name=self._agent.name,
            agent=self._agent,
            artifact_service=InMemoryArtifactService(),
            session_service=InMemorySessionService(),
            memory_service=InMemoryMemoryService(),
        )

    def _build_agent(self) -> LlmAgent:
        """
        Construct the Gemini-based LlmAgent with:
        - Model name
        - Agent name/description
        - System instruction callback
        - Available tool functions
        """
        return LlmAgent(
            model="gemini-2.5-flash",    # Specify Gemini model version
            name="orchestrator_agent",          # Human identifier for this agent
            description="Delegates user queries to child A2A agents based on intent.",
            instruction=self._root_instruction,  # Function providing system prompt text
            tools=[
                FunctionTool(self._list_agents),               # Tool 1: list available child agents
                FunctionTool(self._delegate_task),             # Tool 2: call a child agent
            ],
        )

    def _root_instruction(self, context: ReadonlyContext) -> str:
        """
        System prompt function: returns instruction text for the LLM,
        including which tools it can use and a list of child agents.
        """
        # Build dynamic agent summary and delegation rules
        names = set(self.connectors.keys())
        lines: list[str] = []

        lines.append("You are an Orchestrator. Use tools to delegate user intents to child agents.\n")
        lines.append("Tools:\n- _list_agents() -> list available child agents\n- _delegate_task(agent_name, message) -> send a text command to that agent\n")
        lines.append("IMPORTANT: For carbon credit purchases, ALWAYS delegate to PaymentAgent using _delegate_task('PaymentAgent', 'buy_carbon_credits(amount=X)') - do NOT ask for company names, let PaymentAgent handle it.\n")

        # Agent-specific routing guidance
        lines.append("Routing rules (auto-choose agent; do not ask for data that child agents can derive):")
        if "TellTimeAgent" in names:
            lines.append("- Time requests -> TellTimeAgent (e.g., 'What time is it?').")
        if "GreetingAgent" in names:
            lines.append("- Greetings/salutations -> GreetingAgent.")
        if "WalletBalanceAgent" in names:
            lines.append("- 'Check my wallet balance' or addresses -> WalletBalanceAgent. It uses public testnet RPCs; no API keys required.")
        if "PaymentAgent" in names:
            lines.append("- Direct HBAR/ETH/MATIC transfers -> PaymentAgent (text commands like 'Send 1 HBAR to account 0.0.123').")
            lines.append("- Carbon credit purchases -> PaymentAgent:")
            lines.append("  * When user says 'buy N credits' or 'purchase credits' -> delegate to PaymentAgent with 'buy_carbon_credits(amount=N)' (optionally include company_name).")
            lines.append("  * PaymentAgent will get company details from CarbonCreditAgent, process payment, and record purchase.")
        if "CarbonCreditAgent" in names:
            lines.append("- Carbon credits marketplace info -> CarbonCreditAgent:")
            lines.append("  * Discovery: 'Find 100 carbon credits at best price' -> delegate text unchanged.")
            lines.append("  * Quick list: 'show offers' -> delegate 'list_offers(limit=10)'.")
            lines.append("  * Company details: 'get company details for X' -> delegate 'get_company_details(company_name=X)'.")
        if "IoTCarbonAgent" in names:
            lines.append("- IoT carbon sequestration -> IoTCarbonAgent:")
            lines.append("  * Live data: 'show current IoT device data' -> delegate 'get_live_sensor_data()'.")
            lines.append("  * Predictions: 'predict carbon credits for next 24 hours' -> delegate 'predict_carbon_credits()'.")
            lines.append("  * Device status: 'show IoT device status' -> delegate 'get_device_status()'.")
            lines.append("  * Trends: 'analyze carbon sequestration trends' -> delegate 'analyze_sequestration_trends()'.")
            lines.append("  * Company advice: 'help me prepare for carbon credits' -> delegate 'get_company_preparation_advice()'.")
        # Check for movie search agent (could be named "Movie Search Agent" or similar)
        movie_agent = None
        for name in names:
            if "Movie" in name or "movie" in name:
                movie_agent = name
                break
        
        if movie_agent:
            lines.append(f"- Movie searches and recommendations -> {movie_agent}:")
            lines.append("  * Movie search: 'Find action movies', 'Search for Inception' -> delegate text unchanged.")
            lines.append("  * Actor search: 'Find Leonardo DiCaprio movies' -> delegate text unchanged.")
            lines.append("  * Recommendations: 'Recommend movies like The Matrix' -> delegate text unchanged.")

        lines.append("\nGeneral rules:")
        lines.append("- Maintain conversation context across turns using the same session.")
        lines.append("- Prefer not to re-ask for details that a child agent can compute or look up (DB, discovery, or defaults).")

        # Append discovered agents list
        agent_list = "\n".join(f"- {name}" for name in self.connectors)
        lines.append("\nDiscovered agents:\n" + agent_list)

        return "\n".join(lines)

    def _list_agents(self) -> list[str]:
        """
        Tool function: returns the list of child-agent names currently registered.
        Called by the LLM when it wants to discover available agents.
        """
        return list(self.connectors.keys())

    async def _delegate_task(
        self,
        agent_name: str,
        message: str,
        tool_context: ToolContext
    ) -> str:
        """
        Tool function: forwards the `message` to the specified child agent
        (via its AgentConnector), waits for the response, and returns the
        text of the last reply.
        """
        # Validate agent_name exists
        if agent_name not in self.connectors:
            raise ValueError(f"Unknown agent: {agent_name}")
        connector = self.connectors[agent_name]

        # Ensure session_id persists across tool calls via tool_context.state
        state = tool_context.state
        if "session_id" not in state:
            state["session_id"] = str(uuid.uuid4())
        session_id = state["session_id"]

        # Delegate task asynchronously and await Task result
        child_task = await connector.send_task(message, session_id)

        # Extract text from the last history entry if available
        if child_task.history and len(child_task.history) > 1:
            return child_task.history[-1].parts[0].text
        return ""


    async def invoke(self, query: str, session_id: str) -> str:
        """
        Main entry: receives a user query + session_id,
        sets up or retrieves a session, wraps the query for the LLM,
        runs the Runner (with tools enabled), and returns the final text.
        Note - function updated 28 May 2025
        Summary of changes:
        1. Agent's invoke method is made async
        2. All async calls (get_session, create_session, run_async) 
            are awaited inside invoke method
        3. task manager's on_send_task updated to await the invoke call

        Reason - get_session and create_session are async in the 
        "Current" Google ADK version and were synchronous earlier 
        when this lecture was recorded. This is due to a recent change 
        in the Google ADK code 
        https://github.com/google/adk-python/commit/1804ca39a678433293158ec066d44c30eeb8e23b

        """
        # Attempt to reuse an existing session
        session = await self._runner.session_service.get_session(
            app_name=self._agent.name,
            user_id=self._user_id,
            session_id=session_id
        )
        # Create new if not found
        if session is None:
            session = await self._runner.session_service.create_session(
                app_name=self._agent.name,
                user_id=self._user_id,
                session_id=session_id,
                state={}
            )

        # Wrap the user query in a types.Content message
        content = types.Content(
            role="user",
            parts=[types.Part.from_text(text=query)]
        )

        # 🚀 Run the agent using the Runner and collect the last event
        last_event = None
        async for event in self._runner.run_async(
            user_id=self._user_id,
            session_id=session.id,
            new_message=content
        ):
            last_event = event

        # 🧹 Fallback: return empty string if something went wrong
        if not last_event or not last_event.content or not last_event.content.parts:
            return ""

        # 📤 Extract and join all text responses into one string
        return "\n".join([p.text for p in last_event.content.parts if p.text])


class OrchestratorTaskManager(InMemoryTaskManager):
    """
    🪄 TaskManager wrapper: exposes OrchestratorAgent.invoke() over the
    A2A JSON-RPC `tasks/send` endpoint, handling in-memory storage and
    response formatting.
    """
    def __init__(self, agent: OrchestratorAgent):
        super().__init__()       # Initialize base in-memory storage
        self.agent = agent       # Store our orchestrator logic

    def _get_user_text(self, request: SendTaskRequest) -> str:
        """
        Helper: extract the user's raw input text from the request object.
        """
        return request.params.message.parts[0].text

    async def on_send_task(self, request: SendTaskRequest) -> SendTaskResponse:
        """
        Called by the A2A server when a new task arrives:
        1. Store the incoming user message
        2. Invoke the OrchestratorAgent to get a response
        3. Append response to history, mark completed
        4. Return a SendTaskResponse with the full Task
        """
        logger.info(f"OrchestratorTaskManager received task {request.params.id}")

        # Step 1: save the initial message
        task = await self.upsert_task(request.params)

        # Step 2: run orchestration logic
        user_text = self._get_user_text(request)
        response_text = await self.agent.invoke(user_text, request.params.sessionId)

        # Step 3: wrap the LLM output into a Message
        reply = Message(role="agent", parts=[TextPart(text=response_text)])
        async with self.lock:
            task.status = TaskStatus(state=TaskState.COMPLETED)
            task.history.append(reply)

        # Step 4: return structured response
        return SendTaskResponse(id=request.id, result=task)
