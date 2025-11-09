import json, os, time, random
from datetime import datetime

LOGS_DIR = "logs"
EVENTS_FILE = os.path.join(LOGS_DIR, "events.json")

os.makedirs(LOGS_DIR, exist_ok=True)

actions = ["ALLOW", "BLOCK"]
reasons = [
    "Valid transaction",
    "Suspicious pattern detected",
    "High gas usage",
    "Duplicate nonce",
    "Smart contract anomaly"
]

print("🧠 AFREEGuard AI Logger running... generating simulated blockchain events every 5 seconds.")

while True:
    event = {
        "timestamp": datetime.utcnow().isoformat(),
        "action": random.choice(actions),
        "blocked": random.choice([True, False]),
        "reason": random.choice(reasons),
        "block_hash": f"BLOCK-{random.randint(100000, 999999)}",
        "params": {"txid": f"TX-{random.randint(1000,9999)}"}
    }

    # Write event to events.json
    with open(EVENTS_FILE, "a") as f:
        f.write(json.dumps(event) + "\n")

    print(f"✅ Logged: {event['action']} | {event['reason']}")

    time.sleep(5)