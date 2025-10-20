import json
import os
from datetime import datetime, timezone
from algosdk.v2client import algod
from algosdk import mnemonic, transaction, account
from algosdk.transaction import wait_for_confirmation

def _client():
    node = os.getenv("ALGO_NODE_URL", "https://testnet-api.algonode.cloud")
    key = os.getenv("ALGO_API_KEY", "")
    headers = {"X-API-Key": key} if key else {}
    return algod.AlgodClient(key, node, headers)


def log_event_to_algorand(event):
    """
    Sends a small transaction with event summary to Algorand TestNet.
    Returns the transaction hash (txid) if successful.
    """
    try:
        mn = "Keen daughter jelly actress heart over child tongue mystery bag inflict setup convince path space naive forward economy desk lottery master engine marble above practice"
        sk = mnemonic.to_private_key(mn)
        addr = account.address_from_private_key(sk)

        client = _client()
        params = client.suggested_params()

        note = json.dumps(event).encode()
        txn = transaction.PaymentTxn(
            sender=addr,
            sp=params,
            receiver=addr,
            amt=0,
            note=note,
        )

        signed_txn = txn.sign(sk)
        txid = client.send_transaction(signed_txn)
        wait_for_confirmation(client, txid, 4)

        print("✅ Transaction sent successfully!")
        print(f"🔗 Transaction ID: {txid}")

        # ✳️ Save event locally for AFREEGuard AI Dashboard
        logs_dir = "logs"
        os.makedirs(logs_dir, exist_ok=True)

        with open(os.path.join(logs_dir, "events.jsonl"), "a") as f:
            json.dump({
                "ts": str(datetime.now(timezone.utc)),
                "domain": "afreeguard.ai",
                "action": event.get("action", "unknown"),
                "txid": txid,
                "blocked": event.get("blocked", False),
                "reason": event.get("reason", "manual test")
            }, f)
            f.write("\n")

        return txid

    except Exception as e:
        print(f"[ALG] Logging error: {e}")
        return None

if __name__ == "__main__":
    test_event = {
        "ts": "2025-10-18T22:00:00Z",
        "domain": "afreeguard.ai",
        "action": "security_log_test",
        "blocked": False,
        "reason": "manual test"
    }
    log_event_to_algorand(test_event)