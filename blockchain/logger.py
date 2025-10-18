import json, os
from algosdk.v2client import algod
from algosdk import mnemonic, transaction, account

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
        mn = os.environ["ALGO_MNEMONIC"]
        sk = mnemonic.to_private_key(mn)
        addr = account.address_from_private_key(sk)

        client = _client()
        params = client.suggested_params()

        note = json.dumps({
            "ts": event.get("ts"),
            "domain": event.get("domain"),
            "action": event.get("action"),
            "blocked": event.get("blocked"),
            "reason": event.get("reason")
        }).encode()

        txn = transaction.PaymentTxn(
            sender=addr,
            sp=params,
            receiver=addr,
            amt=0,
            note=note
        )

        stx = txn.sign(sk)
        txid = client.send_transaction(stx)

        from algosdk.future.transaction import wait_for_confirmation
        wait_for_confirmation(client, txid, 4)
        return txid
    except Exception as e:
        print(f"[ALG] Logging error: {e}")
        return None
