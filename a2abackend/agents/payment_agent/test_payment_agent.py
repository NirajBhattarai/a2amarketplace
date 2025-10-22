#!/usr/bin/env python3
"""
Test script for PaymentAgent to demonstrate HBAR transfer functionality.
This script shows how the agent processes payment requests and executes transfers.
"""

import asyncio
import logging
from agents.payment_agent.agent import PaymentAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_payment_agent():
    """
    Test the PaymentAgent with various payment scenarios.
    WARNING: This will execute REAL blockchain transactions!
    """
    logger.info("🧪 Testing PaymentAgent...")
    logger.warning("⚠️  WARNING: This test will execute REAL blockchain transactions!")
    logger.warning("⚠️  Make sure you're using testnet accounts with test funds only!")
    
    # Create the payment agent
    agent = PaymentAgent()
    
    # Check if blockchain clients are configured
    if hasattr(agent, 'hedera_client') and agent.hedera_client:
        logger.info("🔗 Hedera client detected - REAL transactions will be attempted")
    else:
        logger.error("❌ Hedera client not initialized - check your .env configuration")
        return
    
    # Test scenarios - focusing on Hedera only (Ethereum and Polygon temporarily disabled)
    test_cases = [
        "Send 0.001 HBAR to account 0.0.123456",  # Very small amount
        "Send 0.001 HBAR to account 0.0.789012 with memo 'Test payment'",  # Very small amount
        "Check status of transaction hedera_tx_12345",
        # Temporarily disabled tests
        "Transfer 0.0001 ETH to 0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",  # Will show disabled message
        "Send 0.001 MATIC to 0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",  # Will show disabled message
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        logger.info(f"\n📝 Test Case {i}: {test_case}")
        logger.info("=" * 60)
        
        try:
            # Process the payment request
            response = await agent.invoke(test_case, f"test_session_{i}")
            logger.info(f"✅ Response: {response}")
        except Exception as e:
            logger.error(f"❌ Error: {e}")
        
        logger.info("-" * 60)


async def test_direct_tool_calls():
    """
    Test direct tool calls to demonstrate the underlying functionality.
    """
    logger.info("\n🔧 Testing Direct Tool Calls...")
    
    agent = PaymentAgent()
    
    # Test address validation
    logger.info("\n1. Testing Address Validation:")
    validation_tests = [
        ("0.0.123456", "hedera"),
        ("0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6", "ethereum"),
        ("0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6", "polygon"),
        ("invalid_address", "hedera")
    ]
    
    for address, network in validation_tests:
        is_valid = agent._validate_address_format(address, network)
        logger.info(f"   {address} ({network}): {'✅ Valid' if is_valid else '❌ Invalid'}")
    
    # Test HBAR transfer (mock)
    logger.info("\n2. Testing HBAR Transfer (Mock):")
    try:
        result = await agent._execute_hedera_transfer("0.0.123456", 5.0, "Test payment")
        logger.info(f"   Transfer Result: {result}")
    except Exception as e:
        logger.error(f"   Error: {e}")


async def main():
    """
    Main test function.
    """
    logger.info("🚀 Starting PaymentAgent Tests")
    logger.info("=" * 80)
    
    # Test the agent with natural language requests
    await test_payment_agent()
    
    # Test direct tool functionality
    await test_direct_tool_calls()
    
    logger.info("\n🎉 PaymentAgent Tests Completed!")
    logger.info("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
