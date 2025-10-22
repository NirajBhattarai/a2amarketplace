# =============================================================================
# agents/wallet_balance_agent/agent.py
# =============================================================================
# 🎯 Purpose:
# A multi-network wallet balance agent that uses Google's ADK and Gemini model
# to help users check wallet balances across Hedera, Ethereum, and Polygon networks.
# =============================================================================

import logging
import re
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

# Google ADK imports
from google.adk.agents.llm_agent import LlmAgent
from google.adk.sessions import InMemorySessionService
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from google.adk.artifacts import InMemoryArtifactService
from google.adk.runners import Runner
from google.genai import types
from google.adk.tools.function_tool import FunctionTool

# Web3 imports for blockchain interactions
import requests
import json

# Create a module-level logger
logger = logging.getLogger(__name__)


class WalletBalanceAgent:
    """
    💰 Multi-Network Wallet Balance Agent that:
    - Checks wallet balances across Hedera, Ethereum, and Polygon networks
    - Uses Gemini LLM to understand user requests and provide intelligent responses
    - Supports both native currencies and ERC20 tokens
    """

    # Declare which content types this agent accepts by default
    SUPPORTED_CONTENT_TYPES = ["text", "text/plain"]

    def __init__(self):
        """
        🏗️ Constructor: build the internal LLM agent and runner.
        """
        # Build the LLM with its tools and system instruction
        self.agent = self._build_agent()

        # A fixed user_id to group all wallet balance calls into one session
        self.user_id = "wallet_balance_user"

        # Runner wires together: agent logic, sessions, memory, artifacts
        self.runner = Runner(
            app_name=self.agent.name,
            agent=self.agent,
            artifact_service=InMemoryArtifactService(),
            session_service=InMemorySessionService(),
            memory_service=InMemoryMemoryService(),
        )

    def _build_agent(self) -> LlmAgent:
        """
        🔧 Internal: define the LLM, its system instruction, and wrap tools.
        """

        # --- Tool 1: check_wallet_balance ---
        async def check_wallet_balance(
            wallet_address: str,
            network: Optional[str] = None
        ) -> Dict[str, Any]:
            """
            Check wallet balance across supported networks.
            
            Args:
                wallet_address: The wallet address to check (0x... for Ethereum/Polygon, 0.0.123456 for Hedera)
                network: Specific network to check (hedera, ethereum, polygon) or None for all
            
            Returns:
                Dictionary containing balance information across networks
            """
            try:
                balance_result = await self._fetch_wallet_balance(wallet_address, network)
                return balance_result
            except Exception as e:
                logger.error(f"Error checking wallet balance: {e}")
                return {"error": str(e)}

        # --- Tool 2: validate_wallet_address ---
        async def validate_wallet_address(
            wallet_address: str,
            network: str
        ) -> Dict[str, Any]:
            """
            Validate wallet address format for specific network.
            
            Args:
                wallet_address: The wallet address to validate
                network: Network to validate against (hedera, ethereum, polygon)
            
            Returns:
                Validation result with details
            """
            try:
                is_valid = self._validate_address_format(wallet_address, network)
                return {
                    "is_valid": is_valid,
                    "address": wallet_address,
                    "network": network,
                    "message": "Valid address format" if is_valid else "Invalid address format for network"
                }
            except Exception as e:
                logger.error(f"Error validating address: {e}")
                return {"error": str(e)}

        # --- System instruction for the LLM ---
        system_instr = (
            "You are a Multi-Network Wallet Balance Agent. Your role is to help users "
            "check their wallet balances across Hedera, Ethereum, and Polygon networks.\n\n"
            "You have two main tools:\n"
            "1) check_wallet_balance(wallet_address, network) → checks balance across networks\n"
            "2) validate_wallet_address(wallet_address, network) → validates address format\n\n"
            "Supported networks:\n"
            "- Hedera: Use format 0.0.123456 (native HBAR token)\n"
            "- Ethereum: Use format 0x... (native ETH + ERC20 tokens like USDC, USDT)\n"
            "- Polygon: Use format 0x... (native MATIC + ERC20 tokens like USDC, USDT)\n\n"
            "When a user requests wallet balance:\n"
            "1. First, validate the wallet address format\n"
            "2. Then, check the balance across supported networks\n"
            "3. Present the results in a clear, helpful format with USD values\n\n"
            "Always be helpful, provide clear network information, and show both native "
            "and token balances when available."
        )

        # Wrap our Python functions into ADK FunctionTool objects
        tools = [
            FunctionTool(check_wallet_balance),
            FunctionTool(validate_wallet_address),
        ]

        # Finally, create and return the LlmAgent with everything wired up
        return LlmAgent(
            model="gemini-2.5-flash",
            name="wallet_balance_agent",
            description="Checks wallet balances across Hedera, Ethereum, and Polygon networks with support for native currencies and ERC20 tokens.",
            instruction=system_instr,
            tools=tools,
        )

    def _validate_address_format(self, address: str, network: str) -> bool:
        """
        🔍 Validate wallet address format for specific network.
        """
        if network.lower() == "hedera":
            # Hedera account format: 0.0.123456
            pattern = r'^\d+\.\d+\.\d+$'
            return bool(re.match(pattern, address))
        elif network.lower() in ["ethereum", "polygon"]:
            # Ethereum/Polygon address format: 0x followed by 40 hex characters
            pattern = r'^0x[a-fA-F0-9]{40}$'
            return bool(re.match(pattern, address))
        return False

    async def _fetch_wallet_balance(
        self, 
        wallet_address: str, 
        network: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        🔍 Fetch wallet balance across supported networks.
        """
        networks_to_check = []
        
        if network:
            networks_to_check = [network.lower()]
        else:
            # Check all supported networks
            networks_to_check = ["hedera", "ethereum", "polygon"]

        results = {}
        total_usd_value = 0

        for net in networks_to_check:
            try:
                if net == "hedera":
                    balance_data = await self._get_hedera_balance(wallet_address)
                elif net == "ethereum":
                    balance_data = await self._get_ethereum_balance(wallet_address)
                elif net == "polygon":
                    balance_data = await self._get_polygon_balance(wallet_address)
                else:
                    continue

                if balance_data:
                    results[net] = balance_data
                    total_usd_value += balance_data.get("total_usd_value", 0)

            except Exception as e:
                logger.error(f"Error fetching {net} balance: {e}")
                results[net] = {"error": str(e)}

        return {
            "wallet_address": wallet_address,
            "networks": results,
            "total_usd_value": total_usd_value,
            "timestamp": self._get_timestamp()
        }

    async def _get_hedera_balance(self, wallet_address: str) -> Dict[str, Any]:
        """
        🌐 Get Hedera network balance (mock implementation).
        """
        # Mock implementation - in production, use Hedera SDK
        return {
            "network": "Hedera Network",
            "native_balance": {
                "token": "HBAR",
                "balance": "1000.0",
                "usd_value": 50.0
            },
            "total_usd_value": 50.0,
            "status": "success"
        }

    async def _get_ethereum_balance(self, wallet_address: str) -> Dict[str, Any]:
        """
        🔷 Get Ethereum network balance (mock implementation).
        """
        # Mock implementation - in production, use Web3.py or ethers.js
        return {
            "network": "Ethereum Mainnet",
            "native_balance": {
                "token": "ETH",
                "balance": "2.5",
                "usd_value": 5000.0
            },
            "token_balances": [
                {
                    "token": "USDC",
                    "balance": "1000.0",
                    "usd_value": 1000.0
                }
            ],
            "total_usd_value": 6000.0,
            "status": "success"
        }

    async def _get_polygon_balance(self, wallet_address: str) -> Dict[str, Any]:
        """
        🔺 Get Polygon network balance (mock implementation).
        """
        # Mock implementation - in production, use Web3.py or ethers.js
        return {
            "network": "Polygon Network",
            "native_balance": {
                "token": "MATIC",
                "balance": "500.0",
                "usd_value": 400.0
            },
            "token_balances": [
                {
                    "token": "USDT",
                    "balance": "500.0",
                    "usd_value": 500.0
                }
            ],
            "total_usd_value": 900.0,
            "status": "success"
        }

    def _get_timestamp(self) -> str:
        """
        📅 Get current timestamp in ISO format.
        """
        from datetime import datetime
        return datetime.now().isoformat()

    async def invoke(self, query: str, session_id: str) -> str:
        """
        🔄 Public: send a user query through the wallet balance agent pipeline,
        ensuring session reuse or creation, and return the final text reply.
        """
        # 1) Try to fetch an existing session
        session = await self.runner.session_service.get_session(
            app_name=self.agent.name,
            user_id=self.user_id,
            session_id=session_id,
        )

        # 2) If not found, create a new session with empty state
        if session is None:
            session = await self.runner.session_service.create_session(
                app_name=self.agent.name,
                user_id=self.user_id,
                session_id=session_id,
                state={},
            )

        # 3) Wrap the user's text in a Gemini Content object
        content = types.Content(
            role="user",
            parts=[types.Part.from_text(text=query)]
        )

        # 🚀 Run the agent using the Runner and collect the last event
        last_event = None
        async for event in self.runner.run_async(
            user_id=self.user_id,
            session_id=session.id,
            new_message=content
        ):
            last_event = event

        # 🧹 Fallback: return empty string if something went wrong
        if not last_event or not last_event.content or not last_event.content.parts:
            return ""

        # 📤 Extract and join all text responses into one string
        return "\n".join([p.text for p in last_event.content.parts if p.text])

    async def stream(self, query: str, session_id: str):
        """
        🌀 Simulates a "streaming" agent that returns a single reply.
        """
        result = await self.invoke(query, session_id)
        yield {
            "is_task_complete": True,
            "content": result
        }
