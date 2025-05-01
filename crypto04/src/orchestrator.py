from flask import Flask, request, jsonify, Response
import docker
import random
import string
import requests
import time
import subprocess
import threading
import signal
import os
import hashlib
import base64
from web3 import Web3

app = Flask(__name__)
client = docker.DockerClient(base_url='unix://var/run/docker.sock')
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS", "0x9fE46736679d2D9a65F0992F2272dE9f3c7fa6e0")
# default to anvil defaults
ETH_PRIVATE_KEY = os.getenv("ETH_PRIVATE_KEY", "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80")
BASE = os.getenv("BASE", "localhost")

anvil_map = {}
pow_challenges = {}  

@app.route('/pow_challenge', methods=['GET'])
def issue_pow_challenge():
    challenge = base64.urlsafe_b64encode(os.urandom(8)).decode('utf-8')  
    difficulty = 24
    
    pow_challenges[challenge] = difficulty
    
    return jsonify({
        "challenge": challenge,
        "difficulty": difficulty
    })

def get_random_path():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))

def cleanup(sig, frame):
    print("CLEANUPPP", flush=True)
    for path_hash in anvil_map.keys():
        print(path_hash, flush=True)
        kill_instance(path_hash)

def kill_instance(path_hash):
    anvil_container = client.containers.get(f"anvil-{path_hash}")
    anvil_container.stop()
    anvil_container.remove()

    signer_container = client.containers.get(f"signer-{path_hash}")
    signer_container.stop()
    signer_container.remove()
    print(f"{path_hash} removed", flush=True)

@app.route('/spawn', methods=['POST'])
def spawn():

    challenge = request.json.get("challenge")
    nonce = request.json.get("nonce")
    
    if challenge not in pow_challenges:
        return jsonify({"error": "Invalid or expired challenge"}), 403
    
    difficulty = pow_challenges[challenge]
    
    target_nibbles = difficulty // 4
    target_prefix = "0" * target_nibbles
    
    digest = hashlib.sha256((challenge + nonce).encode()).hexdigest()
    if not digest.startswith(target_prefix):
        return jsonify({"error": "PoW invalid"}), 403
    
    # 4. If valid, remove the challenge from memory so it can't be reused
    del pow_challenges[challenge]

    path = get_random_path()
    anvil_port = random.randint(8000, 8999)
    signer_port = random.randint(9000, 9999)

    MNEMONIC = os.environ.get('MNEMONIC', "test test test test test test test test test test test junk")

    # 1️⃣ Start Anvil container
    anvil_container = client.containers.run(
        'ghcr.io/foundry-rs/foundry',
        'anvil --host 0.0.0.0',
        detach=True,
        network='orchestrator-net',
        environment=[
            'ANVIL_IP_ADDR=0.0.0.0',
            #TODO manage secrets
            f'MNEMONIC={MNEMONIC}'
        ],
        ports={'8545/tcp': anvil_port},
        name=f"anvil-{path}"
    )

    # Wait a bit to make sure Anvil is responsive
    time.sleep(2)

    f = open("/tmp/sos", "w+")

    #deploy contract with foundry
    result = subprocess.run(
        f"cd /app/contracts && bash deploy.sh http://anvil-{path}:8545/",
        shell=True,
        capture_output=True,
        text=True,
        executable="/bin/bash",
    )

    print("✅ STDOUT:\n", result.stdout, file=f)
    print("✅ STDERR:\n", result.stderr, file=f)

    # 2️⃣ Start signer container, connected to the just-launched Anvil
    signer_container = client.containers.run(
        'offchain-signer',  # Replace with your signer image name
        detach=True,
        network='orchestrator-net',
        environment={
            "ETH_NODE_URL": f"http://anvil-{path}:8545",
            "CONTRACT_ADDRESS": CONTRACT_ADDRESS,
            "ETH_PRIVATE_KEY": ETH_PRIVATE_KEY
        },
        ports={'5001/tcp': signer_port},
        name=f"signer-{path}"
    )

    #start the kill machine
    threading.Timer(300, kill_instance, args=[path]).start()

    # 3️⃣ Track the mapping
    anvil_map[path] = {
        "anvil_port": anvil_port,
        "signer_port": signer_port
    }

    return jsonify({
        "anvil_url": f"http://{BASE}:5000/{path}",
        "signer_url": f"http://{BASE}:5000/{path}/signer",
        "signer_pubkey": "0xfBE1c99586903F72d37cFf5bCd74494b69D8235f",
        "private_key": "0x7791308748d21be53a3fadcf3af371bf8fccb6297c565aadbfd57c59c86b2dee",
        "public_key": "0x0DB7eCC56Ee1D6C977f393E67e46a3360b80a145",
        "contract_address": CONTRACT_ADDRESS
    })

@app.route('/<path_hash>', methods=['GET', 'POST'])
def proxy(path_hash):

    port = anvil_map[path_hash]["anvil_port"]

    # Build the full URL (strip the hash from the path)
    url = f"http://anvil-{path_hash}:8545"

    print("URL ANVIL")

    try:
        resp = requests.request(
            method=request.method,
            url=url,
            headers={key: value for (key, value) in request.headers if key.lower() != 'host'},
            data=request.get_data(),
            cookies=request.cookies,
            allow_redirects=False,
        )

        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        headers = [(k, v) for k, v in resp.headers.items() if k.lower() not in excluded_headers]

        return Response(resp.content, resp.status_code, headers)

    except Exception as e:
        return f"Proxy error: {str(e)}", 500


@app.route('/<path_hash>/signer', methods=['GET', 'POST'])
def proxy_signer(path_hash):
    print(anvil_map)
    port = anvil_map[path_hash]["signer_port"]
    print(request.full_path)

    url = f"http://signer-{path_hash}:5001/latest_event"

    print(url)
    
    try:
        resp = requests.request(
            method=request.method,
            url=url,
            headers={k: v for k, v in request.headers if k.lower() != 'host'},
            data=request.get_data(),
            cookies=request.cookies,
            allow_redirects=False,
        )
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        headers = [(k, v) for k, v in resp.headers.items() if k.lower() not in excluded_headers]
        return Response(resp.content, resp.status_code, headers)
    except Exception as e:
        return f"Proxy error: {str(e)}", 500

@app.route('/<path_hash>/flag', methods=['GET'])
def check_flag(path_hash):
    info = anvil_map.get(path_hash)
    print(anvil_map)
    if not info:
        return "Invalid path", 404

    url = f"http://anvil-{path_hash}:8545"

    minimal_abi = [{
        "constant": True,
        "inputs": [],
        "name": "isSolved",
        "outputs": [{"name": "", "type": "bool"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    }]

    try:
        w3 = Web3(Web3.HTTPProvider(url))
        contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=minimal_abi)
        solved = contract.functions.isSolved().call()

        flag = os.environ.get("FLAG", "UlisseCTF{fake_flag}")

        if solved:
            return flag
        else:
            return "You wish... solve the chall first"
    except Exception as e:
        return f"Contract call failed: {str(e)}", 500


if __name__ == '__main__':
    signal.signal(signal.SIGTERM, cleanup)
    app.run(host='0.0.0.0', port=5000)




