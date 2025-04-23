# Bridgeeer

|         |                   |
| ------- | ----------------- |
| Authors | Renato <@renny>   |
| Points  | 500               |
| Tags    | crypto,blockchain |

## Challenge Description

Im building a brand new bridge for Ethereum L2s. Can you make sure there isnt a billion dollar bug in it?

**Please only use the provided endpoint to flag, test locally otherwise!**

You can use `0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d` as a priv key for local playtesting

This challenge deploys an instance per team, interact with the endpoint using the provided client (the pow is deliberately hard)

```
138.199.236.43:5000
```

---

Note: the flag endpoint is at `/flag`

## Overview

The challenge setup mimicks an unfinished bridge protocol, made up of an onchain contract and an offchain signer.

There are few methods on the contract, with one of them critically being able to emit cross chain messages. These events are parsed and signed via ECDSA by the signer (to be presumably checked and processed on another chain).

### Reasoning

We first notice that the endgoal of this challenge is to hijack control of the smart contract by overriding the `owner` field.

We can also notice the wide degree of control that we in the messages being signed : any sequence of bytes will do.

Furthermore, the signer key being used for messages corresponds to the public key of the owner of the smart contract endpoint.

### Solution

Thus we can make the signer sign a transaction calling `transferOwnership`, provided we correctly encode said tx.

The player will need to properly [rlp encode](https://ethereum.org/en/developers/docs/data-structures-and-encoding/rlp/) the unsigned transaction, then emit that as a cross chain message, to then submit the forged signed transaction, made up of the previously encoded tx data, followed by the signature given by the offchain signer.
