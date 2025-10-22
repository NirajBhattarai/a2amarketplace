#!/usr/bin/env python3
"""
Test script for Payment Agent with Hiero SDK Python integration
"""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_payment_agent():
    """Test the payment agent with real Hedera transactions"""
    try:
        from agents.payment_agent.agent import PaymentAgent
        
        print("🚀 Testing Payment Agent with Hiero SDK Python")
        print("=" * 60)
        
        # Create payment agent instance
        agent = PaymentAgent()
        
        print("✅ Payment Agent created successfully")
        print(f"📋 Hedera Account ID: {agent.hedera_account_id}")
        print(f"🌐 Network: {agent.hedera_network}")
        
        # Test 1: Get account balance
        print("\n" + "=" * 60)
        print("🧪 Testing Account Balance Query")
        print("=" * 60)
        
        balance_result = await agent._get_hedera_balance()
        
        if balance_result["success"]:
            print(f"✅ Balance query successful!")
            print(f"📊 Account Balance: {balance_result['balance']} HBAR")
            print(f"🌐 Network: {balance_result['network']}")
        else:
            print(f"❌ Balance query failed: {balance_result['error']}")
            return
        
        # Test 2: Transfer HBAR
        print("\n" + "=" * 60)
        print("🧪 Testing HBAR Transfer")
        print("=" * 60)
        
        transfer_result = await agent._execute_hedera_transfer(
            destination_account="0.0.3",  # Hedera treasury account
            amount=1.0,  # 1 HBAR
            memo="Test transfer from Payment Agent"
        )
        
        if transfer_result["success"]:
            print(f"✅ Transfer successful!")
            print(f"📋 Transaction ID: {transfer_result['transaction_id']}")
            print(f"💰 Amount: {transfer_result['amount']} HBAR")
            print(f"📥 To: {transfer_result['destination']}")
            print(f"🌐 Network: {transfer_result['network']}")
            print(f"📝 Memo: {transfer_result['memo']}")
        else:
            print(f"❌ Transfer failed: {transfer_result['error']}")
            return
        
        # Test 3: Get updated balance
        print("\n" + "=" * 60)
        print("🧪 Testing Updated Balance Query")
        print("=" * 60)
        
        updated_balance = await agent._get_hedera_balance()
        
        if updated_balance["success"]:
            print(f"✅ Updated balance query successful!")
            print(f"📊 New Account Balance: {updated_balance['balance']} HBAR")
            print(f"📉 Balance Change: {balance_result['balance'] - updated_balance['balance']:.8f} HBAR")
        else:
            print(f"❌ Updated balance query failed: {updated_balance['error']}")
        
        print("\n🎉 All tests completed successfully!")
        print("📝 Note: Payment Agent is now using real Hedera transactions via Hiero SDK Python")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_payment_agent())
