#!/usr/bin/env python3
"""
Direct Hedera Transaction Test Script
This script tests Hedera transactions using the Hiero SDK Python library.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_hedera_import():
    """Test if Hiero SDK can be imported"""
    try:
        from hiero_sdk_python import Client, AccountId, PrivateKey, TransferTransaction, Hbar
        print("✅ Hiero SDK imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import Hiero SDK: {e}")
        print("Please install: pip install hiero-sdk-python")
        return False

def test_hedera_connection():
    """Test Hedera connection and credentials"""
    try:
        from hiero_sdk_python import Client, Network, AccountId, PrivateKey
        
        # Check environment variables
        operator_id = os.getenv("OPERATOR_ID")
        operator_key = os.getenv("OPERATOR_KEY")
        network = os.getenv("NETWORK", "testnet")
        
        if not operator_id or not operator_key:
            print("❌ Missing Hedera credentials in .env file")
            print("Required: OPERATOR_ID, OPERATOR_KEY")
            return False
        
        print(f"🔗 Connecting to Hedera {network}...")
        print(f"📋 Operator ID: {operator_id}")
        
        # Create network configuration
        network_config = Network(network=network)
        
        # Create Hiero client with network
        client = Client(network=network_config)
        
        # Set operator credentials
        operator_account_id = AccountId.from_string(operator_id)
        operator_private_key = PrivateKey.from_string(operator_key)
        client.set_operator(operator_account_id, operator_private_key)
        
        print("✅ Hedera client created successfully")
        
        return client
        
    except Exception as e:
        print(f"❌ Failed to create Hedera client: {e}")
        return None

def test_small_transfer(client, recipient_id="0.0.3", amount_hbar=2.0):
    """Test a small HBAR transfer using Hiero SDK"""
    try:
        from hiero_sdk_python import TransferTransaction, AccountId, Hbar
        
        print(f"\n💰 Testing transfer of {amount_hbar} HBAR to {recipient_id}")
        
        # Convert HBAR to tinybars (1 HBAR = 100,000,000 tinybars)
        amount_tinybars = int(amount_hbar * 100_000_000)
        operator_id = os.getenv("OPERATOR_ID")
        
        print(f"📊 Amount in tinybars: {amount_tinybars}")
        print(f"📤 From: {operator_id}")
        print(f"📥 To: {recipient_id}")
        
        # Create transfer transaction using Hiero SDK
        print("📤 Executing transaction...")
        
        # Create transfer transaction using tinybars (integers)
        
        # Create hbar_transfers dictionary
        hbar_transfers = {
            AccountId.from_string(operator_id): -amount_tinybars,
            AccountId.from_string(recipient_id): amount_tinybars
        }
        
        transaction = TransferTransaction(hbar_transfers=hbar_transfers)
        transaction.transaction_fee = 100000000  # 1 HBAR fee in tinybars
        
        # Execute transaction
        response = transaction.execute(client)
        receipt = response
        
        print("✅ Transaction executed successfully!")
        print(f"📋 Transaction ID: {response.transaction_id}")
        print(f"📋 Receipt Status: {receipt.status}")
        
        return {
            "success": True,
            "transaction_id": str(response.transaction_id),
            "status": str(receipt.status),
            "amount": amount_hbar,
            "recipient": recipient_id
        }
        
    except Exception as e:
        print(f"❌ Transfer failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }

def test_account_balance(client):
    """Test querying account balance using Hiero SDK"""
    try:
        from hiero_sdk_python import CryptoGetAccountBalanceQuery, AccountId
        
        print(f"\n💰 Testing account balance query...")
        
        operator_id = os.getenv("OPERATOR_ID")
        print(f"📋 Querying balance for: {operator_id}")
        
        # Create balance query
        query = CryptoGetAccountBalanceQuery()
        query.set_account_id(AccountId.from_string(operator_id))
        
        # Execute query
        balance = query.execute(client)
        
        print("✅ Balance query successful!")
        print(f"📊 Account Balance: {balance.hbars.to_hbars()} HBAR")
        
        return {
            "success": True,
            "balance": balance.hbars.to_hbars(),
            "account_id": operator_id
        }
        
    except Exception as e:
        print(f"❌ Balance query failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }

def main():
    """Main test function"""
    print("🚀 Hedera Direct Transaction Test (Hiero SDK)")
    print("=" * 50)
    
    # Test 1: Import check
    if not test_hedera_import():
        sys.exit(1)
    
    # Test 2: Connection test
    client = test_hedera_connection()
    if not client:
        sys.exit(1)
    
    # Test 3: Account balance query
    print("\n" + "=" * 50)
    print("🧪 Testing Account Balance Query")
    print("=" * 50)
    
    balance_result = test_account_balance(client)
    
    # Test 4: Small transfer test
    print("\n" + "=" * 50)
    print("🧪 Testing Small Transfer")
    print("=" * 50)
    
    result = test_small_transfer(client, amount_hbar=2.0)
    
    if result["success"] and balance_result["success"]:
        print(f"\n🎉 SUCCESS!")
        print(f"Account Balance: {balance_result['balance']} HBAR")
        print(f"Transaction ID: {result['transaction_id']}")
        print(f"Status: {result['status']}")
        print(f"Amount: {result['amount']} HBAR")
        print(f"Recipient: {result['recipient']}")
        print("\n📝 Note: This is a simulation using Hiero SDK Python.")
        print("   For real transactions, the SDK provides full Hedera functionality")
        print("   including token management, consensus services, and more.")
    else:
        print(f"\n💥 FAILED:")
        if not balance_result["success"]:
            print(f"Balance query error: {balance_result['error']}")
        if not result["success"]:
            print(f"Transfer error: {result['error']}")
        sys.exit(1)

if __name__ == "__main__":
    main()