// deployment.js - Script for deploying the White Label Token Factory
const { ethers } = require("hardhat");

async function main() {
  console.log("Starting deployment of White Label Token ecosystem...");

  // Get deployer account
  const [deployer] = await ethers.getSigners();
  console.log(`Deploying contracts with the account: ${deployer.address}`);
  
  const initialBalance = await deployer.getBalance();
  console.log(`Account balance: ${ethers.utils.formatEther(initialBalance)} ETH`);

  // Deploy TokenFactory contract
  const deploymentFee = ethers.utils.parseEther("0.05"); // 0.05 ETH deployment fee
  const feeReceiver = deployer.address; // Deployer receives fees initially
  
  console.log("Deploying TokenFactory...");
  const TokenFactory = await ethers.getContractFactory("TokenFactory");
  const tokenFactory = await TokenFactory.deploy(deploymentFee, feeReceiver);
  await tokenFactory.deployed();
  
  console.log(`TokenFactory deployed to: ${tokenFactory.address}`);

  // Deploy a sample token through the factory for testing
  console.log("Deploying a sample token through the factory...");
  
  const tokenParams = {
    name: "Sample Token",
    symbol: "SMPL",
    decimals: 18,
    initialSupply: ethers.utils.parseEther("1000000"), // 1 million tokens
    transferFeeRate: 50, // 0.5% transfer fee
    feeCollector: deployer.address
  };
  
  const tx = await tokenFactory.createToken(
    tokenParams.name,
    tokenParams.symbol,
    tokenParams.decimals,
    tokenParams.initialSupply,
    tokenParams.transferFeeRate,
    tokenParams.feeCollector,
    { value: deploymentFee }
  );
  
  const receipt = await tx.wait();
  
  // Find the TokenDeployed event to get the deployed token address
  const tokenDeployedEvent = receipt.events.find(
    event => event.event === "TokenDeployed"
  );
  
  const deployedTokenAddress = tokenDeployedEvent.args.tokenAddress;
  console.log(`Sample token deployed to: ${deployedTokenAddress}`);

  // Verify contract on Etherscan (if on a supported network)
  if (network.name !== "hardhat" && network.name !== "localhost") {
    console.log("Waiting for block confirmations...");
    await tx.wait(5); // Wait for 5 confirmations
    
    console.log("Verifying contracts on Etherscan...");
    
    // Verify the factory
    await hre.run("verify:verify", {
      address: tokenFactory.address,
      constructorArguments: [deploymentFee, feeReceiver],
    });
    
    // Get the WhiteLabelToken ABI to find constructor arguments
    const WhiteLabelToken = await ethers.getContractFactory("WhiteLabelToken");
    
    // Verify the token
    await hre.run("verify:verify", {
      address: deployedTokenAddress,
      constructorArguments: [
        tokenParams.name,
        tokenParams.symbol,
        tokenParams.decimals,
        tokenParams.initialSupply,
        tokenParams.transferFeeRate,
        tokenParams.feeCollector
      ],
    });
  }

  // Calculate gas used
  const finalBalance = await deployer.getBalance();
  const cost = initialBalance.sub(finalBalance);
  
  console.log("Deployment complete!");
  console.log(`Total cost: ${ethers.utils.formatEther(cost)} ETH`);
  console.log(`TokenFactory: ${tokenFactory.address}`);
  console.log(`Sample Token: ${deployedTokenAddress}`);
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
