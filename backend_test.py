import os
from flask import Flask, jsonify
from flask_cors import CORS
from algosdk.v2client import algod

print("\n⚙️  RUNNING FILE PATH =>", os.path.abspath(__file__), "\n")

# Flask setup
app = Flask(__name__)
CORS(app)
app.url_map.strict_slashes = False  # allow /api/logs and /api/logs/

# Algorand client setup
ALGOD_API = "https://testnet-api.algonode.cloud"
ALGOD_TOKEN = ""
client = algod.AlgodClient(ALGOD_TOKEN, ALGOD_API)

# === ROUTES ===

@app.route("/")
def home():
    return jsonify({"message": "Backend is live ✅"})

@app.route("/routes")
def list_routes():
    """List all registered Flask routes for debugging"""
    import urllib
    routes = []
    for rule in app.url_map.iter_rules():
        methods = ",".join(rule.methods)
        url = urllib.parse.unquote(str(rule))
        routes.append({"path": url, "methods": methods})
    return jsonify(routes)

@app.route("/api/logs", methods=["GET"])
def get_logs():
    """Return recent Algorand TestNet transactions"""
    try:
        status = client.status()
        last_round = status["last-round"]
        txns_out = []
        for rnd in range(last_round - 3, last_round):
            block = client.block_info(rnd)
            for tx in block.get("block", {}).get("txns", []):
                txns_out.append({
                    "round": rnd,
                    "txid": tx.get("tx", "N/A"),
                    "type": tx.get("txn", {}).get("type", "unknown"),
                    "sender": tx.get("txn", {}).get("snd", "N/A")
                })
        return jsonify({"round": last_round, "events": txns_out})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# === MAIN ENTRY POINT ===
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8502)