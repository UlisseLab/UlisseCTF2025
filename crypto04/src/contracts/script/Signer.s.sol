// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import "forge-std/Script.sol";
import "../src/Signer.sol";

contract DeploySigner is Script {
    function run() external {
        vm.startBroadcast();

        // Deploy the Signer contract
        Signer signer = new Signer{value: 1337}();

        console.log("Signer deployed to:", address(signer));

        vm.stopBroadcast();
    }
}
