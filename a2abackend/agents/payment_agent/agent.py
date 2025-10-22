# =============================================================================
# agents/payment_agent/agent.py
# =============================================================================
# 🎯 Purpose:
# A multi-network payment agent that uses Google's ADK and Gemini model
# to help users send payments across Hedera, Ethereum, and Polygon networks.
# =============================================================================

import logging
import re
from typing import List, Dict, Any, Optional
from datetime import datetime
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
import os
from decimal import Decimal

# Create a module-level logger
logger = logging.getLogger(__name__)

# Hedera SDK imports - using Hiero SDK Python (no Java dependencies)
HEDERA_SDK_AVAILABLE = False

# Web3 imports for Ethereum and Polygon
from web3 import Web3
from eth_account import Account
from eth_account.signers.local import LocalAccount

def _check_hedera_sdk():
    """Check if we can use Hiero SDK Python (no Java dependencies)"""
    global HEDERA_SDK_AVAILABLE
    try:
        from hiero_sdk_python import Client, Network, AccountId, PrivateKey, TransferTransaction, Hbar, CryptoGetAccountBalanceQuery
        HEDERA_SDK_AVAILABLE = True
        logger.info("✅ Hiero SDK Python available (no Java dependencies)")
        return True
    except Exception as e:
        HEDERA_SDK_AVAILABLE = False
        logger.error(f"❌ Hiero SDK Python not available: {e}")
        logger.error("❌ PaymentAgent cannot function without Hiero SDK Python")
        return False


class PaymentAgent:
    """
    💸 Multi-Network Payment Agent that:
    - Sends payments across Hedera, Ethereum, and Polygon networks
    - Uses Gemini LLM to understand user requests and provide intelligent responses
    - Supports both native currencies and ERC20 tokens
    - Handles transaction confirmation and status tracking
    """

    # Declare which content types this agent accepts by default
    SUPPORTED_CONTENT_TYPES = ["text", "text/plain"]

    def __init__(self):
        """
        🏗️ Constructor: build the internal LLM agent and runner.
        """
        # Initialize blockchain clients
        self._initialize_blockchain_clients()
        
        # Build the LLM with its tools and system instruction
        self.agent = self._build_agent()

        # A fixed user_id to group all payment calls into one session
        self.user_id = "payment_user"

        # Runner wires together: agent logic, sessions, memory, artifacts
        self.runner = Runner(
            app_name=self.agent.name,
            agent=self.agent,
            artifact_service=InMemoryArtifactService(),
            session_service=InMemorySessionService(),
            memory_service=InMemoryMemoryService(),
        )

    def _initialize_blockchain_clients(self):
        """
        🔗 Initialize blockchain clients for Hedera, Ethereum, and Polygon.
        Uses Hiero SDK Python instead of Java SDK
        """
        try:
            # Check if we can use Hiero SDK Python
            _check_hedera_sdk()
            
            # Initialize Hedera configuration
            self.hedera_account_id = os.getenv("OPERATOR_ID", os.getenv("HEDERA_ACCOUNT_ID", "0.0.123456"))
            self.hedera_private_key = os.getenv("OPERATOR_KEY", os.getenv("HEDERA_PRIVATE_KEY", ""))
            self.hedera_network = os.getenv("NETWORK", os.getenv("HEDERA_NETWORK", "testnet"))
            
            # Check if Hiero SDK Python is available
            if not HEDERA_SDK_AVAILABLE:
                logger.error("❌ Hiero SDK Python not available - PaymentAgent cannot function")
                raise RuntimeError("Required dependencies not available. PaymentAgent cannot start.")
            
            # Initialize Hiero SDK client
            if self.hedera_account_id and self.hedera_private_key:
                try:
                    from hiero_sdk_python import Client, Network, AccountId, PrivateKey
                    
                    # Create network configuration
                    network_config = Network(network=self.hedera_network)
                    
                    # Create Hiero client with network
                    self.hedera_client = Client(network=network_config)
                    
                    # Set operator credentials
                    operator_account_id = AccountId.from_string(self.hedera_account_id)
                    operator_private_key = PrivateKey.from_string(self.hedera_private_key)
                    self.hedera_client.set_operator(operator_account_id, operator_private_key)
                    
                    logger.info("✅ Hiero SDK Python configured successfully")
                    logger.info(f"📋 Account ID: {self.hedera_account_id}")
                    logger.info(f"🌐 Network: {self.hedera_network}")
                except Exception as e:
                    logger.error(f"❌ Failed to initialize Hiero SDK client: {e}")
                    self.hedera_client = None
            else:
                logger.warning("⚠️ Hedera credentials not configured in .env file")
                self.hedera_client = None
            
            # Temporarily disable Ethereum and Polygon clients
            self.ethereum_w3 = None
            self.ethereum_account = None
            self.ethereum_rpc_url = ""
            self.ethereum_private_key = ""
            self.ethereum_chain_id = 0
            logger.info("⚠️ Ethereum client temporarily disabled")
            
            self.polygon_w3 = None
            self.polygon_account = None
            self.polygon_rpc_url = ""
            self.polygon_private_key = ""
            self.polygon_chain_id = 0
            logger.info("⚠️ Polygon client temporarily disabled")
                
        except Exception as e:
            logger.error(f"❌ Error initializing blockchain clients: {e}")
            # Set clients to None to fall back to mock mode
            self.hedera_client = None
            self.ethereum_w3 = None
            self.polygon_w3 = None

    def _build_agent(self) -> LlmAgent:
        """
        🔧 Internal: define the LLM, its system instruction, and wrap tools.
        """

        # --- Tool 1: transfer_hbar ---
        async def transfer_hbar(
            destination_account: str,
            amount: float,
            memo: Optional[str] = None
        ) -> Dict[str, Any]:
            """
            Transfer HBAR tokens on Hedera network.
            
            Args:
                destination_account: Hedera account ID (format: 0.0.123456)
                amount: Amount of HBAR to transfer
                memo: Optional transaction memo
            
            Returns:
                Dictionary containing transaction result
            """
            try:
                result = await self._execute_hedera_transfer(destination_account, amount, memo)
                return result
            except Exception as e:
                logger.error(f"Error transferring HBAR: {e}")
                return {"error": str(e), "success": False}

        # --- Tool 2: transfer_eth ---
        async def transfer_eth(
            destination_address: str,
            amount: float,
            gas_limit: Optional[int] = None
        ) -> Dict[str, Any]:
            """
            Transfer ETH tokens on Ethereum network.
            
            Args:
                destination_address: Ethereum address (format: 0x...)
                amount: Amount of ETH to transfer
                gas_limit: Optional gas limit for transaction
            
            Returns:
                Dictionary containing transaction result
            """
            try:
                result = await self._execute_ethereum_transfer(destination_address, amount, gas_limit)
                return result
            except Exception as e:
                logger.error(f"Error transferring ETH: {e}")
                return {"error": str(e), "success": False}

        # --- Tool 3: transfer_matic ---
        async def transfer_matic(
            destination_address: str,
            amount: float,
            gas_limit: Optional[int] = None
        ) -> Dict[str, Any]:
            """
            Transfer MATIC tokens on Polygon network.
            
            Args:
                destination_address: Polygon address (format: 0x...)
                amount: Amount of MATIC to transfer
                gas_limit: Optional gas limit for transaction
            
            Returns:
                Dictionary containing transaction result
            """
            try:
                result = await self._execute_polygon_transfer(destination_address, amount, gas_limit)
                return result
            except Exception as e:
                logger.error(f"Error transferring MATIC: {e}")
                return {"error": str(e), "success": False}

        # --- Tool 4: validate_payment_address ---
        async def validate_payment_address(
            address: str,
            network: str
        ) -> Dict[str, Any]:
            """
            Validate payment address format for specific network.
            
            Args:
                address: The address to validate
                network: Network to validate against (hedera, ethereum, polygon)
            
            Returns:
                Validation result with details
            """
            try:
                is_valid = self._validate_address_format(address, network)
                return {
                    "is_valid": is_valid,
                    "address": address,
                    "network": network,
                    "message": "Valid address format" if is_valid else "Invalid address format for network"
                }
            except Exception as e:
                logger.error(f"Error validating address: {e}")
                return {"error": str(e)}

        # --- Tool 5: get_transaction_status ---
        async def get_transaction_status(
            transaction_id: str,
            network: str
        ) -> Dict[str, Any]:
            """
            Get the status of a payment transaction.
            
            Args:
                transaction_id: The transaction ID to check
                network: Network where transaction was executed
            
            Returns:
                Transaction status information
            """
            try:
                status = await self._check_transaction_status(transaction_id, network)
                return status
            except Exception as e:
                logger.error(f"Error checking transaction status: {e}")
                return {"error": str(e)}

        # --- Tool 6: get_hedera_balance ---
        async def get_hedera_balance(
            account_id: Optional[str] = None
        ) -> Dict[str, Any]:
            """
            Get HBAR balance for a Hedera account.
            
            Args:
                account_id: Hedera account ID (format: 0.0.123456). If not provided, uses operator account.
            
            Returns:
                Dictionary containing balance information
            """
            try:
                balance = await self._get_hedera_balance(account_id)
                return balance
            except Exception as e:
                logger.error(f"Error getting Hedera balance: {e}")
                return {"error": str(e)}

        # --- System instruction for the LLM ---
        system_instr = (
            "You are a Multi-Network Payment Agent. Your role is to help users "
            "send payments across Hedera, Ethereum, and Polygon networks.\n\n"
            "You have six main tools:\n"
            "1) transfer_hbar(destination_account, amount, memo) → sends HBAR on Hedera network\n"
            "2) transfer_eth(destination_address, amount, gas_limit) → sends ETH on Ethereum network\n"
            "3) transfer_matic(destination_address, amount, gas_limit) → sends MATIC on Polygon network\n"
            "4) validate_payment_address(address, network) → validates address format\n"
            "5) get_transaction_status(transaction_id, network) → checks transaction status\n"
            "6) get_hedera_balance(account_id) → gets HBAR balance for Hedera account\n\n"
            "Supported networks:\n"
            "- Hedera: Use format 0.0.123456 (native HBAR token)\n"
            "- Ethereum: Use format 0x... (native ETH + ERC20 tokens)\n"
            "- Polygon: Use format 0x... (native MATIC + ERC20 tokens)\n\n"
            "When a user requests a payment:\n"
            "1. First, validate the destination address format\n"
            "2. Then, execute the appropriate transfer based on network\n"
            "3. Provide transaction confirmation and status\n"
            "4. Offer to check transaction status if needed\n\n"
            "Always be helpful, provide clear network information, and confirm "
            "transactions with transaction IDs when available."
        )

        # Wrap our Python functions into ADK FunctionTool objects
        tools = [
            FunctionTool(transfer_hbar),
            FunctionTool(transfer_eth),
            FunctionTool(transfer_matic),
            FunctionTool(validate_payment_address),
            FunctionTool(get_transaction_status),
            FunctionTool(get_hedera_balance),
        ]

        # Finally, create and return the LlmAgent with everything wired up
        return LlmAgent(
            model="gemini-2.5-flash",
            name="payment_agent",
            description="Sends payments across Hedera, Ethereum, and Polygon networks with support for native currencies and ERC20 tokens.",
            instruction=system_instr,
            tools=tools,
        )

    def _validate_address_format(self, address: str, network: str) -> bool:
        """
        🔍 Validate payment address format for specific network.
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

    async def _execute_hedera_transfer(
        self, 
        destination_account: str, 
        amount: float, 
        memo: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        🌐 Execute HBAR transfer on Hedera network using Hiero SDK Python
        """
        try:
            # Check if Hiero SDK Python is available
            if not HEDERA_SDK_AVAILABLE:
                return {
                    "success": False,
                    "error": "Hiero SDK Python not available. PaymentAgent cannot function.",
                    "network": "Hedera Network"
                }
            
            if not hasattr(self, 'hedera_client') or not self.hedera_client:
                return {
                    "success": False,
                    "error": "Hedera client not configured. Check your .env configuration.",
                    "network": "Hedera Network"
                }
            
            # Convert HBAR to tinybars (1 HBAR = 100,000,000 tinybars)
            amount_tinybars = int(amount * 100_000_000)
            
            logger.info(f"🔄 Processing real Hedera transfer: {amount} HBAR to {destination_account}")
            logger.info(f"📊 Amount in tinybars: {amount_tinybars}")
            logger.info(f"📤 From: {self.hedera_account_id}")
            logger.info(f"📥 To: {destination_account}")
            
            # Import Hiero SDK classes
            from hiero_sdk_python import TransferTransaction, AccountId, Hbar
            
            # Create transfer transaction using tinybars (integers)
            hbar_transfers = {
                AccountId.from_string(self.hedera_account_id): -amount_tinybars,
                AccountId.from_string(destination_account): amount_tinybars
            }
            
            transaction = TransferTransaction(hbar_transfers=hbar_transfers)
            transaction.transaction_fee = 100000000  # 1 HBAR fee in tinybars
            
            # Add memo if provided
            if memo:
                transaction.set_transaction_memo(memo)
            
            # Execute transaction
            response = transaction.execute(self.hedera_client)
            
            logger.info(f"✅ Transaction executed successfully!")
            logger.info(f"📋 Transaction ID: {response.transaction_id}")
            
            return {
                "success": True,
                "network": f"Hedera {self.hedera_network.title()}",
                "transaction_id": str(response.transaction_id),
                "destination": destination_account,
                "amount": amount,
                "token": "HBAR",
                "memo": memo,
                "status": "completed",
                "timestamp": self._get_timestamp(),
                "note": "Real Hedera transaction using Hiero SDK Python"
            }
            
        except Exception as e:
            logger.error(f"Error executing Hedera transfer: {e}")
            return {
                "success": False,
                "error": str(e),
                "network": "Hedera Network",
                "destination": destination_account,
                "amount": amount
            }

    async def _get_hedera_balance(self, account_id: Optional[str] = None) -> Dict[str, Any]:
        """
        💰 Get HBAR balance for a Hedera account using Hiero SDK Python
        """
        try:
            # Check if Hiero SDK Python is available
            if not HEDERA_SDK_AVAILABLE:
                return {
                    "success": False,
                    "error": "Hiero SDK Python not available. PaymentAgent cannot function.",
                    "network": "Hedera Network"
                }
            
            if not hasattr(self, 'hedera_client') or not self.hedera_client:
                return {
                    "success": False,
                    "error": "Hedera client not configured. Check your .env configuration.",
                    "network": "Hedera Network"
                }
            
            # Use provided account_id or default to operator account
            target_account = account_id or self.hedera_account_id
            
            logger.info(f"💰 Querying Hedera balance for account: {target_account}")
            
            # Import Hiero SDK classes
            from hiero_sdk_python import CryptoGetAccountBalanceQuery, AccountId
            
            # Create balance query
            query = CryptoGetAccountBalanceQuery()
            query.set_account_id(AccountId.from_string(target_account))
            
            # Execute query
            balance = query.execute(self.hedera_client)
            
            logger.info(f"✅ Balance query successful!")
            logger.info(f"📊 Account Balance: {balance.hbars.to_hbars()} HBAR")
            
            return {
                "success": True,
                "network": f"Hedera {self.hedera_network.title()}",
                "account_id": target_account,
                "balance": balance.hbars.to_hbars(),
                "token": "HBAR",
                "timestamp": self._get_timestamp(),
                "note": "Real Hedera balance query using Hiero SDK Python"
            }
            
        except Exception as e:
            logger.error(f"Error querying Hedera balance: {e}")
            return {
                "success": False,
                "error": str(e),
                "network": "Hedera Network",
                "account_id": account_id or self.hedera_account_id
            }

    async def _execute_ethereum_transfer(
        self, 
        destination_address: str, 
        amount: float, 
        gas_limit: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        🔷 Execute ETH transfer on Ethereum network using real Web3.py.
        """
        try:
            # Temporarily disabled
            return {
                "success": False,
                "error": "Ethereum transfers are temporarily disabled. Focus on Hedera transfers first.",
                "network": "Ethereum Network"
            }
            
        except Exception as e:
            logger.error(f"Error executing Ethereum transfer: {e}")
            return {
                "success": False,
                "error": str(e),
                "network": "Ethereum Network",
                "destination": destination_address,
                "amount": amount
            }

    async def _execute_polygon_transfer(
        self, 
        destination_address: str, 
        amount: float, 
        gas_limit: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        🔺 Execute MATIC transfer on Polygon network using real Web3.py.
        """
        try:
            # Temporarily disabled
            return {
                "success": False,
                "error": "Polygon transfers are temporarily disabled. Focus on Hedera transfers first.",
                "network": "Polygon Network"
            }
            
        except Exception as e:
            logger.error(f"Error executing Polygon transfer: {e}")
            return {
                "success": False,
                "error": str(e),
                "network": "Polygon Network",
                "destination": destination_address,
                "amount": amount
            }

    async def _check_transaction_status(
        self, 
        transaction_id: str, 
        network: str
    ) -> Dict[str, Any]:
        """
        📊 Check transaction status on the specified network using real blockchain queries.
        """
        try:
            if network.lower() == "hedera":
                if not self.hedera_client:
                    return {
                        "transaction_id": transaction_id,
                        "network": "Hedera Network",
                        "status": "error",
                        "error": "Hedera client not initialized",
                        "timestamp": self._get_timestamp()
                    }
                
                # Get transaction receipt using the correct API
                from hedera import TransactionId
                
                # Handle test transaction IDs (for testing purposes)
                if transaction_id.startswith("hedera_tx_"):
                    return {
                        "transaction_id": transaction_id,
                        "network": f"Hedera {self.hedera_network.title()}",
                        "status": "test_transaction",
                        "note": "This is a test transaction ID - not a real Hedera transaction",
                        "timestamp": self._get_timestamp()
                    }
                
                tx_id = TransactionId.fromString(transaction_id)
                receipt = self.hedera_client.getTransactionReceipt(tx_id)
                
                return {
                    "transaction_id": transaction_id,
                    "network": f"Hedera {self.hedera_network.title()}",
                    "status": str(receipt.status),
                    "timestamp": self._get_timestamp()
                }
                
            elif network.lower() in ["ethereum", "eth"]:
                return {
                    "transaction_id": transaction_id,
                    "network": "Ethereum Network (Disabled)",
                    "status": "disabled",
                    "error": "Ethereum transfers are temporarily disabled",
                    "timestamp": self._get_timestamp()
                }
                
            elif network.lower() in ["polygon", "matic"]:
                return {
                    "transaction_id": transaction_id,
                    "network": "Polygon Network (Disabled)",
                    "status": "disabled",
                    "error": "Polygon transfers are temporarily disabled",
                    "timestamp": self._get_timestamp()
                }
            else:
                return {"error": f"Unsupported network: {network}"}
                
        except Exception as e:
            logger.error(f"Error checking transaction status: {e}")
            return {
                "transaction_id": transaction_id,
                "network": network,
                "error": str(e),
                "timestamp": self._get_timestamp()
            }

    def _get_timestamp(self) -> str:
        """
        📅 Get current timestamp in ISO format.
        """
        from datetime import datetime
        return datetime.now().isoformat()

    async def invoke(self, query: str, session_id: str) -> str:
        """
        🔄 Public: send a user query through the payment agent pipeline,
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
