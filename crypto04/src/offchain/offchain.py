import os
import json
import time
import threading
from flask import Flask, jsonify
from web3 import Web3
from eth_keys import keys

app = Flask(__name__)

# Load configuration from environment variables
eth_node_url = os.getenv("ETH_NODE_URL", "http://localhost:8545")
contract_address = os.getenv("CONTRACT_ADDRESS", "0x9e8123cd548F36F6E9A806f9A6346CF246E940bd")
# default to anvil defaults
eth_private_key = os.getenv(
    "ETH_PRIVATE_KEY",
    "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
)

w3 = Web3(Web3.HTTPProvider(eth_node_url))

# Load ABI from a local JSON file (make sure abi.json is in the same folder)
with open("./Signer.json", "r") as f:
    abi = json.load(f)["abi"]

contract = w3.eth.contract(address=contract_address, abi=abi)

# Global variable to store the latest event raw bytes
latest_event_raw = None

@app.route('/latest_event', methods=['GET'])
def get_latest_event():
    global latest_event_raw

    event_filter = contract.events.MessageEmitted.create_filter(from_block='0x0')
    try:
        new_events = event_filter.get_new_entries()
        print(len(new_events), new_events, contract_address)
        for event in new_events:
            # Extract event struct (now the Message struct only has the 'body' field)
            message = event["args"]["m"]
            body = message["body"]

            # Set latest_event_raw to the message body bytes
            latest_event_raw = body

            print("Received new event:", latest_event_raw.hex())

    except Exception as e:
        print("Error in event listener:", e)

    if latest_event_raw is None:
        return jsonify({"error": "No event received yet"}), 404

    # Compute the keccak hash of the raw event bytes
    event_hash = w3.keccak(latest_event_raw)
    print("Event hash:", event_hash.hex())

    # Sign the hash directly using eth_keys (without EIP-191 prefix)
    private_key_bytes = bytes.fromhex(eth_private_key[2:])  # Remove '0x'
    priv_key = keys.PrivateKey(private_key_bytes)
    signature = priv_key.sign_msg_hash(event_hash)

    print("SIG: ", signature.vrs)

    return jsonify({
        "raw_event": latest_event_raw.hex(),
        "event_hash": event_hash.hex(),
        "v": signature.v,
        "r": hex(signature.r),
        "s": hex(signature.s),
        "signature": signature.to_bytes().hex()
    })

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001, debug=False)
