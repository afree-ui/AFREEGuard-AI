# scripts/mint_and_send.py
import os, time
from algosdk.v2client import algod, indexer
from algosdk import account, mnemonic
from algosdk import transaction as tx

ALGOD_URL     = os.getenv("ALGO_ALGOD_URL", "https://testnet-api.algonode.cloud")
INDEXER_URL   = os.getenv("ALGO_INDEXER_URL", "https://testnet-idx.algonode.cloud")
ALGOD_TOKEN   = os.getenv("ALGO_API_KEY", "")           # none needed for Algonode
PARA_ADDR     = os.getenv("PARA_ADDR")                  # your ParaWallet address

if not PARA_ADDR:
    raise SystemExit("Set PARA_ADDR to your ParaWallet TestNet address")

algod_client   = algod.AlgodClient(ALGOD_TOKEN, ALGOD_URL)
indexer_client = indexer.IndexerClient(ALGOD_TOKEN, INDEXER_URL)

def wait(txid, max_rounds=30):
    for _ in range(max_rounds):
        try:
            p = algod_client.pending_transaction_info(txid)
            if p.get("confirmed-round"):
                return p
        except Exception:
            pass
        time.sleep(1)
    raise RuntimeError("Timeout waiting for tx")

def main():
    # 1) make a temporary creator account (DO NOT share this mnemonic)
    creator_sk, creator_addr = account.generate_account()
    print("Creator address:", creator_addr)
    print("Creator mnemonic (save temporarily if you want):")
    print(mnemonic.from_private_key(creator_sk))
    print("\nFund the creator address on TESTNET from a faucet, then press Enter...")
    input()

    # 2) create a 1-unit, 0-decimals ASA (NFT)
    params = algod_client.suggested_params()
    txn = tx.AssetConfigTxn(
        sender=creator_addr,
        sp=params,
        total=1,
        default_frozen=False,
        unit_name="POCNFT",
        asset_name="AFREEGuard AI NFT",
        manager=creator_addr,
        reserve=creator_addr,
        freeze=creator_addr,
        clawback=creator_addr,
        decimals=0,
    )
    stxn = txn.sign(creator_sk)
    txid = algod_client.send_transaction(stxn)
    info = wait(txid)
    asa_id = info["asset-index"]
    print("Created ASA ID:", asa_id)

    # 3) remind to OPT-IN in ParaWallet (required before receiving)
    print("\nOpen ParaWallet (TestNet) and **opt-in** to ASA:", asa_id)
    print("In ParaWallet, add the asset by ID and tap Opt-in.")
    input("Press Enter AFTER the wallet is opted-in...")

    # 4) transfer 1 unit to ParaWallet
    params = algod_client.suggested_params()
    send = tx.AssetTransferTxn(
        sender=creator_addr,
        sp=params,
        receiver=PARA_ADDR,
        amt=1,
        index=asa_id,
    )
    stxn = send.sign(creator_sk)
    txid = algod_client.send_transaction(stxn)
    wait(txid)
    print("Transferred 1 unit to:", PARA_ADDR)

    print("\nSUCCESS. Use this in your PoC:")
    print("  export ALGO_NFT_ASA_ID={}".format(asa_id))

if __name__ == "__main__":
    main()
