// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import "forge-std/Script.sol";
import "../src/Signer.sol";  // Import the Signer contract

contract SignMessage is Script {
    function run() external {
        vm.startBroadcast(); 

        // Fetch the deployed contract address from environment variables
        address payable signerAddress = payable(vm.envAddress("CONTRACT_ADDR"));
        Signer signer = Signer(signerAddress);  // Now it correctly converts

        // Message to be signed on-chain
        bytes memory messageBody = abi.encodePacked("Hello, On-Chain Signing");

        // Send the message with 0.1 ETH attached
        signer.emitCrossChainMessage(messageBody);

        vm.stopBroadcast();
    }
}
