"""
Prebooking Agent for Carbon Credit Prebooking and Prepayment
Handles automated prebooking based on IoT predictions and prepayment processing
"""

import asyncio
import json
import logging
import httpx
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from google.adk.agents import Agent
from google.adk.tools import FunctionTool

logger = logging.getLogger(__name__)

@dataclass
class PrebookingRequest:
    """Data class for prebooking requests"""
    company_name: str
    predicted_credits: float
    time_horizon: int  # hours
    prepayment_amount: float
    confidence_level: float
    prediction_source: str
    timestamp: datetime

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
    Integrates with IoT Carbon Agent predictions and Payment Agent for transactions
    """
    
    def __init__(self, iot_agent_url: str = "http://localhost:10006", 
                 payment_agent_url: str = "http://localhost:10005",
                 carbon_credit_agent_url: str = "http://localhost:10003"):
        self.iot_agent_url = iot_agent_url
        self.payment_agent_url = payment_agent_url
        self.carbon_credit_agent_url = carbon_credit_agent_url
        
        # In-memory storage for prebookings (in production, use database)
        self.prebookings: Dict[str, PrebookingRecord] = {}
        self.pending_prebookings: List[str] = []
        
        # Prebooking configuration
        self.min_confidence_threshold = 0.7
        self.max_prebooking_hours = 168  # 1 week
        self.prepayment_discount_rate = 0.05  # 5% discount for prepayment
        
        # Initialize agent and runner
        self._runner = self._build_agent()
        self._agent = self._runner.agent
        
        logger.info("🔮 Prebooking Agent initialized")

    async def _make_http_request(self, url: str, method: str = "POST", 
                               data: Dict = None, timeout: int = 30) -> Dict[str, Any]:
        """Make HTTP request to other agents"""
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                if method.upper() == "POST":
                    response = await client.post(url, json=data)
                else:
                    response = await client.get(url)
                
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"❌ HTTP request failed to {url}: {e}")
            return {"error": str(e), "success": False}

    async def get_iot_prediction(self, hours: int = 24) -> Dict[str, Any]:
        """
        Get carbon credit prediction from IoT Carbon Agent
        
        Args:
            hours: Number of hours to predict ahead
            
        Returns:
            Dictionary containing prediction data
        """
        logger.info(f"🔮 Getting IoT prediction for {hours} hours")
        
        request_data = {
            "jsonrpc": "2.0",
            "id": f"prediction-{datetime.now().timestamp()}",
            "method": "tasks/send",
            "params": {
                "id": f"prediction-task-{datetime.now().timestamp()}",
                "sessionId": f"prediction-session-{datetime.now().timestamp()}",
                "message": {
                    "role": "user",
                    "parts": [{"type": "text", "text": f"Get {hours}-hour carbon credit forecast from MQTT data"}]
                }
            }
        }
        
        response = await self._make_http_request(f"{self.iot_agent_url}/", data=request_data)
        
        if "error" in response:
            logger.error(f"❌ Failed to get IoT prediction: {response['error']}")
            return {"error": response["error"], "success": False}
        
        logger.info("✅ IoT prediction retrieved successfully")
        return response

    async def get_available_credits(self) -> Dict[str, Any]:
        """
        Get available carbon credit offers from Carbon Credit Agent
        
        Returns:
            Dictionary containing available credit offers
        """
        logger.info("💰 Getting available carbon credit offers")
        
        request_data = {
            "jsonrpc": "2.0",
            "id": f"credits-{datetime.now().timestamp()}",
            "method": "tasks/send",
            "params": {
                "id": f"credits-task-{datetime.now().timestamp()}",
                "sessionId": f"credits-session-{datetime.now().timestamp()}",
                "message": {
                    "role": "user",
                    "parts": [{"type": "text", "text": "Show me available carbon credit offers"}]
                }
            }
        }
        
        response = await self._make_http_request(f"{self.carbon_credit_agent_url}/", data=request_data)
        
        if "error" in response:
            logger.error(f"❌ Failed to get available credits: {response['error']}")
            return {"error": response["error"], "success": False}
        
        logger.info("✅ Available credits retrieved successfully")
        return response

    async def process_prepayment(self, amount: float, company_name: str) -> Dict[str, Any]:
        """
        Process prepayment through Payment Agent
        
        Args:
            amount: Prepayment amount in HBAR
            company_name: Company making the prepayment
            
        Returns:
            Dictionary containing payment result
        """
        logger.info(f"💳 Processing prepayment of {amount} HBAR for {company_name}")
        
        request_data = {
            "jsonrpc": "2.0",
            "id": f"prepayment-{datetime.now().timestamp()}",
            "method": "tasks/send",
            "params": {
                "id": f"prepayment-task-{datetime.now().timestamp()}",
                "sessionId": f"prepayment-session-{datetime.now().timestamp()}",
                "message": {
                    "role": "user",
                    "parts": [{"type": "text", "text": f"Process prepayment of {amount} HBAR for {company_name} carbon credit prebooking"}]
                }
            }
        }
        
        response = await self._make_http_request(f"{self.payment_agent_url}/", data=request_data)
        
        if "error" in response:
            logger.error(f"❌ Failed to process prepayment: {response['error']}")
            return {"error": response["error"], "success": False}
        
        logger.info("✅ Prepayment processed successfully")
        return response

    async def create_prebooking(self, company_name: str, predicted_credits: float, 
                              time_horizon: int, confidence_level: float) -> Dict[str, Any]:
        """
        Create a new carbon credit prebooking
        
        Args:
            company_name: Name of the company
            predicted_credits: Predicted number of credits
            time_horizon: Time horizon in hours
            confidence_level: Confidence level of prediction (0-1)
            
        Returns:
            Dictionary containing prebooking result
        """
        logger.info(f"📋 Creating prebooking for {company_name}: {predicted_credits} credits over {time_horizon}h")
        
        # Validate inputs
        if confidence_level < self.min_confidence_threshold:
            return {
                "success": False,
                "error": f"Confidence level {confidence_level} below minimum threshold {self.min_confidence_threshold}",
                "message": "Prediction confidence too low for prebooking"
            }
        
        if time_horizon > self.max_prebooking_hours:
            return {
                "success": False,
                "error": f"Time horizon {time_horizon}h exceeds maximum {self.max_prebooking_hours}h",
                "message": "Time horizon too long for prebooking"
            }
        
        # Calculate prepayment amount with discount
        base_price = predicted_credits * 10  # $10 per credit (example)
        prepayment_amount = base_price * (1 - self.prepayment_discount_rate)
        
        # Create prebooking record
        prebooking_id = f"pb_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{company_name.replace(' ', '_')}"
        
        prebooking = PrebookingRecord(
            id=prebooking_id,
            company_name=company_name,
            predicted_credits=predicted_credits,
            actual_credits=None,
            prepayment_amount=prepayment_amount,
            status="pending",
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(hours=time_horizon),
            confidence_level=confidence_level,
            prediction_source="iot_carbon_agent"
        )
        
        # Store prebooking
        self.prebookings[prebooking_id] = prebooking
        self.pending_prebookings.append(prebooking_id)
        
        logger.info(f"✅ Prebooking created: {prebooking_id}")
        
        return {
            "success": True,
            "prebooking_id": prebooking_id,
            "company_name": company_name,
            "predicted_credits": predicted_credits,
            "prepayment_amount": prepayment_amount,
            "discount_rate": self.prepayment_discount_rate,
            "expires_at": prebooking.expires_at.isoformat(),
            "confidence_level": confidence_level,
            "message": f"Prebooking created successfully. Prepayment required: {prepayment_amount:.2f} HBAR"
        }

    async def process_prebooking_request(self, company_name: str, time_horizon: int = 24) -> Dict[str, Any]:
        """
        Process a complete prebooking request including prediction and prepayment
        
        Args:
            company_name: Name of the company
            time_horizon: Time horizon for prediction in hours
            
        Returns:
            Dictionary containing prebooking result
        """
        logger.info(f"🔄 Processing prebooking request for {company_name} ({time_horizon}h)")
        
        try:
            # Step 1: Get IoT prediction
            prediction_result = await self.get_iot_prediction(time_horizon)
            if "error" in prediction_result:
                return {
                    "success": False,
                    "error": "Failed to get prediction",
                    "details": prediction_result["error"]
                }
            
            # Step 2: Extract prediction data (simplified - in real implementation, parse the response)
            predicted_credits = 50.0  # Placeholder - would extract from actual prediction
            confidence_level = 0.85   # Placeholder - would extract from actual prediction
            
            # Step 3: Create prebooking
            prebooking_result = await self.create_prebooking(
                company_name=company_name,
                predicted_credits=predicted_credits,
                time_horizon=time_horizon,
                confidence_level=confidence_level
            )
            
            if not prebooking_result["success"]:
                return prebooking_result
            
            # Step 4: Process prepayment
            prepayment_result = await self.process_prepayment(
                amount=prebooking_result["prepayment_amount"],
                company_name=company_name
            )
            
            if "error" in prepayment_result:
                # Mark prebooking as failed
                prebooking_id = prebooking_result["prebooking_id"]
                if prebooking_id in self.prebookings:
                    self.prebookings[prebooking_id].status = "cancelled"
                
                return {
                    "success": False,
                    "error": "Prepayment failed",
                    "prebooking_id": prebooking_id,
                    "details": prepayment_result["error"]
                }
            
            # Mark prebooking as confirmed
            prebooking_id = prebooking_result["prebooking_id"]
            if prebooking_id in self.prebookings:
                self.prebookings[prebooking_id].status = "confirmed"
            
            logger.info(f"✅ Prebooking completed successfully: {prebooking_id}")
            
            return {
                "success": True,
                "prebooking_id": prebooking_id,
                "company_name": company_name,
                "predicted_credits": predicted_credits,
                "prepayment_amount": prebooking_result["prepayment_amount"],
                "payment_status": "completed",
                "expires_at": prebooking_result["expires_at"],
                "message": f"Prebooking completed successfully for {company_name}"
            }
            
        except Exception as e:
            logger.error(f"❌ Prebooking request failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Prebooking request failed"
            }

    async def get_prebooking_status(self, prebooking_id: str) -> Dict[str, Any]:
        """
        Get status of a specific prebooking
        
        Args:
            prebooking_id: ID of the prebooking
            
        Returns:
            Dictionary containing prebooking status
        """
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
        """
        List all prebookings, optionally filtered by company
        
        Args:
            company_name: Optional company name filter
            
        Returns:
            Dictionary containing list of prebookings
        """
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

    async def cancel_prebooking(self, prebooking_id: str) -> Dict[str, Any]:
        """
        Cancel a prebooking
        
        Args:
            prebooking_id: ID of the prebooking to cancel
            
        Returns:
            Dictionary containing cancellation result
        """
        if prebooking_id not in self.prebookings:
            return {
                "success": False,
                "error": "Prebooking not found",
                "message": f"No prebooking found with ID: {prebooking_id}"
            }
        
        prebooking = self.prebookings[prebooking_id]
        
        if prebooking.status == "completed":
            return {
                "success": False,
                "error": "Cannot cancel completed prebooking",
                "message": "Prebooking has already been completed"
            }
        
        prebooking.status = "cancelled"
        
        logger.info(f"✅ Prebooking cancelled: {prebooking_id}")
        
        return {
            "success": True,
            "prebooking_id": prebooking_id,
            "status": "cancelled",
            "message": f"Prebooking {prebooking_id} has been cancelled"
        }

    def _handle_gemini_error(self, error: Exception) -> str:
        """
        🔧 Handle Gemini API errors with proper logging and user-friendly messages.
        """
        error_str = str(error)
        logger.error(f"🚨 Gemini API Error in Prebooking Agent: {error_str}")

        if "503 UNAVAILABLE" in error_str or "overloaded" in error_str.lower():
            logger.warning("⚠️ Gemini API is overloaded - Prebooking Agent")
            return "The AI service is temporarily overloaded. Please try again in a few moments."
        elif "400 Bad Request" in error_str:
            logger.error("❌ Bad request to Gemini API - Prebooking Agent")
            return "Invalid request format. Please check your input."
        elif "rate limit" in error_str.lower():
            logger.warning("⏰ Rate limit exceeded - Prebooking Agent")
            return "Too many requests. Please wait before trying again."
        else:
            logger.error(f"❌ Unknown Gemini API error in Prebooking Agent: {error_str}")
            return "An unexpected error occurred. Please try again later."

    def _build_agent(self):
        """Build the Prebooking Agent with tools and system instructions"""
        from google.adk.agents.llm_agent import LlmAgent
        from google.adk.sessions import InMemorySessionService
        from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
        from google.adk.artifacts import InMemoryArtifactService
        from google.adk.runners import Runner
        from google.adk.tools import FunctionTool
        
        system_instruction = (
            "You are a Carbon Credit Prebooking Agent. Your role is to help companies "
            "prebook carbon credits based on IoT predictions and process prepayments.\n\n"
            "You have the following capabilities:\n"
            "1) process_prebooking_request(company_name, time_horizon) → Complete prebooking process\n"
            "2) create_prebooking(company_name, predicted_credits, time_horizon, confidence_level) → Create new prebooking\n"
            "3) get_prebooking_status(prebooking_id) → Check status of specific prebooking\n"
            "4) list_prebookings(company_name) → List all prebookings for a company\n"
            "5) cancel_prebooking(prebooking_id) → Cancel a prebooking\n"
            "6) get_iot_prediction(hours) → Get carbon credit prediction from IoT data\n"
            "7) get_available_credits() → Get available carbon credit offers\n"
            "8) process_prepayment(amount, company_name) → Process prepayment\n\n"
            "Prebooking Process:\n"
            "1. Get IoT prediction for specified time horizon\n"
            "2. Validate prediction confidence level\n"
            "3. Create prebooking record with predicted credits\n"
            "4. Calculate prepayment amount with discount\n"
            "5. Process prepayment through Payment Agent\n"
            "6. Confirm prebooking if payment successful\n\n"
            "Key Features:\n"
            "- Minimum confidence threshold: 70%\n"
            "- Maximum prebooking horizon: 1 week (168 hours)\n"
            "- Prepayment discount: 5% off base price\n"
            "- Integration with IoT Carbon Agent for predictions\n"
            "- Integration with Payment Agent for transactions\n"
            "- Integration with Carbon Credit Agent for available offers\n\n"
            "IMPORTANT ERROR HANDLING:\n"
            "- If IoT prediction fails, provide clear error message\n"
            "- If prepayment fails, mark prebooking as cancelled\n"
            "- Log all prebooking attempts with detailed information\n"
            "- When Gemini API throws errors, use _handle_gemini_error method\n"
            "- Always validate confidence levels and time horizons\n"
            "- Provide step-by-step logging for debugging\n\n"
            "Always be helpful, provide clear prebooking information, and confirm "
            "transactions with prebooking IDs when available."
        )
        
        tools = [
            FunctionTool(self.process_prebooking_request),
            FunctionTool(self.create_prebooking),
            FunctionTool(self.get_prebooking_status),
            FunctionTool(self.list_prebookings),
            FunctionTool(self.cancel_prebooking),
            FunctionTool(self.get_iot_prediction),
            FunctionTool(self.get_available_credits),
            FunctionTool(self.process_prepayment),
        ]
        
        # Create the LLM agent
        agent = LlmAgent(
            model="gemini-2.5-flash",
            name="prebooking_agent",
            description="Carbon Credit Prebooking Agent for automated prebooking based on IoT predictions",
            instruction=system_instruction,
            tools=tools
        )
        
        # Create runner
        runner = Runner(
            app_name=agent.name,
            agent=agent,
            artifact_service=InMemoryArtifactService(),
            session_service=InMemorySessionService(),
            memory_service=InMemoryMemoryService(),
        )
        
        return runner

    async def invoke(self, query: str, session_id: str) -> str:
        """
        Handle a user query and return a response string.
        
        Args:
            query: What the user said
            session_id: Session identifier
            
        Returns:
            str: Agent's reply
        """
        from google.genai import types
        
        # Get or create session
        session = await self._runner.session_service.get_session(
            app_name=self._agent.name,
            user_id="prebooking_user",
            session_id=session_id
        )
        
        if session is None:
            session = await self._runner.session_service.create_session(
                app_name=self._agent.name,
                user_id="prebooking_user",
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
        async for event in self._runner.run_async(
            user_id="prebooking_user",
            session_id=session.id,
            new_message=content
        ):
            last_event = event
        
        # Extract response
        if not last_event or not last_event.content or not last_event.content.parts:
            return "I apologize, but I couldn't process your request. Please try again."
        
        return "\n".join([p.text for p in last_event.content.parts if p.text])
