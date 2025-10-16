from __future__ import annotations

import os
from typing import Optional

from algosdk.v2client import algod
from algosdk import account, mnemonic

# ---- Config: TestNet client (Algonode – no token needed) ----
ALGO_ALGOD_URL = os.getenv("ALGO_ALGOD_URL", "https://testnet-api.algonode.cloud")
ALGO_API_KEY = os.getenv("ALGO_API_KEY", "")  # keep hook for other providers
client = algod.AlgodClient(ALGO_API_KEY, ALGO_ALGOD_URL)

# Default placeholder ASA (NFT) id for testing; replace later if you want
DEFAULT_ASA_ID = 745467084


def create_wallet():
    """Create a throwaway wallet keypair and print its info."""
    private_key, address = account.generate_account()
    print("Address:", address)
    print("Mnemonic:", mnemonic.from_private_key(private_key))
    return private_key, address


def holds_asa(address: str, asa_id: int = DEFAULT_ASA_ID) -> bool:
    """Return True if `address` holds > 0 units of the given ASA id."""
    try:
        # Clean up address
        clean_addr = address.strip()
        info = client.account_info(clean_addr)

        for asset in info.get("assets", []):
            if asset.get("asset-id") == asa_id and asset.get("amount", 0) > 0:
                return True
        return False
    except Exception as e:
        print("Error checking ASA:", e)
        return False

def env_asa_id() -> Optional[int]:
    """
    Read the ASA/NFT id from environment variable ALGO_NFT_ASA_ID.
    Returns an int if present/valid, otherwise None.
    """
    raw = os.getenv("ALGO_NFT_ASA_ID", "").strip()
    if not raw:
        return None
    try:
        return int(raw)
    except ValueError:
        return None
