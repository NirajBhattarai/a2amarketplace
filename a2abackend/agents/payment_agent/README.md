# 💸 Payment Agent

A multi-network payment agent that supports sending payments across Hedera, Ethereum, and Polygon networks with native currency and ERC20 token support.

## 🌟 Features

- **Multi-Network Support**: Send payments across Hedera, Ethereum, and Polygon networks
- **Native Currency Support**: HBAR (Hedera), ETH (Ethereum), MATIC (Polygon)
- **ERC20 Token Support**: USDC, USDT, and other popular tokens
- **Address Validation**: Validates payment address formats for each network
- **Transaction Tracking**: Provides transaction IDs and status checking
- **Intelligent Parsing**: Automatically detects network from payment requests

## 🔧 Supported Networks

### Hedera Network
- **Native Token**: HBAR
- **Address Format**: `0.0.123456`
- **Example**: `Send 5 HBAR to account 0.0.123456`

### Ethereum Mainnet
- **Native Token**: ETH
- **ERC20 Tokens**: USDC, USDT, WETH
- **Address Format**: `0x...` (40 hex characters)
- **Example**: `Transfer 0.1 ETH to 0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6`

### Polygon Network
- **Native Token**: MATIC
- **ERC20 Tokens**: USDC, USDT, WMATIC
- **Address Format**: `0x...` (40 hex characters)
- **Example**: `Send 10 MATIC to 0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6`

## 🚀 Usage Examples

### HBAR Transfer
```
Send 5 HBAR to account 0.0.123456
```

### Ethereum Transfer
```
Transfer 0.1 ETH to 0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6
```

### Polygon Transfer
```
Send 10 MATIC to 0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6
```

### With Transaction Memo
```
Send 2.5 HBAR to account 0.0.789012 with memo "Payment for services"
```

### Check Transaction Status
```
Check status of transaction hedera_tx_12345
```

## 🛠️ Technical Implementation

### Agent Architecture
- **LLM**: Google Gemini 2.5 Flash
- **Tools**: `transfer_hbar()`, `transfer_eth()`, `transfer_matic()`, `validate_payment_address()`, `get_transaction_status()`
- **Protocol**: A2A JSON-RPC 2.0
- **Port**: 10005 (default)

### Payment Processing Flow
1. **Address Validation**: Validates format for specific network
2. **Network Detection**: Automatically detects network from address format
3. **Transaction Execution**: Executes payment on appropriate network
4. **Confirmation**: Returns transaction ID and status
5. **Status Tracking**: Provides transaction status checking

### Available Tools

#### 1. transfer_hbar(destination_account, amount, memo)
- Transfers HBAR on Hedera network
- Parameters: Hedera account ID, amount, optional memo
- Returns: Transaction result with ID

#### 2. transfer_eth(destination_address, amount, gas_limit)
- Transfers ETH on Ethereum network
- Parameters: Ethereum address, amount, optional gas limit
- Returns: Transaction result with ID

#### 3. transfer_matic(destination_address, amount, gas_limit)
- Transfers MATIC on Polygon network
- Parameters: Polygon address, amount, optional gas limit
- Returns: Transaction result with ID

#### 4. validate_payment_address(address, network)
- Validates payment address format
- Parameters: Address to validate, network type
- Returns: Validation result

#### 5. get_transaction_status(transaction_id, network)
- Checks transaction status
- Parameters: Transaction ID, network
- Returns: Status information

## 🔄 Integration with A2A System

The Payment Agent integrates seamlessly with the A2A (Agent-to-Agent) system:

1. **Discovery**: Automatically discovered by orchestrator agents
2. **Task Management**: Handles incoming payment requests via JSON-RPC
3. **Session Management**: Maintains conversation context
4. **Error Handling**: Provides clear error messages and recovery options

## 🚀 Running the Agent

### Start the Payment Agent Server
```bash
cd a2abackend/agents/payment_agent
python -m agents.payment_agent --host localhost --port 10005
```

### Test with Orchestrator
The agent will be automatically discovered and can be called via:
```python
# Example usage in orchestrator
response = await orchestrator.invoke("Send 5 HBAR to account 0.0.123456")
```

## 🔒 Security Considerations

- **Address Validation**: All addresses are validated before processing
- **Amount Verification**: Amounts are checked for validity
- **Transaction Confirmation**: All transactions provide confirmation IDs
- **Error Handling**: Comprehensive error handling and user feedback

## 📊 Response Format

### Successful Payment
```json
{
  "success": true,
  "network": "Hedera Network",
  "transaction_id": "hedera_tx_12345",
  "destination": "0.0.123456",
  "amount": 5.0,
  "token": "HBAR",
  "status": "completed",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Error Response
```json
{
  "error": "Invalid address format for Hedera network",
  "success": false
}
```

## 🔧 Configuration

The agent can be configured with:
- **Host**: Server host (default: localhost)
- **Port**: Server port (default: 10005)
- **Network Settings**: Blockchain network configurations
- **Gas Limits**: Custom gas limits for Ethereum/Polygon transactions

## 📝 Development Notes

- **Mock Implementation**: Current implementation uses mock responses
- **Production Ready**: Can be extended with real blockchain SDKs
- **Extensible**: Easy to add new networks and token types
- **Testable**: Comprehensive test coverage for all tools
