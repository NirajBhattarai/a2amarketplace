#!/usr/bin/env python3
"""
Single Hedera Transaction Test
Tests only one Hedera transaction to ensure it works.
"""

import asyncio
import logging
import os
from agents.payment_agent.agent import PaymentAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_single_hedera_transfer():
    """Test a single Hedera transfer"""
    logger.info("🚀 Testing Single Hedera Transfer")
    logger.info("=" * 50)
    
    # Create the payment agent
    agent = PaymentAgent()
    
    # Check if Hedera client is configured
    if hasattr(agent, 'hedera_client') and agent.hedera_client:
        logger.info("✅ Hedera client detected - REAL transaction will be attempted")
    else:
        logger.error("❌ Hedera client not initialized - check your .env configuration")
        return False
    
    # Test a single transfer
    test_message = "Send 0.001 HBAR to account 0.0.123456"
    logger.info(f"📝 Test: {test_message}")
    logger.info("-" * 50)
    
    try:
        response = await agent.invoke(test_message, "single_test_session")
        logger.info(f"✅ Response: {response}")
        return True
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return False

async def main():
    """Main test function"""
    success = await test_single_hedera_transfer()
    
    if success:
        logger.info("\n🎉 SUCCESS! Hedera transfer test completed successfully!")
    else:
        logger.error("\n💥 FAILED! Hedera transfer test failed.")
        exit(1)

if __name__ == "__main__":
    asyncio.run(main())
