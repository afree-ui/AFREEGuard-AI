#!/bin/bash
# AFREEGuard AI test script
# Runs blocked + allowed case for NFT guardrail

API_URL="http://127.0.0.1:8000/query"

echo "=== Running AFREEGuard AI Guardrail Tests ==="

# 1. Blocked case (fake wallet)
echo ""
echo "--- Blocked Case (Fake Wallet) ---"
curl -s -X POST $API_URL \
  -H "Content-Type: application/json" \
  -d '{
    "domain": "web3",
    "user_input": "Execute governance vote",
    "action": "propose_vote",
    "params": {
      "wallet_address": "SOME_FAKE_WALLET",
      "proposal": "Change X"
    }
  }' | jq

# 2. Allowed case (real wallet)
echo ""
echo "--- Allowed Case (Your ParaWallet with NFT) ---"
curl -s -X POST $API_URL \
  -H "Content-Type: application/json" \
  -d "{
    \"domain\": \"web3\",
    \"user_input\": \"Execute governance vote\",
    \"action\": \"propose_vote\",
    \"params\": {
      \"wallet_address\": \"${PARA_ADDR}\",
      \"proposal\": \"Change X\"
    }
  }" | jq

echo ""
echo "=== Tests Finished ==="
