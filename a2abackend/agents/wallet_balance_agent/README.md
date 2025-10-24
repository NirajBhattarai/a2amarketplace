# 💰 Wallet Balance Agent

A comprehensive **multi-network wallet balance checking agent** supporting Hedera, Ethereum, and Polygon networks with native currencies and ERC20 tokens.

## 🎯 Overview

This agent provides **unified wallet balance checking** across multiple blockchain networks with:
- **Multi-network support** for Hedera, Ethereum, and Polygon
- **Native currency and ERC20 token** balance checking
- **Intelligent address validation** and network detection
- **USD value conversion** for all balances
- **Real-time balance updates** and status monitoring

## ✨ Key Features

### 🌐 **Multi-Network Support**
- **Hedera Network**: HBAR balances with account ID validation
- **Ethereum Mainnet**: ETH and ERC20 tokens (USDC, USDT, WETH)
- **Polygon Network**: MATIC and ERC20 tokens (USDC, USDT, WMATIC)
- **Automatic Network Detection**: Smart detection from address format

### 💱 **Advanced Balance Features**
- **USD Value Conversion**: Real-time USD values for all balances
- **Token Support**: Native currencies and popular ERC20 tokens
- **Address Validation**: Network-specific address format validation
- **Comprehensive Reporting**: Detailed balance breakdowns by network

## 🔧 Supported Networks

### Hedera Network
- **Native Token**: HBAR
- **Address Format**: `0.0.123456`
- **Example**: `0.0.123456`

### Ethereum Mainnet
- **Native Token**: ETH
- **ERC20 Tokens**: USDC, USDT, WETH
- **Address Format**: `0x...` (40 hex characters)
- **Example**: `0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6`

### Polygon Network
- **Native Token**: MATIC
- **ERC20 Tokens**: USDC, USDT, WMATIC
- **Address Format**: `0x...` (40 hex characters)
- **Example**: `0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6`

## 🚀 Usage Examples

### Basic Balance Check
```
Check balance for wallet 0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6
```

### Network-Specific Check
```
Get Ethereum balance for 0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6
```

### Hedera Account Check
```
Check Hedera balance for account 0.0.123456
```

### Multi-Network Check
```
Show my wallet balance across all networks
```

## 🛠️ Technical Implementation

### Agent Architecture
- **LLM**: Google Gemini 2.5 Flash
- **Tools**: `check_wallet_balance()`, `validate_wallet_address()`
- **Protocol**: A2A JSON-RPC 2.0
- **Port**: 10004 (default)

### Balance Checking Logic
1. **Address Validation**: Validates format for specific network
2. **Network Detection**: Automatically detects network from address format
3. **Balance Fetching**: Queries blockchain networks for balances
4. **Token Support**: Checks both native currencies and ERC20 tokens
5. **USD Conversion**: Converts balances to approximate USD values

### Mock Implementation
Currently uses mock data for demonstration. In production, would integrate with:
- **Hedera SDK**: For HBAR and Hedera token balances
- **Web3.py**: For Ethereum and Polygon balances
- **Price APIs**: For real-time USD conversion

## 🔧 Development

### Running the Agent
```bash
python3 -m agents.wallet_balance_agent --host localhost --port 10004
```

### Agent Card
Available at: `http://localhost:10004/.well-known/agent.json`

### Health Check
```bash
curl http://localhost:10004/health
```

## 📊 Response Format

The agent returns structured balance information:

```json
{
  "wallet_address": "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
  "networks": {
    "ethereum": {
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
      "total_usd_value": 6000.0
    }
  },
  "total_usd_value": 6000.0,
  "timestamp": "2025-01-27T10:30:00Z"
}
```

## 🔮 Future Enhancements

- **Real Blockchain Integration**: Replace mock data with actual blockchain queries
- **Additional Networks**: Support for Bitcoin, Solana, Binance Smart Chain
- **Price Feeds**: Real-time price data from CoinGecko or CoinMarketCap
- **Transaction History**: Show recent transactions and activity
- **Portfolio Analytics**: Advanced portfolio tracking and analytics
- **DeFi Integration**: Check DeFi protocol positions and yields

## 🤝 Contributing

This agent follows the same A2A pattern as other agents in the system:
- `agent.py`: Core business logic with LLM integration
- `task_manager.py`: A2A protocol handling
- `__main__.py`: Server entry point and agent registration

## 📚 Related Documentation

- [A2A Protocol Specification](https://github.com/google/A2A)
- [Google ADK Documentation](https://github.com/google/agent-development-kit)
- [Hedera SDK](https://docs.hedera.com/hedera/sdks-and-apis/sdks)
- [Web3.py Documentation](https://web3py.readthedocs.io/)
