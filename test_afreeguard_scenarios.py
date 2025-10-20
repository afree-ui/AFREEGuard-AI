from algosdk import account, transaction, mnemonic
from algosdk.v2client import algod
import json, time

# === Blockchain setup ===
ALGOD_URL = "https://testnet-api.algonode.cloud"
ALGOD_TOKEN = ""
ALGOD_CLIENT = algod.AlgodClient(ALGOD_TOKEN, ALGOD_URL)

# === AFREECHAIN test wallet ===
ALGO_MNEMONIC = "keen daughter jelly actress heart over child tongue mystery bag inflict setup convince path space naive forward economy desk lottery master engine marble above practice"
sender_private_key = mnemonic.to_private_key(ALGO_MNEMONIC)
sender_address = account.address_from_private_key(sender_private_key)

# === Define test scenarios ===
SCENARIOS = [
    {
        "action": "financial_advice",
        "blocked": True,
        "reason": "Financial advisory detected — user not licensed to perform financial advice under AFREEGuard AI policy."
    },
    {
        "action": "wallet_verification",
        "blocked": True,
        "reason": "Invalid wallet address — failed checksum or format validation."
    },
    {
        "action": "nft_verification",
        "blocked": True,
        "reason": "Access denied — user wallet contains no required NFT for permission access."
    },
    {
        "action": "nft_verification",
        "blocked": False,
        "reason": "Validated NFT ownership — permission granted for protected access."
    }
]

# === Helper: Send event to blockchain ===
def send_afreeguard_event(event):
    note_json = {
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "action": event["action"],
        "blocked": event["blocked"],
        "reason": event["reason"]
    }
    note = json.dumps(note_json).encode()

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
    print(f"✅ [{event['action']}] Blocked={event['blocked']} | TXID={txid}")
    return txid


print("🚀 Running AFREEGuard AI Security Policy Test Suite\n")

# === Execute all test scenarios ===
for scenario in SCENARIOS:
    txid = send_afreeguard_event(scenario)
    time.sleep(10)  # wait 10s between logs

print("\n✅ All 4 AFREEGuard AI scenarios have been simulated and logged to the blockchain.")