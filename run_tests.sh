#!/bin/bash
# AFREEGuard AI test script
# Runs blocked + allowed case for NFT guardrail

API_URL="http://127.0.0.1:8000/query"

echo "=== Running AFREEGuard AI Guardrail Tests ==="

# 1. Blocked case (fake wallet)
echo ""
echo "--- Blocked Case (Fake Wallet) ---"
curl -s -X POST http://127.0.0.1:8000/query \
  -H "Content-Type: application/json" \
  -d "{
        \"domain\": \"web3\",
        \"user_input\": \"Execute governance vote\",
        \"action\": \"propose_vote\",
        \"params\": {
          \"wallet_address\": \"${PARA_ADDR}\",
          \"proposal\": \"Change parameter X\"
        }
      }" | jq

# 2. Allowed case (real wallet)
echo ""
echo "--- Allowed Case (Your ParaWallet with NFT) ---"
jq -n --arg w "$ALGO_TEST_WALLET" \
  '{domain:"web3",
    user_input:"Execute governance vote",
    action:"propose_vote",
    params:{wallet_address:$w},
    proposal:"Change X"}' \
| curl -s -X POST http://127.0.0.1:8000/query \
    -H 'Content-Type: application/json' \
    -d @- | jq

echo ""
echo "=== Tests Finished ==="
