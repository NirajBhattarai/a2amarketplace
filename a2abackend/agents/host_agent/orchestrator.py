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

    def _handle_gemini_error(self, error: Exception) -> str:
        """
        🔧 Handle Gemini API errors with proper logging and user-friendly messages.
        """
        error_str = str(error)
        logger.error(f"🚨 Gemini API Error in Orchestrator: {error_str}")
        
        if "503 UNAVAILABLE" in error_str or "overloaded" in error_str.lower():
            logger.warning("⚠️ Gemini API is overloaded - Orchestrator")
            return "The AI service is temporarily overloaded. Please try again in a few moments."
        elif "400 Bad Request" in error_str:
            logger.error("❌ Bad request to Gemini API - Orchestrator")
            return "Invalid request format. Please check your input."
        elif "rate limit" in error_str.lower():
            logger.warning("⏰ Rate limit exceeded - Orchestrator")
            return "Too many requests. Please wait before trying again."
        else:
            logger.error(f"❌ Unknown Gemini API error in Orchestrator: {error_str}")
            return "An unexpected error occurred. Please try again later."

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
        lines.append("IMPORTANT ROUTING RULES:\n")
        lines.append("- For carbon credit purchases ('buy', 'purchase', 'get'): delegate to PaymentAgent\n")
        lines.append("- For FUTURE carbon credit purchases ('prebook', 'create prebooking'): delegate to PrebookingAgent\n")
        lines.append("- PaymentAgent handles immediate purchases with real blockchain transactions\n")
        lines.append("- PrebookingAgent handles future purchases with approval workflows\n")

        
        lines.append("IMPORTANT ROUTING RULES:\n")
        lines.append("- For carbon credit purchases ('buy', 'purchase', 'get'): delegate to PaymentAgent\n")
        lines.append("- For FUTURE carbon credit purchases ('prebook', 'create prebooking'): delegate to PrebookingAgent\n")
        lines.append("- PaymentAgent handles immediate purchases with real blockchain transactions\n")
        lines.append("- PrebookingAgent handles future purchases with approval workflows\n")

        # Agent-specific routing guidance
        lines.append("Routing rules (auto-choose agent; do not ask for data that child agents can derive):")
        if "TellTimeAgent" in names:
            lines.append("- Time requests -> TellTimeAgent (e.g., 'What time is it?').")
        if "GreetingAgent" in names:
            lines.append("- Greetings/salutations -> GreetingAgent.")
        if "WalletBalanceAgent" in names:
            lines.append("- 'Check my wallet balance' or addresses -> WalletBalanceAgent. It uses public testnet RPCs; no API keys required.")
        if "Hedera Payment Agent" in names:
            lines.append("- Hedera HBAR transfers -> Hedera Payment Agent:")
            lines.append("  * When user mentions 'hedera payment agent', 'hedera payment', 'hedera transfer', or 'HBAR transfer' -> delegate to Hedera Payment Agent.")
            lines.append("  * Direct HBAR transfers: 'Send X HBAR to account 0.0.123' -> delegate to Hedera Payment Agent.")
            lines.append("  * Balance checks: 'Check my HBAR balance' -> delegate to Hedera Payment Agent.")
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
            lines.append("  * Company registration: 'show registered companies', 'list companies making carbon credits' -> delegate 'get_registered_companies()'.")
            lines.append("  * Company details: 'which companies are registered', 'show all companies' -> delegate 'get_registered_companies()'.")
        if "IoTCarbonAgent" in names:
            lines.append("- IoT carbon sequestration -> IoTCarbonAgent:")
            lines.append("  * Live data: 'show current IoT device data' -> delegate 'get_live_sensor_data()'.")
            lines.append("  * Predictions: 'predict carbon credits for next 24 hours' -> delegate 'predict_carbon_credits()'.")
            lines.append("  * Device status: 'show IoT device status' -> delegate 'get_device_status()'.")
            lines.append("  * Trends: 'analyze carbon sequestration trends' -> delegate 'analyze_sequestration_trends()'.")
            lines.append("  * Company advice: 'help me prepare for carbon credits' -> delegate 'get_company_preparation_advice()'.")
            lines.append("  * Live companies: 'which companies are generating carbon credits now', 'show companies generating live', 'get live generating companies' -> delegate 'get_live_generating_companies()'.")
        if "PrebookingAgent" in names:
            lines.append("- Carbon credit prebooking -> PrebookingAgent:")
            lines.append("  * Prebooking requests: 'prebook X credits from CompanyName', 'create prebooking for CompanyName' -> delegate text unchanged.")
            lines.append("  * Prebooking management: 'list prebookings', 'get prebooking status', 'approve prebooking' -> delegate text unchanged.")
            lines.append("  * Let PrebookingAgent handle company validation and suggestions internally.")
        if "AutomationAgent" in names:
            lines.append("- Automation and workflows -> AutomationAgent:")
            lines.append("  * Rule management: 'list automation rules', 'enable automation', 'disable automation' -> delegate text unchanged.")
            lines.append("  * Automation status: 'automation status', 'check automation' -> delegate text unchanged.")
            lines.append("  * Workflow creation: 'create automation rule', 'add automation' -> delegate text unchanged.")
            lines.append("  * Scheduled tasks: 'schedule task', 'create schedule' -> delegate text unchanged.")

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
