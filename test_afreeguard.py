from algosdk.v2client import algod
from algosdk import account, transaction
import base64, json, os, time

# ✅ Load environment variables
ALGOD_URL = os.getenv("ALGO_NODE_URL", "https://testnet-api.algonode.cloud")
ALGOD_KEY = os.getenv("ALGO_API_KEY", "")
ALGOD_CLIENT = algod.AlgodClient(ALGOD_KEY, ALGOD_URL)
SENDER = os.getenv("SONYLXSLS4WV6DW4YGILBQBLIFH74CJAXMFXK5CZVXCQGO6LQK7GCRWJAY")
ALGO_MNEMONIC =keen daughter jelly actress heart over child tongue mystery bag inflict setup convince path space naive forward economy desk lottery master engine marble above practice

# ✅ Step 1: Define harmless (allowed) transaction note
note = {
    "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "action": "allow",
    "blocked": False,
    "reason": "Normal wallet-to-wallet transfer"
}

# ✅ Step 2: Create a zero-Algo test transaction to self
params = ALGOD_CLIENT.suggested_params()
txn = transaction.PaymentTxn(
    sender=SENDER,
    sp=params,
    receiver=SENDER,
    amt=0,
    note=base64.b64encode(json.dumps(note).encode())
)

# ✅ Step 3: Sign and send
signed_txn = txn.sign_with_mnemonic(MNEMONIC)
txid = ALGOD_CLIENT.send_transaction(signed_txn)

print(f"✅ Test transaction sent successfully!")
print(f"🔗 TxID: {txid}")
print(f"🧠 Note data: {note}")