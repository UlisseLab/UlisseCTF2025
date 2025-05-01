// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import {Test, console} from "forge-std/Test.sol";
import {Signer, Message} from "../src/Signer.sol";

contract SignerTest is Test {
    Signer public signer;
    address public admin;
    address public user;

    function setUp() public {
        admin = address(this);
        user = address(0x123);
        signer = new Signer();
    }

    function test_InitialAdmin() public {
        assertEq(signer.admin(), admin);
    }

    /*
    function test_EmitCrossChainMessage() public {
        bytes memory messageBody = "Hello, cross-chain!";
        uint256 value = 1 ether;

        vm.deal(admin, value);

        vm.expectEmit(true, false, false, true);
        emit Signer.MessageEmitted(Message({version : 2, body: messageBody, val: value}));

        signer.emitCrossChainMessage{value: value}(messageBody);

        assertEq(address(signer).balance, value);
    }
     */

    function test_WithdrawByAdmin() public {
        uint256 deposit = 2 ether;
        vm.deal(address(this), deposit);
        payable(address(signer)).transfer(deposit);

        assertEq(address(signer).balance, deposit);

        vm.expectEmit(true, true, false, true);
        emit Signer.FundsWithdrawn(admin, deposit);

        signer.withdraw();

        assertEq(address(signer).balance, 0);
        assertEq(admin.balance, deposit);
    }

    function testFail_WithdrawByNonAdmin() public {
        vm.prank(user);
        signer.withdraw();
    }

    function test_TransferOwnership() public {
        assertEq(signer.admin(), admin);

        vm.expectEmit(true, true, false, false);
        emit Signer.OwnershipTransferred(admin, user);

        signer.transferOwnership(user);

        assertEq(signer.admin(), user);
    }

    function testFail_TransferOwnershipByNonAdmin() public {
        vm.prank(user);
        signer.transferOwnership(user);
    }

    function testFail_TransferOwnershipToZeroAddress() public {
        signer.transferOwnership(address(0));
    }

    function test_ReceiveEther() public {
        uint256 amount = 1 ether;
        vm.deal(user, amount);

        vm.prank(user);
        payable(address(signer)).transfer(amount);

        assertEq(address(signer).balance, amount);
    }

    receive() external payable {}
}
