"""
Prebooking Agent for Carbon Credit Prebooking and Prepayment
Handles prebooking with $300 threshold for automatic vs manual approval
"""

import asyncio
import json
import logging
import httpx
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
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

logger = logging.getLogger(__name__)

# Hedera SDK imports - using Hiero SDK Python (no Java dependencies)
HEDERA_SDK_AVAILABLE = False

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
        logger.error("❌ PrebookingAgent cannot function without Hiero SDK Python")
        return False

@dataclass
class PrebookingRecord:
    """Data class for prebooking records"""
    id: str
    company_name: str
    predicted_credits: float
    actual_credits: Optional[float]
    prepayment_amount: float
    status: str  # pending, confirmed, cancelled, completed
    created_at: datetime
    expires_at: datetime
    confidence_level: float
    prediction_source: str

class PrebookingAgent:
    """
    Prebooking Agent for Carbon Credit Prebooking and Prepayment
    Handles prebooking with $300 threshold for automatic vs manual approval
    """
    
    def __init__(self, payment_agent_url: str = "http://localhost:10005", iot_agent_url: str = "http://localhost:10006"):
        self.payment_agent_url = payment_agent_url
        self.iot_agent_url = iot_agent_url
        
        # In-memory storage for prebookings (in production, use database)
        self.prebookings: Dict[str, PrebookingRecord] = {}
        
        # Prebooking configuration
        self.auto_approval_threshold = 300.0  # $300 threshold
        self.prepayment_discount_rate = 0.05  # 5% discount for prepayment
        self.base_price_per_credit = 10.0  # $10 per credit
        
        # Initialize Hedera client
        self._initialize_hedera_client()
        
        # Initialize agent and runner
        self.agent = self._build_agent()
        self.runner = Runner(
            app_name=self.agent.name,
            agent=self.agent,
            artifact_service=InMemoryArtifactService(),
            session_service=InMemorySessionService(),
            memory_service=InMemoryMemoryService(),
        )
        
        # Fixed user_id for session management
        self.user_id = "prebooking_user"
        
        logger.info("🔮 Prebooking Agent initialized")

    def _initialize_hedera_client(self):
        """Initialize Hedera client for HBAR transfers"""
        try:
            # Check if we can use Hiero SDK Python
            _check_hedera_sdk()
            
            # Initialize Hedera configuration
            self.hedera_account_id = os.getenv("OPERATOR_ID", os.getenv("HEDERA_ACCOUNT_ID", "0.0.123456"))
            self.hedera_private_key = os.getenv("OPERATOR_KEY", os.getenv("HEDERA_PRIVATE_KEY", ""))
            self.hedera_network = os.getenv("NETWORK", os.getenv("HEDERA_NETWORK", "testnet"))
            
            # Check if Hiero SDK Python is available
            if not HEDERA_SDK_AVAILABLE:
                logger.error("❌ Hiero SDK Python not available - PrebookingAgent cannot function")
                self.hedera_client = None
                return
            
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
                
        except Exception as e:
            logger.error(f"❌ Error initializing Hedera client: {e}")
            self.hedera_client = None

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
                    "error": "Hiero SDK Python not available. PrebookingAgent cannot function.",
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
            
            # Check for specific error types and provide user-friendly messages
            error_str = str(e)
            if "INSUFFICIENT_PAYER_BALANCE" in error_str:
                return {
                    "success": False,
                    "error": "Insufficient HBAR balance in your account. Please add more HBAR to your testnet account to complete this transaction.",
                    "error_type": "insufficient_balance",
                    "network": "Hedera Network",
                    "destination": destination_account,
                    "amount": amount,
                    "suggestion": "Visit the Hedera testnet faucet to get free testnet HBAR"
                }
            elif "INVALID_ACCOUNT_ID" in error_str:
                return {
                    "success": False,
                    "error": "Invalid destination account ID. Please check the account address.",
                    "error_type": "invalid_account",
                    "network": "Hedera Network",
                    "destination": destination_account,
                    "amount": amount
                }
            else:
                return {
                    "success": False,
                    "error": str(e),
                    "network": "Hedera Network",
                    "destination": destination_account,
                    "amount": amount
                }

    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        return datetime.now().isoformat()

    def _parse_prebooking_request(self, user_input: str) -> Dict[str, Any]:
        """
        Parse user input to extract company name and credit amount
        """
        import re
        
        user_input_lower = user_input.lower()
        
        # Extract credit amount
        credit_amount = 1  # default
        credit_patterns = [
            r'(\d+)\s*credits?',
            r'book\s*(\d+)',
            r'prebook\s*(\d+)',
            r'(\d+)\s*carbon\s*credits?'
        ]
        
        for pattern in credit_patterns:
            match = re.search(pattern, user_input_lower)
            if match:
                credit_amount = int(match.group(1))
                break
        
        # Extract company name
        company_name = None
        
        # Patterns for company extraction
        company_patterns = [
            r'from\s+([A-Za-z\s&.,]+?)(?:\s|$)',
            r'for\s+([A-Za-z\s&.,]+?)(?:\s|$)',
            r'with\s+([A-Za-z\s&.,]+?)(?:\s|$)',
            r'company\s+([A-Za-z\s&.,]+?)(?:\s|$)'
        ]
        
        for pattern in company_patterns:
            match = re.search(pattern, user_input)
            if match:
                company_name = match.group(1).strip()
                # Clean up common suffixes
                company_name = re.sub(r'\s+(?:Ltd|Corp|Inc|LLC|Company)$', '', company_name)
                break
        
        # If no company found, look for capitalized words
        if not company_name:
            words = user_input.split()
            capitalized_words = [word for word in words if word[0].isupper() and len(word) > 2]
            if capitalized_words:
                # Take the first capitalized word as potential company name
                company_name = capitalized_words[0]
        
        return {
            "company_name": company_name,
            "credit_amount": credit_amount,
            "original_input": user_input
        }

    async def _process_payment(self, company_name: str, amount_usd: float, prebooking_id: str) -> Dict[str, Any]:
        """
        Process actual payment via Payment Agent
        """
        try:
            # Convert USD to HBAR (simplified conversion rate)
            hbar_amount = amount_usd / 100  # $1 = 0.01 HBAR for simulation
            
            # Create payment request for Payment Agent
            payment_request = {
                "jsonrpc": "2.0",
                "id": f"payment_{prebooking_id}",
                "method": "tasks/send",
                "params": {
                    "id": f"payment_task_{prebooking_id}",
                    "sessionId": f"prebooking_payment_{prebooking_id}",
                    "message": {
                        "role": "user",
                        "parts": [{
                            "type": "text",
                            "text": f"Send {hbar_amount} HBAR to account 0.0.123456 for prebooking payment to {company_name}"
                        }]
                    }
                }
            }
            
            logger.info(f"💳 Processing payment via Payment Agent: {hbar_amount} HBAR for {company_name}")
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.payment_agent_url}/",
                    json=payment_request,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if "result" in data and "history" in data["result"]:
                        # Extract payment result from response
                        history = data["result"]["history"]
                        if history and len(history) > 0:
                            payment_response = history[-1]["parts"][0]["text"]
                            
                            # Check if payment was successful
                            if "success" in payment_response.lower() or "completed" in payment_response.lower():
                                return {
                                    "success": True,
                                    "transaction_id": f"prebooking_tx_{prebooking_id}",
                                    "amount_hbar": hbar_amount,
                                    "amount_usd": amount_usd,
                                    "status": "completed",
                                    "payment_agent_response": payment_response
                                }
                            else:
                                return {
                                    "success": False,
                                    "error": "Payment failed",
                                    "payment_agent_response": payment_response
                                }
                
                return {
                    "success": False,
                    "error": "Payment agent not available",
                    "message": "Could not process payment - Payment Agent not responding"
                }
                
        except Exception as e:
            logger.error(f"❌ Error processing payment: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Payment processing failed: {str(e)}"
            }

    async def handle_prebooking_request(self, user_input: str) -> Dict[str, Any]:
        """
        Handle prebooking requests with intelligent parsing
        """
        try:
            # Parse the user input
            parsed = self._parse_prebooking_request(user_input)
            company_name = parsed["company_name"]
            credit_amount = parsed["credit_amount"]
            
            logger.info(f"🔍 Parsed prebooking request: Company='{company_name}', Credits={credit_amount}")
            
            # If no company name found, ask user to specify
            if not company_name:
                return {
                    "success": False,
                    "error": "No company specified",
                    "message": "Please specify a company name for the prebooking. For example: 'prebook 2 credits from GreenEarth Ltd' or 'book 1 credit for BlueSky Carbon'"
                }
            
            # Create the prebooking
            result = await self.create_prebooking(company_name, credit_amount, 24)
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error handling prebooking request: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to process prebooking request: {str(e)}"
            }

    async def _check_company_exists(self, company_name: str) -> Dict[str, Any]:
        """
        Check if a company exists in the registered companies list
        by calling the IoT Carbon Agent
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.iot_agent_url}/",
                    json={
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "tasks/send",
                        "params": {
                            "id": f"company_check_{datetime.now().timestamp()}",
                            "sessionId": "prebooking_company_check",
                            "message": {
                                "role": "user",
                                "parts": [{"type": "text", "text": "get_registered_companies()"}]
                            }
                        }
                    },
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if "result" in data and "history" in data["result"]:
                        # Extract company names from the response
                        history = data["result"]["history"]
                        if history and len(history) > 0:
                            response_text = history[-1]["parts"][0]["text"]
                            
                            # Parse company names from the response
                            import re
                            company_names = []
                            
                            # Look for company names in the response
                            if "companies" in response_text.lower():
                                lines = response_text.split('\n')
                                for line in lines:
                                    # Look for company names in markdown format (e.g., **CompanyName**:)
                                    if '**' in line and ':' in line:
                                        # Extract company name from markdown format
                                        match = re.search(r'\*\*([^*]+)\*\*:', line)
                                        if match:
                                            company_name = match.group(1).strip()
                                            # Skip summary lines
                                            if not company_name.lower().startswith('overall') and not company_name.lower().startswith('summary'):
                                                company_names.append(company_name)
                                    elif 'company_name' in line.lower():
                                        # Extract company name from JSON format
                                        match = re.search(r'"company_name":\s*"([^"]+)"', line)
                                        if match:
                                            company_names.append(match.group(1))
                            
                            # Check if the requested company exists
                            company_name_lower = company_name.lower()
                            exact_match = None
                            similar_matches = []
                            
                            for registered_company in company_names:
                                if registered_company.lower() == company_name_lower:
                                    exact_match = registered_company
                                    break
                                elif company_name_lower in registered_company.lower() or registered_company.lower() in company_name_lower:
                                    similar_matches.append(registered_company)
                            
                            if exact_match:
                                return {
                                    "exists": True,
                                    "company_name": exact_match,
                                    "message": f"✅ Company '{exact_match}' is registered and available for prebooking."
                                }
                            elif similar_matches:
                                return {
                                    "exists": False,
                                    "suggestions": similar_matches,
                                    "message": f"❌ Company '{company_name}' not found. Did you mean one of these registered companies: {', '.join(similar_matches)}?"
                                }
                            else:
                                return {
                                    "exists": False,
                                    "suggestions": company_names,
                                    "message": f"❌ Company '{company_name}' not found. Available companies: {', '.join(company_names) if company_names else 'No companies registered yet.'}"
                                }
                
                return {
                    "exists": False,
                    "message": "❌ Unable to check company registration. Please try again."
                }
                
        except Exception as e:
            logger.error(f"Error checking company existence: {e}")
            return {
                "exists": False,
                "message": f"❌ Error checking company registration: {str(e)}"
            }

    async def create_prebooking(
        self, 
        company_name: str, 
        predicted_credits: float, 
        time_horizon: int = 24
    ) -> Dict[str, Any]:
        """
        Create a carbon credit prebooking with $300 threshold logic
        
        Args:
            company_name: Name of the company
            predicted_credits: Predicted number of credits
            time_horizon: Time horizon in hours (default 24)
            
        Returns:
            Dictionary containing prebooking result
        """
        logger.info(f"🔮 Creating prebooking for {company_name}: {predicted_credits} credits")
        
        # First, validate that the company exists
        company_check = await self._check_company_exists(company_name)
        if not company_check["exists"]:
            return {
                "success": False,
                "error": company_check["message"],
                "suggestions": company_check.get("suggestions", [])
            }
        
        # Use the exact company name from the validation
        validated_company_name = company_check.get("company_name", company_name)
        
        # Calculate prepayment amount with discount
        base_price = predicted_credits * self.base_price_per_credit
        prepayment_amount = base_price * (1 - self.prepayment_discount_rate)
        
        # Check if amount is under $300 threshold
        if prepayment_amount < self.auto_approval_threshold:
            logger.info(f"✅ Amount ${prepayment_amount:.2f} is under ${self.auto_approval_threshold} threshold - auto-approving")
            return await self._process_auto_approval(validated_company_name, predicted_credits, prepayment_amount, time_horizon)
        else:
            logger.info(f"⚠️ Amount ${prepayment_amount:.2f} exceeds ${self.auto_approval_threshold} threshold - requires user approval")
            return await self._request_user_approval(validated_company_name, predicted_credits, prepayment_amount, time_horizon)

    async def _process_auto_approval(
        self, 
        company_name: str, 
        predicted_credits: float, 
        prepayment_amount: float, 
        time_horizon: int
    ) -> Dict[str, Any]:
        """Process automatic approval for amounts under $300"""
        try:
            # Create prebooking record
            prebooking_id = f"pb_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{company_name.replace(' ', '_')}"
            
            prebooking = PrebookingRecord(
                id=prebooking_id,
                company_name=company_name,
                predicted_credits=predicted_credits,
                actual_credits=None,
                prepayment_amount=prepayment_amount,
                status="confirmed",
                created_at=datetime.now(),
                expires_at=datetime.now() + timedelta(hours=time_horizon),
                confidence_level=0.85,  # Default confidence
                prediction_source="auto_approved"
            )
            
            # Store prebooking
            self.prebookings[prebooking_id] = prebooking
            
            # Process actual HBAR payment via Payment Agent
            payment_result = await self._process_payment(company_name, prepayment_amount, prebooking_id)
            
            # Check if payment was successful
            if not payment_result.get("success", False):
                # Payment failed - update prebooking status
                prebooking.status = "payment_failed"
                self.prebookings[prebooking_id] = prebooking
                
                logger.error(f"❌ Payment failed for prebooking: {prebooking_id}")
                
                return {
                    "success": False,
                    "prebooking_id": prebooking_id,
                    "company_name": company_name,
                    "predicted_credits": predicted_credits,
                    "prepayment_amount": prepayment_amount,
                    "status": "payment_failed",
                    "payment_result": payment_result,
                    "error": "Payment processing failed",
                    "message": f"Prebooking created but payment failed for {company_name}. Please try again or contact support."
                }
            
            logger.info(f"✅ Auto-approved prebooking with successful payment: {prebooking_id}")
            
            return {
                "success": True,
                "prebooking_id": prebooking_id,
                "company_name": company_name,
                "predicted_credits": predicted_credits,
                "prepayment_amount": prepayment_amount,
                "discount_rate": self.prepayment_discount_rate,
                "expires_at": prebooking.expires_at.isoformat(),
                "status": "auto_approved",
                "payment_result": payment_result,
                "message": f"Prebooking auto-approved and payment processed for {company_name}. Amount ${prepayment_amount:.2f} is under ${self.auto_approval_threshold} threshold."
            }
            
        except Exception as e:
            logger.error(f"❌ Error in auto-approval: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Auto-approval failed"
            }

    async def _request_user_approval(
        self, 
        company_name: str, 
        predicted_credits: float, 
        prepayment_amount: float, 
        time_horizon: int
    ) -> Dict[str, Any]:
        """Request user approval for amounts over $300"""
        try:
            # Create pending prebooking record
            prebooking_id = f"pb_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{company_name.replace(' ', '_')}"
            
            prebooking = PrebookingRecord(
                id=prebooking_id,
                company_name=company_name,
                predicted_credits=predicted_credits,
                actual_credits=None,
                prepayment_amount=prepayment_amount,
                status="pending_approval",
                created_at=datetime.now(),
                expires_at=datetime.now() + timedelta(hours=time_horizon),
                confidence_level=0.85,  # Default confidence
                prediction_source="user_approval_required"
            )
            
            # Store prebooking
            self.prebookings[prebooking_id] = prebooking
            
            logger.info(f"⏳ User approval required for prebooking: {prebooking_id}")
            
            return {
                "success": True,
                "prebooking_id": prebooking_id,
                "company_name": company_name,
                "predicted_credits": predicted_credits,
                "prepayment_amount": prepayment_amount,
                "discount_rate": self.prepayment_discount_rate,
                "expires_at": prebooking.expires_at.isoformat(),
                "status": "pending_approval",
                "requires_approval": True,
                "message": f"Prebooking requires user approval. Amount ${prepayment_amount:.2f} exceeds ${self.auto_approval_threshold} threshold. Please confirm to proceed with payment."
            }
            
        except Exception as e:
            logger.error(f"❌ Error requesting user approval: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to create approval request"
            }

    async def approve_prebooking(self, prebooking_id: str) -> Dict[str, Any]:
        """Approve a pending prebooking and process payment"""
        try:
            if prebooking_id not in self.prebookings:
                return {
                    "success": False,
                    "error": "Prebooking not found",
                    "message": f"No prebooking found with ID: {prebooking_id}"
                }
            
            prebooking = self.prebookings[prebooking_id]
            
            if prebooking.status != "pending_approval":
                return {
                    "success": False,
                    "error": "Prebooking not pending approval",
                    "message": f"Prebooking {prebooking_id} is not pending approval"
                }
            
            # Process actual HBAR payment via Payment Agent
            payment_result = await self._process_payment(prebooking.company_name, prebooking.prepayment_amount, prebooking_id)
            
            # Check if payment was successful
            if not payment_result.get("success", False):
                # Payment failed - update prebooking status
                prebooking.status = "payment_failed"
                self.prebookings[prebooking_id] = prebooking
                
                logger.error(f"❌ Payment failed for prebooking: {prebooking_id}")
                
                return {
                    "success": False,
                    "prebooking_id": prebooking_id,
                    "company_name": prebooking.company_name,
                    "predicted_credits": prebooking.predicted_credits,
                    "prepayment_amount": prebooking.prepayment_amount,
                    "status": "payment_failed",
                    "payment_result": payment_result,
                    "error": "Payment processing failed",
                    "message": f"Prebooking approved but payment failed for {prebooking.company_name}. Please try again or contact support."
                }
            
            # Update prebooking status
            prebooking.status = "confirmed"
            
            logger.info(f"✅ Prebooking approved: {prebooking_id}")
            
            return {
                "success": True,
                "prebooking_id": prebooking_id,
                "company_name": prebooking.company_name,
                "predicted_credits": prebooking.predicted_credits,
                "prepayment_amount": prebooking.prepayment_amount,
                "status": "confirmed",
                "payment_result": payment_result,
                "message": f"Prebooking approved and real HBAR payment processed for {prebooking.company_name}. Transaction ID: {payment_result.get('transaction_id', 'N/A')}"
            }
            
        except Exception as e:
            logger.error(f"❌ Error approving prebooking: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to approve prebooking"
            }

    async def get_prebooking_status(self, prebooking_id: str) -> Dict[str, Any]:
        """Get status of a specific prebooking"""
        if prebooking_id not in self.prebookings:
            return {
                "success": False,
                "error": "Prebooking not found",
                "message": f"No prebooking found with ID: {prebooking_id}"
            }
        
        prebooking = self.prebookings[prebooking_id]
        
        return {
            "success": True,
            "prebooking_id": prebooking_id,
            "company_name": prebooking.company_name,
            "predicted_credits": prebooking.predicted_credits,
            "actual_credits": prebooking.actual_credits,
            "prepayment_amount": prebooking.prepayment_amount,
            "status": prebooking.status,
            "created_at": prebooking.created_at.isoformat(),
            "expires_at": prebooking.expires_at.isoformat(),
            "confidence_level": prebooking.confidence_level,
            "prediction_source": prebooking.prediction_source
        }

    async def list_prebookings(self, company_name: Optional[str] = None) -> Dict[str, Any]:
        """List all prebookings, optionally filtered by company"""
        prebookings_list = []
        
        for prebooking in self.prebookings.values():
            if company_name is None or prebooking.company_name == company_name:
                prebookings_list.append({
                    "prebooking_id": prebooking.id,
                    "company_name": prebooking.company_name,
                    "predicted_credits": prebooking.predicted_credits,
                    "status": prebooking.status,
                    "created_at": prebooking.created_at.isoformat(),
                    "expires_at": prebooking.expires_at.isoformat(),
                    "confidence_level": prebooking.confidence_level
                })
        
        return {
            "success": True,
            "prebookings": prebookings_list,
            "total_count": len(prebookings_list),
            "filter": company_name if company_name else "all"
        }

    def _build_agent(self) -> LlmAgent:
        """Build the Prebooking Agent with tools and system instructions"""
        
        # System instruction for the LLM
        system_instruction = (
            "You are a Carbon Credit Prebooking Agent. Your role is to help companies "
            "prebook carbon credits with intelligent approval logic.\n\n"
            "You have the following capabilities:\n"
            "1) handle_prebooking_request(user_input) → Parse and process prebooking requests\n"
            "2) create_prebooking(company_name, predicted_credits, time_horizon) → Create new prebooking\n"
            "3) approve_prebooking(prebooking_id) → Approve a pending prebooking\n"
            "4) get_prebooking_status(prebooking_id) → Check status of specific prebooking\n"
            "5) list_prebookings(company_name) → List all prebookings for a company\n\n"
            "IMPORTANT PARSING RULES:\n"
            "- When user says 'prebook X credits from CompanyName', extract CompanyName and X\n"
            "- When user says 'book X credits for CompanyName', extract CompanyName and X\n"
            "- When user says 'create prebooking for CompanyName', extract CompanyName and use default 1 credit\n"
            "- If no company name is specified, ask the user to specify a company\n"
            "- If no credit amount is specified, use default 1 credit\n"
            "- Company names should be exact matches to registered companies\n\n"
            "Prebooking Logic:\n"
            "- Amounts under $300: Automatically approved and processed\n"
            "- Amounts over $300: Require user confirmation before processing\n"
            "- 5% discount applied to all prepayments\n"
            "- Base price: $10 per carbon credit\n\n"
            "Key Features:\n"
            "- Automatic approval for amounts under $300\n"
            "- User confirmation required for amounts over $300\n"
            "- Real HBAR payment processing\n"
            "- Prebooking tracking and status management\n\n"
            "Always be helpful, provide clear prebooking information, and explain "
            "the approval process based on the amount threshold."
        )
        
        # Wrap our Python functions into ADK FunctionTool objects
        tools = [
            FunctionTool(self.create_prebooking),
            FunctionTool(self.approve_prebooking),
            FunctionTool(self.get_prebooking_status),
            FunctionTool(self.list_prebookings),
            FunctionTool(self.handle_prebooking_request),
        ]
        
        # Create the LLM agent
        agent = LlmAgent(
            model="gemini-2.5-flash",
            name="prebooking_agent",
            description="Carbon Credit Prebooking Agent for automated prebooking based on IoT predictions",
            instruction=system_instruction,
            tools=tools
        )
        
        return agent

    async def invoke(self, query: str, session_id: str) -> str:
        """
        Handle a user query and return a response string.
        
        Args:
            query: What the user said
            session_id: Session identifier
            
        Returns:
            str: Agent's reply
        """
        # Get or create session
        session = await self.runner.session_service.get_session(
            app_name=self.agent.name,
            user_id=self.user_id,
            session_id=session_id
        )
        
        if session is None:
            session = await self.runner.session_service.create_session(
                app_name=self.agent.name,
                user_id=self.user_id,
                session_id=session_id,
                state={}
            )
        
        # Format the user message
        content = types.Content(
            role="user",
            parts=[types.Part.from_text(text=query)]
        )
        
        # Run the agent
        last_event = None
        async for event in self.runner.run_async(
            user_id=self.user_id,
            session_id=session.id,
            new_message=content
        ):
            last_event = event
        
        # Extract response
        if not last_event or not last_event.content or not last_event.content.parts:
            return "I apologize, but I couldn't process your request. Please try again."
        
        return "\n".join([p.text for p in last_event.content.parts if p.text])