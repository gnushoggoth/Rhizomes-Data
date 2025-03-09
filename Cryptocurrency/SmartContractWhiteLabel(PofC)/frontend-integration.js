// TokenCreator.js - React component for deploying new tokens through the factory
import React, { useState, useEffect } from 'react';
import { ethers } from 'ethers';
import TokenFactoryABI from './abis/TokenFactory.json';
import WhiteLabelTokenABI from './abis/WhiteLabelToken.json';

const TokenCreator = () => {
  // State variables
  const [provider, setProvider] = useState(null);
  const [signer, setSigner] = useState(null);
  const [factoryContract, setFactoryContract] = useState(null);
  const [account, setAccount] = useState('');
  const [deploymentFee, setDeploymentFee] = useState('');
  const [deployedTokens, setDeployedTokens] = useState([]);
  
  // Form state
  const [tokenForm, setTokenForm] = useState({
    name: '',
    symbol: '',
    decimals: 18,
    initialSupply: '1000000',
    transferFeeRate: 50, // 0.5%
    feeCollector: '',
  });
  
  // Transaction status
  const [txPending, setTxPending] = useState(false);
  const [txHash, setTxHash] = useState('');
  const [txError, setTxError] = useState('');
  
  // Constants
  const FACTORY_ADDRESS = '0x...'; // Address of the deployed factory
  
  // Connect to blockchain
  useEffect(() => {
    const connectBlockchain = async () => {
      try {
        // Check if MetaMask is installed
        if (window.ethereum) {
          // Create provider and signer
          const web3Provider = new ethers.providers.Web3Provider(window.ethereum);
          await window.ethereum.request({ method: 'eth_requestAccounts' });
          const web3Signer = web3Provider.getSigner();
          const userAddress = await web3Signer.getAddress();
          
          // Create contract instance
          const factory = new ethers.Contract(
            FACTORY_ADDRESS,
            TokenFactoryABI.abi,
            web3Signer
          );
          
          // Get deployment fee
          const fee = await factory.deploymentFee();
          
          // Initialize state
          setProvider(web3Provider);
          setSigner(web3Signer);
          setFactoryContract(factory);
          setAccount(userAddress);
          setDeploymentFee(ethers.utils.formatEther(fee));
          setTokenForm(prev => ({ ...prev, feeCollector: userAddress }));
          
          // Load user's tokens
          loadUserTokens(factory, userAddress);
          
          // Setup account change listener
          window.ethereum.on('accountsChanged', (accounts) => {
            if (accounts.length > 0) {
              setAccount(accounts[0]);
              setTokenForm(prev => ({ ...prev, feeCollector: accounts[0] }));
              loadUserTokens(factory, accounts[0]);
            } else {
              setAccount('');
              setDeployedTokens([]);
            }
          });
        } else {
          console.error("Please install MetaMask!");
        }
      } catch (error) {
        console.error("Connection error:", error);
      }
    };
    
    connectBlockchain();
    
    // Cleanup event listeners
    return () => {
      if (window.ethereum) {
        window.ethereum.removeAllListeners('accountsChanged');
      }
    };
  }, []);
  
  // Load user's tokens
  const loadUserTokens = async (factory, address) => {
    try {
      const tokenAddresses = await factory.getTokensByCreator(address);
      
      const tokenPromises = tokenAddresses.map(async (tokenAddress) => {
        const token = new ethers.Contract(
          tokenAddress,
          WhiteLabelTokenABI.abi,
          provider
        );
        
        const [name, symbol, totalSupply, decimals] = await Promise.all([
          token.name(),
          token.symbol(),
          token.totalSupply(),
          token.decimals()
        ]);
        
        return {
          address: tokenAddress,
          name,
          symbol,
          totalSupply: ethers.utils.formatUnits(totalSupply, decimals),
          decimals
        };
      });
      
      const tokens = await Promise.all(tokenPromises);
      setDeployedTokens(tokens);
    } catch (error) {
      console.error("Error loading tokens:", error);
    }
  };
  
  // Handle form changes
  const handleFormChange = (e) => {
    const { name, value } = e.target;
    setTokenForm(prev => ({ ...prev, [name]: value }));
  };
  
  // Deploy new token
  const deployNewToken = async (e) => {
    e.preventDefault();
    setTxPending(true);
    setTxHash('');
    setTxError('');
    
    try {
      // Convert values to appropriate formats
      const decimals = parseInt(tokenForm.decimals);
      const initialSupply = ethers.utils.parseUnits(
        tokenForm.initialSupply, 
        decimals
      );
      const transferFeeRate = parseInt(tokenForm.transferFeeRate);
      
      // Call the factory contract
      const tx = await factoryContract.createToken(
        tokenForm.name,
        tokenForm.symbol,
        decimals,
        initialSupply,
        transferFeeRate,
        tokenForm.feeCollector,
        { value: ethers.utils.parseEther(deploymentFee) }
      );
      
      setTxHash(tx.hash);
      
      // Wait for confirmation
      const receipt = await tx.wait();
      
      // Find the TokenDeployed event to get the deployed token address
      const tokenDeployedEvent = receipt.events.find(
        event => event.event === "TokenDeployed"
      );
      
      // Reload tokens
      await loadUserTokens(factoryContract, account);
      
      // Reset form
      setTokenForm({
        name: '',
        symbol: '',
        decimals: 18,
        initialSupply: '1000000',
        transferFeeRate: 50,
        feeCollector: account,
      });
    } catch (error) {
      console.error("Deployment error:", error);
      setTxError(error.message);
    } finally {
      setTxPending(false);
    }
  };
  
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">White Label Token Creator</h1>
      
      {/* Connection Status */}
      <div className="mb-6 p-4 bg-gray-100 rounded">
        <p>
          <strong>Status:</strong> {account ? 'Connected' : 'Not Connected'}
        </p>
        {account && (
          <>
            <p><strong>Account:</strong> {account}</p>
            <p><strong>Deployment Fee:</strong> {deploymentFee} ETH</p>
          </>
        )}
      </div>
      
      {/* Token Form */}
      <div className="mb-8 p-6 border rounded shadow">
        <h2 className="text-xl font-semibold mb-4">Create New Token</h2>
        
        <form onSubmit={deployNewToken}>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Token Name */}
            <div>
              <label className="block mb-1">Token Name</label>
              <input
                type="text"
                name="name"
                value={tokenForm.name}
                onChange={handleFormChange}
                className="w-full p-2 border rounded"
                placeholder="My Token"
                required
              />
            </div>
            
            {/* Token Symbol */}
            <div>
              <label className="block mb-1">Token Symbol</label>
              <input
                type="text"
                name="symbol"
                value={tokenForm.symbol}
                onChange={handleFormChange}
                className="w-full p-2 border rounded"
                placeholder="MTK"
                required
              />
            </div>
            
            {/* Decimals */}
            <div>
              <label className="block mb-1">Decimals</label>
              <input
                type="number"
                name="decimals"
                value={tokenForm.decimals}
                onChange={handleFormChange}
                className="w-full p-2 border rounded"
                min="0"
                max="18"
                required
              />
            </div>
            
            {/* Initial Supply */}
            <div>
              <label className="block mb-1">Initial Supply</label>
              <input
                type="text"
                name="initialSupply"
                value={tokenForm.initialSupply}
                onChange={handleFormChange}
                className="w-full p-2 border rounded"
                placeholder="1000000"
                required
              />
            </div>
            
            {/* Transfer Fee Rate */}
            <div>
              <label className="block mb-1">Transfer Fee (basis points, 100 = 1%)</label>
              <input
                type="number"
                name="transferFeeRate"
                value={tokenForm.transferFeeRate}
                onChange={handleFormChange}
                className="w-full p-2 border rounded"
                min="0"
                max="1000"
                required
              />
              <small className="text-gray-500">
                {(tokenForm.transferFeeRate / 100).toFixed(2)}% fee per transfer
              </small>
            </div>
            
            {/* Fee Collector */}
            <div>
              <label className="block mb-1">Fee Collector Address</label>
              <input
                type="text"
                name="feeCollector"
                value={tokenForm.feeCollector}
                onChange={handleFormChange}
                className="w-full p-2 border rounded"
                placeholder="0x..."
                required
              />
            </div>
          </div>
          
          {/* Submit Button */}
          <button
            type="submit"
            className="mt-4 px-6 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:bg-gray-400"
            disabled={!account || txPending}
          >
            {txPending ? 'Deploying...' : 'Deploy Token'}
          </button>
          
          {/* Transaction Status */}
          {txHash && (
            <div className="mt-4 p-3 bg-green-100 text-green-800 rounded">
              <p>Transaction submitted: {txHash}</p>
            </div>
          )}
          
          {txError && (
            <div className="mt-4 p-3 bg-red-100 text-red-800 rounded">
              <p>Error: {txError}</p>
            </div>
          )}
        </form>
      </div>
      
      {/* Deployed Tokens */}
      <div>
        <h2 className="text-xl font-semibold mb-4">Your Tokens</h2>
        
        {deployedTokens.length === 0 ? (
          <p>No tokens deployed yet.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full bg-white border">
              <thead>
                <tr>
                  <th className="py-2 px-4 border">Name</th>
                  <th className="py-2 px-4 border">Symbol</th>
                  <th className="py-2 px-4 border">Total Supply</th>
                  <th className="py-2 px-4 border">Address</th>
                  <th className="py-2 px-4 border">Actions</th>
                </tr>
              </thead>
              <tbody>
                {deployedTokens.map((token, index) => (
                  <tr key={index}>
                    <td className="py-2 px-4 border">{token.name}</td>
                    <td className="py-2 px-4 border">{token.symbol}</td>
                    <td className="py-2 px-4 border">{token.totalSupply}</td>
                    <td className="py-2 px-4 border truncate max-w-xs">
                      {token.address}
                    </td>
                    <td className="py-2 px-4 border">
                      <a
                        href={`/manage/${token.address}`