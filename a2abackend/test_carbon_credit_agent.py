#!/usr/bin/env python3
"""
Test script for the Carbon Credit Negotiation Agent
"""

import asyncio
import logging
from agents.carbon_credit_agent.agent import CarbonCreditAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_carbon_credit_agent():
    """Test the carbon credit agent with sample queries."""
    
    # Create agent instance
    agent = CarbonCreditAgent()
    
    # Test queries
    test_queries = [
        "Find 100 carbon credits at best price",
        "Buy 500 carbon credits for maximum $15 per credit",
        "Get carbon credits from sustainable companies",
        "Negotiate carbon credit purchase with USDC payment"
    ]
    
    for query in test_queries:
        logger.info(f"\n{'='*50}")
        logger.info(f"Testing query: {query}")
        logger.info(f"{'='*50}")
        
        try:
            response = await agent.invoke(query, "test_session")
            logger.info(f"Response: {response}")
        except Exception as e:
            logger.error(f"Error processing query: {e}")
        
        # Small delay between queries
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(test_carbon_credit_agent())
