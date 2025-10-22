# =============================================================================
# agents/carbon_credit_agent/agent.py
# =============================================================================
# 🎯 Purpose:
# A carbon credit negotiation agent that uses Google's ADK and Gemini model
# to help users find and negotiate carbon credit purchases from a database.
# =============================================================================

import logging
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from decimal import Decimal
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

# Database imports
import psycopg2
from psycopg2.extras import RealDictCursor
import os

# Create a module-level logger
logger = logging.getLogger(__name__)


class CarbonCreditAgent:
    """
    🌱 Carbon Credit Negotiation Agent that:
    - Connects to a PostgreSQL database to find carbon credit offers
    - Uses Gemini LLM to understand user requests and provide intelligent responses
    - Negotiates the best deals for carbon credit purchases
    """

    # Declare which content types this agent accepts by default
    SUPPORTED_CONTENT_TYPES = ["text", "text/plain"]

    def __init__(self):
        """
        🏗️ Constructor: build the internal LLM agent, runner, and database connection.
        """
        # Build the LLM with its tools and system instruction
        self.agent = self._build_agent()

        # A fixed user_id to group all carbon credit calls into one session
        self.user_id = "carbon_credit_user"

        # Runner wires together: agent logic, sessions, memory, artifacts
        self.runner = Runner(
            app_name=self.agent.name,
            agent=self.agent,
            artifact_service=InMemoryArtifactService(),
            session_service=InMemorySessionService(),
            memory_service=InMemoryMemoryService(),
        )

        # Database connection setup
        self.db_connection = self._setup_database_connection()

    def _build_agent(self) -> LlmAgent:
        """
        🔧 Internal: define the LLM, its system instruction, and wrap tools.
        """

        # --- Tool 1: search_carbon_credits ---
        async def search_carbon_credits(
            credit_amount: int,
            max_price_per_credit: Optional[float] = None,
            min_price_per_credit: Optional[float] = None,
            payment_method: str = "USDC"
        ) -> List[Dict[str, Any]]:
            """
            Search for carbon credit offers in the database based on criteria.
            
            Args:
                credit_amount: Number of credits requested
                max_price_per_credit: Maximum price willing to pay per credit
                min_price_per_credit: Minimum price per credit (optional)
                payment_method: Preferred payment method (USDC, USDT, HBAR, BANK_TRANSFER)
            
            Returns:
                List of available carbon credit offers
            """
            try:
                offers = await self._fetch_carbon_credit_offers(
                    credit_amount, max_price_per_credit, min_price_per_credit
                )
                return offers
            except Exception as e:
                logger.error(f"Error searching carbon credits: {e}")
                return []

        # --- Tool 2: calculate_negotiation ---
        async def calculate_negotiation(
            offers: List[Dict[str, Any]],
            requested_credits: int
        ) -> Dict[str, Any]:
            """
            Calculate the best negotiation result from available offers.
            
            Args:
                offers: List of carbon credit offers
                requested_credits: Number of credits requested
            
            Returns:
                Negotiation result with best offers and pricing
            """
            try:
                return await self._calculate_best_deal(offers, requested_credits)
            except Exception as e:
                logger.error(f"Error calculating negotiation: {e}")
                return {"error": str(e)}

        # --- Tool 3: buy_credits_with_hbar ---
        async def buy_credits_with_hbar(
            company_id: int,
            amount: float,
            user_account: str = "0.0.123456",
            payment_tx_id: Optional[str] = None,
        ) -> Dict[str, Any]:
            """
            Record a purchase of carbon credits paid with HBAR. This simulates
            payment by updating the database (deduct current_credit, add sold_credit)
            and creating a row in credit_purchase.

            Args:
                company_id: Target company identifier
                amount: Number of credits to purchase
                user_account: Hedera account ID of buyer
                payment_tx_id: Optional payment tx reference
            """
            try:
                # Local import to avoid hard dependency if utilities not present
                from a2abackend.utilities.carbon_marketplace.purchase import purchase_credits

                success, message = purchase_credits(
                    company_id=company_id,
                    user_account=user_account,
                    amount=Decimal(str(amount)),
                    payment_tx_id=payment_tx_id,
                )
                status = "success" if success else "failed"
                return {"status": status, "message": message}
            except Exception as e:
                logger.error(f"Error buying credits: {e}")
                return {"status": "failed", "message": str(e)}

        # --- System instruction for the LLM ---
        system_instr = (
            "You are a Carbon Credit Negotiation Agent. Your role is to help users find "
            "and negotiate the best carbon credit deals from a marketplace database.\n\n"
            "You have two main tools:\n"
            "1) search_carbon_credits(credit_amount, max_price_per_credit, min_price_per_credit, payment_method) "
            "→ searches the database for available carbon credit offers\n"
            "2) calculate_negotiation(offers, requested_credits) → calculates the best deal from available offers\n"
            "3) buy_credits_with_hbar(company_id, amount, user_account, payment_tx_id) → records a purchase paid with HBAR\n\n"
            "When a user requests carbon credits:\n"
            "1. First, use search_carbon_credits to find available offers\n"
            "2. Then, use calculate_negotiation to determine the best deal\n"
            "3. If the user confirms, call buy_credits_with_hbar to record the simulated purchase\n"
            "4. Present the results in a clear, helpful format\n\n"
            "Always be helpful, transparent about pricing, and provide recommendations "
            "for the best carbon credit deals."
        )

        # Wrap our Python functions into ADK FunctionTool objects
        tools = [
            FunctionTool(search_carbon_credits),
            FunctionTool(calculate_negotiation),
            FunctionTool(buy_credits_with_hbar),
        ]

        # Finally, create and return the LlmAgent with everything wired up
        return LlmAgent(
            model="gemini-2.5-flash",
            name="carbon_credit_agent",
            description="Negotiates carbon credit purchases by finding the best deals from marketplace companies.",
            instruction=system_instr,
            tools=tools,
        )

    def _setup_database_connection(self):
        """
        🔗 Setup database connection for carbon credit data.
        """
        try:
            # Get database URL from environment or use default
            db_url = os.getenv('CARBON_MARKETPLACE_DATABASE_URL', 
                             'postgresql://postgres:password@localhost:5432/carbon_credit_iot')
            
            # Parse connection parameters
            conn = psycopg2.connect(db_url)
            logger.info("Database connection established")
            return conn
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            return None

    async def _fetch_carbon_credit_offers(
        self, 
        credit_amount: int, 
        max_price: Optional[float] = None,
        min_price: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        🔍 Fetch carbon credit offers from the database.
        """
        if not self.db_connection:
            logger.error("No database connection available")
            return []

        try:
            with self.db_connection.cursor(cursor_factory=RealDictCursor) as cursor:
                # Build the query with optional price filters
                query = """
                    SELECT 
                        c.company_id,
                        c.company_name,
                        c.wallet_address,
                        cc.current_credit,
                        cc.offer_price,
                        cc.total_credit,
                        cc.sold_credit
                    FROM company c
                    INNER JOIN company_credit cc ON c.company_id = cc.company_id
                    WHERE cc.current_credit >= %s
                """
                params = [credit_amount * 0.01]  # At least 1% of requested amount
                
                if max_price:
                    query += " AND (cc.offer_price IS NULL OR cc.offer_price <= %s)"
                    params.append(max_price)
                
                if min_price:
                    query += " AND (cc.offer_price IS NULL OR cc.offer_price >= %s)"
                    params.append(min_price)
                
                query += " ORDER BY cc.offer_price ASC"
                
                cursor.execute(query, params)
                results = cursor.fetchall()
                
                # Convert to list of dictionaries
                offers = []
                for row in results:
                    offers.append({
                        'company_id': row['company_id'],
                        'company_name': row['company_name'],
                        'wallet_address': row['wallet_address'],
                        'current_credit': float(row['current_credit']),
                        'offer_price': float(row['offer_price']) if row['offer_price'] else None,
                        'total_credit': float(row['total_credit']),
                        'sold_credit': float(row['sold_credit'])
                    })
                
                logger.info(f"Found {len(offers)} carbon credit offers")
                return offers
                
        except Exception as e:
            logger.error(f"Error fetching carbon credit offers: {e}")
            return []

    async def _calculate_best_deal(
        self, 
        offers: List[Dict[str, Any]], 
        requested_credits: int
    ) -> Dict[str, Any]:
        """
        💰 Calculate the best deal from available offers.
        """
        if not offers:
            return {
                "status": "failed",
                "message": "No carbon credit offers found",
                "total_credits_found": 0,
                "requested_credits": requested_credits
            }

        # Sort offers by price (ascending)
        sorted_offers = sorted(
            [offer for offer in offers if offer['offer_price'] is not None],
            key=lambda x: x['offer_price']
        )

        best_offers = []
        total_credits_found = 0
        total_cost = 0
        remaining_credits = requested_credits

        # Select best offers to fulfill the request
        for offer in sorted_offers:
            if remaining_credits <= 0:
                break
            
            credits_to_take = min(remaining_credits, offer['current_credit'])
            if credits_to_take > 0:
                best_offers.append({
                    **offer,
                    'credits_to_purchase': credits_to_take,
                    'total_cost': credits_to_take * offer['offer_price']
                })
                
                total_credits_found += credits_to_take
                total_cost += credits_to_take * offer['offer_price']
                remaining_credits -= credits_to_take

        average_price = total_cost / total_credits_found if total_credits_found > 0 else 0
        
        # Generate recommendations
        recommendations = []
        if total_credits_found < requested_credits:
            recommendations.append(
                f"Only found {total_credits_found} credits out of {requested_credits} requested. "
                "Consider increasing your maximum price per credit."
            )
        
        if average_price > 0:
            best_price = min(offer['offer_price'] for offer in best_offers)
            recommendations.append(
                f"Average price: ${average_price:.2f} per credit. "
                f"Best deal: ${best_price:.2f} per credit."
            )
        
        if len(best_offers) > 1:
            recommendations.append(
                f"Diversified across {len(best_offers)} companies for risk mitigation."
            )

        return {
            "status": "success" if total_credits_found >= requested_credits * 0.8 else "partial",
            "total_credits_found": total_credits_found,
            "requested_credits": requested_credits,
            "best_offers": best_offers,
            "average_price": average_price,
            "total_cost": total_cost,
            "recommendations": recommendations,
            "negotiation_id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat()
        }

    async def invoke(self, query: str, session_id: str) -> str:
        """
        🔄 Public: send a user query through the carbon credit agent pipeline,
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
