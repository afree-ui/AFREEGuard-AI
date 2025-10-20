from algosdk import account, transaction, mnemonic
from algosdk.v2client import algod
import json, time

ALGOD_URL = "https://testnet-api.algonode.cloud"
ALGOD_TOKEN = ""
ALGOD_CLIENT = algod.AlgodClient(ALGOD_TOKEN, ALGOD_URL)

# === Your wallet mnemonic (testnet) ===
ALGO_MNEMONIC = "keen daughter jelly actress heart over child tongue mystery bag inflict setup convince path space naive forward economy desk lottery master engine marble above practice"

# ✅ Convert mnemonic to private key and derive public address
sender_private_key = mnemonic.to_private_key(ALGO_MNEMONIC)
sender_address = account.address_from_private_key(sender_private_key)
print("🧠 Wallet address:", sender_address)

# === Simulated AFREEGuard event ===
note_json = {
    "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "action": "security_alert",
    "blocked": True,
    "reason": "Simulated intrusion detected by AFREEGuard AI"
}
note = json.dumps(note_json).encode()

# === Create and send transaction ===
params = ALGOD_CLIENT.suggested_params()
txn = transaction.PaymentTxn(
    sender=sender_address,
    sp=params,
    receiver=sender_address,
    amt=0,
    note=note
)

signed_txn = txn.sign(sender_private_key)
txid = ALGOD_CLIENT.send_transaction(signed_txn)
print("✅ Sent transaction with note. TXID:", txid)