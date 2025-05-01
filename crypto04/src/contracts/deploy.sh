#!/bin/sh
#default anvil priv key, just to send funds, fund 1eth to deployer and player
cast send $ETH_PUB_ADMIN --value 1000000000000000000 --rpc-url $1 --private-key 0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80
cast send $ETH_PUBLIC_KEY --value 1000000000000000000 --rpc-url $1 --private-key 0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80

cast balance --rpc-url $1 $ETH_PUBLIC_KEY
forge script script/Signer.s.sol --rpc-url $1 --private-key $ETH_PRIVATE_KEY --broadcast
