'use client';

import { useState } from 'react';

interface PaymentInterfaceProps {
  onSendMessage: (message: string) => void;
  className?: string;
}

export function PaymentInterface({ onSendMessage, className = '' }: PaymentInterfaceProps) {
  const [selectedNetwork, setSelectedNetwork] = useState<'hedera' | 'ethereum' | 'polygon'>('hedera');
  const [amount, setAmount] = useState('');
  const [recipient, setRecipient] = useState('');
  const [memo, setMemo] = useState('');

  const handleQuickPayment = (template: string) => {
    onSendMessage(template);
  };

  const handleCustomPayment = () => {
    if (!amount || !recipient) return;
    
    let message = '';
    if (selectedNetwork === 'hedera') {
      message = `Send ${amount} HBAR to account ${recipient}`;
      if (memo) message += ` with memo '${memo}'`;
    } else if (selectedNetwork === 'ethereum') {
      message = `Transfer ${amount} ETH to ${recipient}`;
    } else if (selectedNetwork === 'polygon') {
      message = `Send ${amount} MATIC to ${recipient}`;
    }
    
    onSendMessage(message);
  };

  const quickPayments = [
    {
      label: 'Test Hedera Transfer',
      message: 'Send 0.001 HBAR to account 0.0.123456',
      network: 'hedera',
      description: 'Small HBAR test transfer'
    },
    {
      label: 'Test Ethereum Transfer',
      message: 'Transfer 0.0001 ETH to 0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6',
      network: 'ethereum',
      description: 'Small ETH test transfer'
    },
    {
      label: 'Test Polygon Transfer',
      message: 'Send 0.001 MATIC to 0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6',
      network: 'polygon',
      description: 'Small MATIC test transfer'
    },
    {
      label: 'Hedera with Memo',
      message: 'Send 0.001 HBAR to account 0.0.123456 with memo "Test payment"',
      network: 'hedera',
      description: 'HBAR transfer with memo'
    },
    {
      label: 'Check Transaction Status',
      message: 'Check status of transaction hedera_tx_12345',
      network: 'hedera',
      description: 'Check transaction status'
    },
    {
      label: 'Validate Address',
      message: 'Validate address 0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6 for ethereum',
      network: 'ethereum',
      description: 'Validate Ethereum address'
    }
  ];

  return (
    <div className={`bg-white rounded-lg shadow-lg p-6 ${className}`}>
      <div className="flex items-center mb-4">
        <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center mr-3">
          <span className="text-green-600 text-lg">💰</span>
        </div>
        <div>
          <h3 className="text-lg font-semibold text-gray-800">Payment Interface</h3>
          <p className="text-sm text-gray-500">Multi-network blockchain payments via PaymentAgent</p>
        </div>
      </div>

      {/* Quick Payment Templates */}
      <div className="mb-6">
        <h4 className="text-sm font-medium text-gray-700 mb-3">Quick Payment Templates</h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
          {quickPayments.map((payment, index) => (
            <button
              key={index}
              onClick={() => handleQuickPayment(payment.message)}
              className={`p-3 text-left rounded-lg border transition-colors ${
                payment.network === 'hedera' 
                  ? 'border-purple-200 hover:border-purple-300 hover:bg-purple-50'
                  : payment.network === 'ethereum'
                  ? 'border-blue-200 hover:border-blue-300 hover:bg-blue-50'
                  : 'border-pink-200 hover:border-pink-300 hover:bg-pink-50'
              }`}
            >
              <div className="flex items-center justify-between">
                <div className="font-medium text-sm text-gray-800">{payment.label}</div>
                <div className={`text-xs px-2 py-1 rounded-full ${
                  payment.network === 'hedera' 
                    ? 'bg-purple-100 text-purple-700'
                    : payment.network === 'ethereum'
                    ? 'bg-blue-100 text-blue-700'
                    : 'bg-pink-100 text-pink-700'
                }`}>
                  {payment.network === 'hedera' ? '🟣 HBAR' : payment.network === 'ethereum' ? '🔵 ETH' : '🟡 MATIC'}
                </div>
              </div>
              <div className="text-xs text-gray-500 mt-1">{payment.description}</div>
              <div className="text-xs text-gray-400 mt-1 font-mono">{payment.message}</div>
            </button>
          ))}
        </div>
      </div>

      {/* Custom Payment Form */}
      <div className="border-t pt-4">
        <h4 className="text-sm font-medium text-gray-700 mb-3">Custom Payment</h4>
        
        {/* Network Selection */}
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">Network</label>
          <div className="flex space-x-2">
            {[
              { value: 'hedera', label: 'Hedera (HBAR)', color: 'purple' },
              { value: 'ethereum', label: 'Ethereum (ETH)', color: 'blue' },
              { value: 'polygon', label: 'Polygon (MATIC)', color: 'pink' }
            ].map((network) => (
              <button
                key={network.value}
                onClick={() => setSelectedNetwork(network.value as any)}
                className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                  selectedNetwork === network.value
                    ? `bg-${network.color}-600 text-white`
                    : `bg-${network.color}-100 text-${network.color}-700 hover:bg-${network.color}-200`
                }`}
              >
                {network.label}
              </button>
            ))}
          </div>
        </div>

        {/* Amount and Recipient */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Amount</label>
            <input
              type="text"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              placeholder={selectedNetwork === 'hedera' ? '0.001' : '0.0001'}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {selectedNetwork === 'hedera' ? 'Account ID' : 'Address'}
            </label>
            <input
              type="text"
              value={recipient}
              onChange={(e) => setRecipient(e.target.value)}
              placeholder={selectedNetwork === 'hedera' ? '0.0.123456' : '0x...'}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        </div>

        {/* Memo (Hedera only) */}
        {selectedNetwork === 'hedera' && (
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-1">Memo (Optional)</label>
            <input
              type="text"
              value={memo}
              onChange={(e) => setMemo(e.target.value)}
              placeholder="Payment memo"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        )}

        {/* Send Button */}
        <button
          onClick={handleCustomPayment}
          disabled={!amount || !recipient}
          className="w-full bg-green-600 text-white py-2 px-4 rounded-lg font-medium hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          Send {selectedNetwork === 'hedera' ? 'HBAR' : selectedNetwork === 'ethereum' ? 'ETH' : 'MATIC'} Payment
        </button>
      </div>

      {/* Warning */}
      <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
        <div className="flex items-start">
          <div className="flex-shrink-0">
            <span className="text-yellow-600 text-sm">⚠️</span>
          </div>
          <div className="ml-2">
            <p className="text-sm text-yellow-800">
              <strong>Warning:</strong> These are real blockchain transactions. 
              Make sure you're using testnet accounts with test funds only.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
