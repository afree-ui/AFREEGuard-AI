# server.py
from flask import Flask, jsonify
from algosdk.v2client import algod, indexer
from datetime import datetime
from flask_cors import CORS
import os

# === Flask Setup ===
app = Flask(__name__)
CORS(app)

# === Algorand Clients ===
ALGOD_URL = "https://testnet-api.algonode.cloud"
INDEXER_URL = "https://testnet-idx.algonode.cloud"

client = algod.AlgodClient("", ALGOD_URL)
indexer_client = indexer.IndexerClient("", INDEXER_URL)

# === Health Check Endpoint ===
@app.route("/", methods=["GET"])
def root():
    status = client.status()
    return jsonify({
        "message": "✅ AFREEGuard AI backend running on Algorand TestNet",
        "network": "Algorand TestNet",
        "status": status
    }), 200

# === Blockchain Logs Endpoint ===
@app.route("/api/logs", methods=["GET"])
def get_logs():
    """Fetch recent transactions from Algorand TestNet using Indexer"""
    try:
        # Your monitored wallet address
        address = os.getenv("AFREECHAIN_WALLET", "SONYLXSLS4W6DW4YGILBQBLIFH74CJAXMFX5CZVXCQG06LQK7GCRWJAY")

        # Fetch recent transactions
        response = indexer_client.search_transactions_by_address(address, limit=10)
        txns = response.get("transactions", [])
        logs = []

        for tx in txns:
            logs.append({
                "ts": datetime.utcfromtimestamp(tx.get("round-time", 0)).isoformat(),
                "action": tx.get("tx-type", "unknown"),
                "blocked": False,  # Placeholder for AI rules
                "reason": "Fetched via Algorand Indexer",
                "txid": tx.get("id", "N/A"),
                "params": {
                    "sender": tx.get("sender", ""),
                    "fee": tx.get("fee", 0),
                    "round": tx.get("confirmed-round", ""),
                    "receiver": tx.get("payment-transaction", {}).get("receiver", ""),
                    "amount": tx.get("payment-transaction", {}).get("amount", 0)
                }
            })

        return jsonify({"events": logs}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# === Reset Logs Placeholder (optional) ===
@app.route("/api/reset", methods=["POST"])
def reset_logs():
    return jsonify({"message": "Logs cleared successfully (mock endpoint)."}), 200

# === Run Server ===
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8502)