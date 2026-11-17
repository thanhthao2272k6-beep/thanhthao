from __future__ import annotations

import json
import os
from pathlib import Path

from solcx import compile_source, get_installed_solc_versions
from web3 import Web3


ROOT = Path(__file__).resolve().parent.parent
CONTRACT_PATH = ROOT / "contracts" / "ScholarshipApplicationTracker.sol"
DEPLOYMENT_PATH = ROOT / "web" / "deployment.json"
SOLC_VERSION = "0.8.24"
EXPECTED_CHAIN_ID = 1337


def main() -> None:
    rpc_url = os.environ.get("GANACHE_RPC_URL", "http://127.0.0.1:7545")
    web3 = Web3(Web3.HTTPProvider(rpc_url, request_kwargs={"timeout": 30}))

    if not web3.is_connected():
        raise ConnectionError(f"Cannot connect to Ganache at {rpc_url}")
    if web3.eth.chain_id != EXPECTED_CHAIN_ID:
        raise ValueError(
            f"Expected Ganache chain ID {EXPECTED_CHAIN_ID}, got {web3.eth.chain_id}"
        )
    if SOLC_VERSION not in {str(version) for version in get_installed_solc_versions()}:
        raise RuntimeError(
            "Solidity compiler 0.8.24 is not installed. Run "
            "\"python -c \\\"from solcx import install_solc; "
            "install_solc('0.8.24')\\\"\" first."
        )

    accounts = web3.eth.accounts
    if not accounts:
        raise RuntimeError(f"No Ganache test accounts available at {rpc_url}")
    administrator = accounts[0]
    source = CONTRACT_PATH.read_text(encoding="utf-8")
    compiled = compile_source(
        source,
        output_values=["abi", "bin"],
        solc_version=SOLC_VERSION,
        optimize=True,
        optimize_runs=200,
    )
    _, artifact = next(iter(compiled.items()))
    factory = web3.eth.contract(abi=artifact["abi"], bytecode=artifact["bin"])
    transaction_hash = factory.constructor().transact({"from": administrator})
    receipt = web3.eth.wait_for_transaction_receipt(transaction_hash)
    if receipt.status != 1 or receipt.contractAddress is None:
        raise RuntimeError(f"Contract deployment failed: {transaction_hash.hex()}")

    deployment = {
        "address": receipt.contractAddress,
        "abi": artifact["abi"],
        "network": {"chainId": web3.eth.chain_id, "rpcUrl": rpc_url},
        "administrator": administrator,
    }
    DEPLOYMENT_PATH.write_text(
        f"{json.dumps(deployment, indent=2)}\n",
        encoding="utf-8",
    )
    print(f"Contract deployed to {receipt.contractAddress}")
    print(f"Administrator: {administrator}")
    print(f"Browser configuration written to {DEPLOYMENT_PATH}")


if __name__ == "__main__":
    main()
