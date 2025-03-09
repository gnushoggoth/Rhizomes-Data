// TokenManager.js - React component for managing deployed tokens
import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { ethers } from 'ethers';
import WhiteLabelTokenABI from './abis/WhiteLabelToken.json';

const TokenManager = () => {
  // Get token address from URL params
  const { tokenAddress } = useParams();
  
  // State variables
  const [provider, setProvider] = useState(null);
  const [signer, setSigner] = useState(null);
  const [tokenContract, setTokenContract] = useState(null);
  const [account, setAccount] = useState('');
  const [isOwner, setIsOwner] = useState(false);
  
  // Token data
  const [tokenData, setTokenData] = useState({
    name: '',
    symbol: '',
    decimals: 0,
    totalSupply: '0',
    ownerBalance: '0',
    owner: '',
    transferFeeRate: 0,
    feeCollector: '',
    feesEnabled: false,
    whitelistEnabled: false
  });
  
  // Form states
  const [mintForm, setMintForm] = useState({
    recipient: '',
    amount: ''
  });
  
  const [feeForm, setFeeForm] = useState({
    newRate: 0,
    newCollector: '',
    enabled: true
  });
  
  const [whitelistForm, setWhitelistForm] = useState({
    address: '',
    status: true
  });
  
  const [transferForm, setTransferForm] = useState({
    recipient: '',
    amount: ''
  });
  
  // Transaction status
  const [txPending, setTxPending] = useState(false);
  const [txHash, setTxHash] = useState('');
  const [txError, setTxError] = useState('');
  
  // Initialize
  useEffect(() => {
    const connectToToken = async () => {
      try {
        // Check if MetaMask is installed
        if (window.ethereum && tokenAddress) {
          // Create provider and signer
          const web3Provider = new ethers.providers.Web3Provider(window.ethereum);
          await window.ethereum.request({ method: 'eth_requestAccounts' });
          const web3Signer = web3Provider.getSigner();
          const userAddress = await web3Signer.getAddress();
          
          // Create token contract instance
          const token = new ethers.Contract(
            tokenAddress,
            WhiteLabelTokenABI.abi,
            web3Signer
          );
          
          // Initialize state
          setProvider(web3Provider);
          setSigner(web3Signer);
          setTokenContract(token);
          setAccount(userAddress);
          
          // Load token data
          await loadTokenData(token, userAddress);
          
          // Setup account change listener
          window.ethereum.on('accountsChanged', async (accounts) => {
            if (accounts.length > 0) {
              setAccount(accounts[0]);
              await loadTokenData(token, accounts[0]);
            } else {
              setAccount('');
            }
          });
        } else {
          console.error("Please install MetaMask or provide a valid token address!");
        }
      } catch (error) {
        console.error("Connection error:", error);
      }
    };
    
    connectToToken();
    
    // Cleanup event listeners
    return () => {
      if (window.ethereum) {
        window.ethereum.removeAllListeners('accountsChanged');
      }
    };
  }, [tokenAddress]);
  
  // Load token data
  const loadTokenData = async (token, userAddress) => {
    try {
      // Get token basic information
      const [
        name,
        symbol,
        decimals,
        totalSupply,
        ownerBalance,
        owner,
        transferFeeRate,
        feeCollector,
        feesEnabled,
        whitelistEnabled
      ] = await Promise.all([
        token.name(),
        token.symbol(),
        token.decimals(),
        token.totalSupply(),
        token.balanceOf(userAddress),
        token.owner(),
        token.transferFeeRate(),
        token.feeCollector(),
        token.feesEnabled(),
        token.whitelistEnabled()
      ]);
      
      // Format data
      setTokenData({
        name,
        symbol,
        decimals: decimals.toNumber(),
        totalSupply: ethers.utils.formatUnits(totalSupply, decimals),
        ownerBalance: ethers.utils.formatUnits(ownerBalance, decimals),
        owner,
        transferFeeRate: transferFeeRate.toNumber(),
        feeCollector,
        feesEnabled,
        whitelistEnabled
      });
      
      // Check if user is owner
      setIsOwner(owner.toLowerCase() === userAddress.toLowerCase());
      
      // Initialize forms with current values
      setFeeForm({
        newRate: transferFeeRate.toNumber(),
        newCollector: feeCollector,
        enabled: feesEnabled
      });
      
      setMintForm(prev => ({
        ...prev,
        recipient: userAddress
      }));
      
      setWhitelistForm(prev => ({
        ...prev,
        address: userAddress
      }));
      
    } catch (error) {
      console.error("Error loading token data:", error);
    }
  };
  
  // Handle form changes
  const handleMintFormChange = (e) => {
    const { name, value } = e.target;
    setMintForm(prev => ({ ...prev, [name]: value }));
  };
  
  const handleFeeFormChange = (e) => {
    const { name, value } = e.target;
    const newValue = name === 'enabled' ? e.target.checked : value;
    setFeeForm(prev => ({ ...prev, [name]: newValue }));
  };
  
  const handleWhitelistFormChange = (e) => {
    const { name, value } = e.target;
    const newValue = name === 'status' ? e.target.checked : value;
    setWhitelistForm(prev => ({ ...prev, [name]: newValue }));
  };
  
  const handleTransferFormChange = (e) => {
    const { name, value } = e.target;
    setTransferForm(prev => ({ ...prev, [name]: value }));
  };
  
  // Mint tokens (owner only)
  const mintTokens = async (e) => {
    e.preventDefault();
    
    if (!isOwner) {
      setTxError("Only the token owner can mint tokens");
      return;
    }
    
    setTxPending(true);
    setTxHash('');
    setTxError('');
    
    try {
      const amount = ethers.utils.parseUnits(mintForm.amount, tokenData.decimals);
      
      const tx = await tokenContract.mint(mintForm.recipient, amount);
      setTxHash(tx.hash);
      
      await tx.wait();
      
      // Reload token data
      await loadTokenData(tokenContract, account);
      
      // Reset form
      setMintForm(prev => ({
        ...prev,
        amount: ''
      }));
      
    } catch (error) {
      console.error("Mint error:", error);
      setTxError(error.message);
    } finally {
      setTxPending(false);
    }
  };
  
  // Update fee configuration (owner only)
  const updateFeeConfig = async (e) => {
    e.preventDefault();
    
    if (!isOwner) {
      setTxError("Only the token owner can update fee configuration");
      return;
    }
    
    setTxPending(true);
    setTxHash('');
    setTxError('');
    
    try {
      const tx = await tokenContract.updateFeeConfig(
        feeForm.newRate,
        feeForm.newCollector,
        feeForm.enabled
      );
      setTxHash(tx.hash);
      
      await tx.wait();
      
      // Reload token data
      await loadTokenData(tokenContract, account);
      
    } catch (error) {
      console.error("Fee update error:", error);
      setTxError(error.message);
    } finally {
      setTxPending(false);
    }
  };
  
  // Update whitelist (owner only)
  const updateWhitelist = async (e) => {
    e.preventDefault();
    
    if (!isOwner) {
      setTxError("Only the token owner can update the whitelist");
      return;
    }
    
    setTxPending(true);
    setTxHash('');
    setTxError('');
    
    try {
      const tx = await tokenContract.updateWhitelist(
        whitelistForm.address,
        whitelistForm.status
      );
      setTxHash(tx.hash);
      
      await tx.wait();
      
      // Reset form
      setWhitelistForm(prev => ({
        ...prev,
        address: ''
      }));
      
    } catch (error) {
      console.error("Whitelist update error:", error);
      setTxError(error.message);
    } finally {
      setTxPending(false);
    }
  };
  
  // Toggle whitelist functionality (owner only)
  const toggleWhitelist = async () => {
    if (!isOwner) {
      setTxError("Only the token owner can toggle whitelist functionality");
      return;
    }
    
    setTxPending(true);
    setTxHash('');
    setTxError('');
    
    try {
      const tx = await tokenContract.setWhitelistEnabled(!tokenData.whitelistEnabled);
      setTxHash(tx.hash);
      
      await tx.wait();
      
      // Reload token data
      await loadTokenData(tokenContract, account);
      
    } catch (error) {
      console.error("Whitelist toggle error:", error);
      setTxError(error.message);
    } finally {
      setTxPending(false);
    }
  };
  
  // Transfer tokens
  const transferTokens = async (e) => {
    e.preventDefault();
    
    setTxPending(true);
    setTxHash('');
    setTxError('');
    
    try {
      const amount = ethers.utils.parseUnits(transferForm.amount, tokenData.decimals);
      
      const tx = await tokenContract.transfer(transferForm.recipient, amount);
      setTxHash(tx.hash);
      
      await tx.wait();
      
      // Reload token data
      await loadTokenData(tokenContract, account);
      
      // Reset form
      setTransferForm({
        recipient: '',
        amount: ''
      });
      
    } catch (error) {
      console.error("Transfer error:", error);
      setTxError(error.message);
    } finally {
      setTxPending(false);
    }
  };
  
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">
        {tokenData.name} ({tokenData.symbol}) Management
      </h1>
      
      {/* Token Information */}
      <div className="mb-8 p-6 border rounded shadow bg-gray-50">
        <h2 className="text-xl font-semibold mb-4">Token Information</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <p><strong>Address:</strong> {tokenAddress}</p>
            <p><strong>Name:</strong> {tokenData.name}</p>
            <p><strong>Symbol:</strong> {tokenData.symbol}</p>
            <p><strong>Decimals:</strong> {tokenData.decimals}</p>
          </div>
          <div>
            <p><strong>Total Supply:</strong> {tokenData.totalSupply} {tokenData.symbol}</p>
            <p><strong>Your Balance:</strong> {tokenData.ownerBalance} {tokenData.symbol}</p>
            <p><strong>Transfer Fee:</strong> {(tokenData.transferFeeRate / 100).toFixed(2)}%</p>
            <p><strong>Fee Status:</strong> {tokenData.feesEnabled ? 'Enabled' : 'Disabled'}</p>
            <p><strong>Whitelist:</strong> {tokenData.whitelistEnabled ? 'Enabled' : 'Disabled'}</p>
          </div>
        </div>
        
        <div className="mt-2">
          <p><strong>Owner:</strong> {tokenData.owner}</p>
          <p><strong>Fee Collector:</strong> {tokenData.feeCollector}</p>
        </div>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Transfer Tokens (For all users) */}
        <div className="p-6 border rounded shadow">
          <h2 className="text-xl font-semibold mb-4">Transfer Tokens</h2>
          
          <form onSubmit={transferTokens}>
            <div className="mb-4">
              <label className="block mb-1">Recipient Address</label>
              <input
                type="text"
                name="recipient"
                value={transferForm.recipient}
                onChange={handleTransferFormChange}
                className="w-full p-2 border rounded"
                placeholder="0x..."
                required
              />
            </div>
            
            <div className="mb-4">
              <label className="block mb-1">Amount</label>
              <input
                type="text"
                name="amount"
                value={transferForm.amount}
                onChange={handleTransferFormChange}
                className="w-full p-2 border rounded"
                placeholder="100"
                required
              />
            </div>
            
            <button
              type="submit"
              className="px-6 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:bg-gray-400"
              disabled={!account || txPending}
            >
              {txPending ? 'Processing...' : 'Transfer'}
            </button>
          </form>
        </div>
        
        {/* Mint Tokens (Owner only) */}
        {isOwner && (
          <div className="p-6 border rounded shadow">
            <h2 className="text-xl font-semibold mb-4">Mint Tokens (Owner Only)</h2>
            
            <form onSubmit={mintTokens}>
              <div className="mb-4">
                <label className="block mb-1">Recipient Address</label>
                <input
                  type="text"
                  name="recipient"
                  value={mintForm.recipient}
                  onChange={handleMintFormChange}
                  className="w-full p-2 border rounded"
                  placeholder="0x..."
                  required
                />
              </div>
              
              <div className="mb-4">
                <label className="block mb-1">Amount</label>
                <input
                  type="text"
                  name="amount"
                  value={mintForm.amount}
                  onChange={handleMintFormChange}
                  className="w-full p-2 border rounded"
                  placeholder="1000"
                  required
                />
              </div>
              
              <button
                type="submit"
                className="px-6 py-2 bg-green-500 text-white rounded hover:bg-green-600 disabled:bg-gray-400"
                disabled={txPending}
              >
                {txPending ? 'Processing...' : 'Mint Tokens'}
              </button>
            </form>
          </div>
        )}
        
        {/* Update Fee Config (Owner only) */}
        {isOwner && (
          <div className="p-6 border rounded shadow">
            <h2 className="text-xl font-semibold mb-4">Fee Configuration (Owner Only)</h2>
            
            <form onSubmit={updateFeeConfig}>
              <div className="mb-4">
                <label className="block mb-1">Transfer Fee Rate (basis points, 100 = 1%)</label>
                <input
                  type="number"
                  name="newRate"
                  value={feeForm.newRate}
                  onChange={handleFeeFormChange}
                  className="w-full p-2 border rounded"
                  min="0"
                  max="1000"
                  required
                />
                <small className="text-gray-500">
                  {(feeForm.newRate / 100).toFixed(2)}% fee per transfer
                </small>
              </div>
              
              <div className="mb-4">
                <label className="block mb-1">Fee Collector Address</label>
                <input
                  type="text"
                  name="newCollector"
                  value={feeForm.newCollector}
                  onChange={handleFeeFormChange}
                  className="w-full p-2 border rounded"
                  placeholder="0x..."
                  required
                />
              </div>
              
              <div className="mb-4">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    name="enabled"
                    checked={feeForm.enabled}
                    onChange={handleFeeFormChange}
                    className="mr-2"
                  />
                  Enable Fees
                </label>
              </div>
              
              <button
                type="submit"
                className="px-6 py-2 bg-purple-500 text-white rounded hover:bg-purple-600 disabled:bg-gray-400"
                disabled={txPending}
              >
                {txPending ? 'Processing...' : 'Update Fee Configuration'}
              </button>
            </form>
          </div>
        )}
        
        {/* Whitelist Management (Owner only) */}
        {isOwner && (
          <div className="p-6 border rounded shadow">
            <h2 className="text-xl font-semibold mb-4">Whitelist Management (Owner Only)</h2>
            
            <div className="mb-4">
              <button
                onClick={toggleWhitelist}
                className="px-6 py-2 bg-orange-500 text-white rounded hover:bg-orange-600 disabled:bg-gray-400 mb-4"
                disabled={txPending}
              >
                {tokenData.whitelistEnabled ? 'Disable Whitelist' : 'Enable Whitelist'}
              </button>
            </div>
            
            <form onSubmit={updateWhitelist}>
              <div className="mb-4">
                <label className="block mb-1">Address</label>
                <input
                  type="text"
                  name="address"
                  value={whitelistForm.address}
                  onChange={handleWhitelistFormChange}
                  className="w-full p-2 border rounded"
                  placeholder="0x..."
                  required
                />
              </div>
              
              <div className="mb-4">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    name="status"
                    checked={whitelistForm.status}
                    onChange={handleWhitelistFormChange}
                    className="mr-2"
                  />
                  Whitelist Status
                </label>
              </div>
              
              <button
                type="submit"
                className="px-6 py-2 bg-yellow-500 text-white rounded hover:bg-yellow-600 disabled:bg-gray-400"
                disabled={txPending}
              >
                {txPending ? 'Processing...' : whitelistForm.status ? 'Add to Whitelist' : 'Remove from Whitelist'}
              </button>
            </form>
          </div>
        )}
      </div>
      
      {/* Transaction Status */}
      {(txHash || txError) && (
        <div className="mt-6">
          {txHash && (
            <div className="p-3 bg-green-100 text-green-800 rounded mb-3">
              <p>Transaction submitted: {txHash}</p>
            </div>
          )}
          
          {txError && (
            <div className="p-3 bg-red-100 text-red-800 rounded">
              <p>Error: {txError}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default TokenManager;