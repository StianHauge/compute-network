// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title AverraToken
 * @dev ERC20 Token for the Averra Compute Network.
 * The Control Plane (owner) mints tokens directly to Node Operators' 
 * wallets when they successfully complete cryptographically verified AI Inference jobs.
 */
contract AverraToken is ERC20, Ownable {
    
    // Mapping to track total compute credits burned by an address
    mapping(address => uint256) public computeCreditsBurned;

    // Events for transparency
    event RewardMinted(address indexed nodeOperator, uint256 amount, string jobId);
    event TokensBurnedForCompute(address indexed developer, uint256 amount);

    constructor() ERC20("Averra Network", "AVR") Ownable(msg.sender) {
        // Initial supply for ecosystem fund, liquidity pools, etc.
        _mint(msg.sender, 100000000 * 10 ** decimals());
    }

    /**
     * @dev Called by the Averra Control Plane to issue rewards for AI generation
     */
    function mintReward(address nodeOperator, uint256 amount, string memory jobId) external onlyOwner {
        _mint(nodeOperator, amount);
        emit RewardMinted(nodeOperator, amount, jobId);
    }
    
    /**
     * @dev Called when a developer spends AVR tokens to run inference on the network.
     * Tokens are burned (deflationary) creating a continuous buy pressure.
     */
    function burnForCompute(uint256 amount) external {
        _burn(msg.sender, amount);
        computeCreditsBurned[msg.sender] += amount;
        emit TokensBurnedForCompute(msg.sender, amount);
    }
}
