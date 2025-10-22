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
                FunctionTool(self._buy_credits_hbar)           # Tool 3: pay with HBAR then record purchase
            ],
        )

    def _root_instruction(self, context: ReadonlyContext) -> str:
        """
        System prompt function: returns instruction text for the LLM,
        including which tools it can use and a list of child agents.
        """
        # Build a bullet-list of agent names
        agent_list = "\n".join(f"- {name}" for name in self.connectors)
        return (
            "You are an orchestrator with tools:\n"
            "- _list_agents() -> list available child agents\n"
            "- _delegate_task(agent_name, message) -> call that agent with a text command\n"
            "- _buy_credits_hbar(credits, company_id=0, company_name='', company_wallet='', price_per_credit=0.0, buyer_account='', memo_prefix='Carbon credits purchase') ->\n"
            "  pay HBAR via PaymentAgent and record purchase with CarbonCreditAgent.\n\n"
            "Rules for carbon credit flow:\n"
            "- Supported payment is HBAR only.\n"
            "- If the user says 'buy' or 'go and pay', DO NOT prompt for buyer account or company wallet.\n"
            "  Auto-resolve company (id, wallet, price) from marketplace DB and use the PaymentAgent buyer account\n"
            "  from environment (OPERATOR_ID/HEDERA_ACCOUNT_ID). Proceed to pay then record the purchase.\n"
            "- Maintain conversation context across turns.\n\n"
            "Available agents:\n" + agent_list
        )

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

    async def _buy_credits_hbar(
        self,
        credits: float,
        company_id: int = 0,
        company_name: str = "",
        company_wallet: str = "",
        price_per_credit: float = 0.0,
        buyer_account: str = "",
        memo_prefix: str = "Carbon credits purchase"
    ) -> str:
        """
        Orchestrate an end-to-end HBAR purchase:
        1) Pay HBAR to company via PaymentAgent
        2) Record purchase with CarbonCreditAgent (updates DB)
        """
        # Resolve connectors
        if "PaymentAgent" not in self.connectors:
            raise ValueError("PaymentAgent not available")
        if "CarbonCreditAgent" not in self.connectors:
            raise ValueError("CarbonCreditAgent not available")

        payment = self.connectors["PaymentAgent"]
        carbon = self.connectors["CarbonCreditAgent"]

        # If details missing, look up from DB utilities
        if company_id == 0 or not company_wallet or price_per_credit <= 0.0:
            try:
                try:
                    from a2abackend.utilities.carbon_marketplace.db import fetch_all  # type: ignore
                except ImportError:
                    from ...utilities.carbon_marketplace.db import fetch_all  # type: ignore
                params = []
                filters = []
                if company_name:
                    filters.append("c.company_name ILIKE %s")
                    params.append(f"%{company_name}%")
                query = (
                    "SELECT c.company_id, c.company_name, c.wallet_address, cc.offer_price "
                    "FROM company c INNER JOIN company_credit cc ON c.company_id = cc.company_id "
                )
                if filters:
                    query += "WHERE " + " AND ".join(filters) + " "
                query += "ORDER BY cc.offer_price ASC LIMIT 1"
                rows = fetch_all(query, params)
                if rows:
                    row = rows[0]
                    company_id = company_id or int(row["company_id"])  # type: ignore[index]
                    company_wallet = company_wallet or str(row["wallet_address"])  # type: ignore[index]
                    price_per_credit = price_per_credit or float(row["offer_price"])  # type: ignore[index]
            except Exception as e:
                logger.error(f"DB lookup failed: {e}")

        # Final compute total HBAR and memo
        total_hbar = float(credits) * float(price_per_credit)
        memo = f"{memo_prefix} company={company_id} credits={credits}"

        # Session continuity
        session_id = str(uuid.uuid4())

        # 1) Pay with PaymentAgent (text command)
        pay_text = (
            f"Send {total_hbar} HBAR to account {company_wallet} with memo '{memo}'"
        )
        pay_task = await payment.send_task(pay_text, session_id)
        tx_text = pay_task.history[-1].parts[0].text if pay_task.history else ""

        # Try to extract a tx id; if not found, reuse memo as fallback
        tx_id = None
        for token in tx_text.replace("\n", " ").split(" "):
            if "tx" in token.lower() or "hedera_" in token.lower():
                tx_id = token.strip(".,;:")
                break
        if not tx_id:
            tx_id = memo

        # 2) Record purchase with CarbonCreditAgent
        buyer = buyer_account or os.getenv("OPERATOR_ID") or os.getenv("HEDERA_ACCOUNT_ID") or "0.0.123456"
        record_text = (
            f"buy_credits_with_hbar(company_id={company_id}, amount={credits}, user_account='{buyer}', payment_tx_id='{tx_id}')"
        )
        record_task = await carbon.send_task(record_text, session_id)
        record_reply = record_task.history[-1].parts[0].text if record_task.history else ""

        return (
            f"Paid {total_hbar} HBAR to {company_wallet} (tx: {tx_id}). "
            f"Recorded purchase: {record_reply}"
        )

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
