// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

struct Message {
    bytes body;
}

contract Signer {
    address public admin;
    address originalAdmin;

    event MessageEmitted(Message m);
    event FundsWithdrawn(address indexed admin, uint256 amount);
    event OwnershipTransferred(address indexed previousAdmin, address indexed newAdmin);

    constructor() payable {
        admin = msg.sender;
        originalAdmin = msg.sender;
        emit OwnershipTransferred(address(0), admin);
    }

    modifier onlyAdmin() {
        require(msg.sender == admin, "Not the admin");
        _;
    }

    /// @notice Emits a cross-chain message
    function emitCrossChainMessage(bytes memory body) public {
        emit MessageEmitted(Message(body));
    }

    function isSolved() public view returns (bool) {
        return admin != originalAdmin;
    }

    /// @notice Allows the admin to withdraw all contract funds. FOR EMERGENCIES ONLY!!!
    function withdraw() external onlyAdmin {
        uint256 balance = address(this).balance;
        require(balance > 0, "No funds available");
        payable(admin).transfer(balance);
        emit FundsWithdrawn(admin, balance);
    }

    /// @notice Allows the admin to transfer ownership.
    function transferOwnership(address newAdmin) external onlyAdmin {
        require(newAdmin != address(0), "New admin cannot be zero address");
        emit OwnershipTransferred(admin, newAdmin);
        admin = newAdmin;
    }

    /// @notice Fallback function to receive Ether.
    receive() external payable {}

    /// @notice Fallback function for unexpected calls.
    fallback() external payable {}
}
