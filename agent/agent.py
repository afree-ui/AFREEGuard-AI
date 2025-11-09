# agent/agent.py
from datetime import datetime
from pathlib import Path
import json
from typing import Optional, Dict, Any

from fastapi import FastAPI
from pydantic import BaseModel
from algosdk.encoding import is_valid_address

# IMPORTANT: import the MODULE (tests can monkeypatch this)
from blockchain import nft_access

app = FastAPI()

# ---- logging to newline-delimited JSON (.jsonl) ----
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True, parents=True)
EVENTS_FILE = LOG_DIR / "events.jsonl"  # dashboard reads this

def log_event(*, domain: str, action: str, blocked: bool,
              reason: Optional[str], params: Dict[str, Any] | None):
    evt = {
        "ts": datetime.utcnow().isoformat() + "Z",
        "domain": domain,
        "action": action,
        "blocked": blocked,
        "reason": reason,
        "params": params or {},
    }
    with EVENTS_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(evt) + "\n")


# ---- request model ----
class Query(BaseModel):
    domain: Optional[str] = None
    user_input: Optional[str] = None
    action: Optional[str] = None
    params: Optional[Dict[str, Any]] = None


@app.post("/query")
def query(q: Query):
    """
    Guardrail policy:
      1) Block all finance 'give_advice'.
      2) For web3 'propose_vote', require the provided wallet_address holds the configured NFT ASA.
         - ASA id comes from env ALGO_NFT_ASA_ID (see nft_access.env_asa_id()).
         - Any wallet that holds the ASA is allowed.
    """
    domain = (q.domain or "").lower()
    action = (q.action or "").lower()
    params = q.params or {}

    # 1) Block financial advice
    if domain == "finance" and action == "give_advice":
        log_event(domain=domain, action=action, blocked=True,
                  reason="Financial advice is blocked", params=params)
        return {"ok": True, "blocked": True, "reason": "Financial advice is blocked"}

    # 2) NFT membership check for web3 propose_vote
    if domain == "web3" and action == "propose_vote":
        # helper to sanitize pasted addresses
        def _clean_addr(s: str | None) -> str | None:
            if not s:
                return None
            # remove spaces/newlines/zero-width junk from copy-paste
            s = "".join(s.split())
            return s

        user_address = _clean_addr(params.get("wallet_address") or params.get("address"))
        if not user_address:
            log_event(domain=domain, action=action, blocked=True,
                      reason="wallet_address required", params=params)
            return {"ok": True, "blocked": True, "reason": "wallet_address required"}

        # validate bech32
        if not is_valid_address(user_address):
            log_event(domain=domain, action=action, blocked=True,
                      reason="invalid wallet address", params=params)
            return {"ok": True, "blocked": True, "reason": "invalid wallet address"}

        # resolve ASA id (env or default)
        asa_id = nft_access.env_asa_id() or nft_access.DEFAULT_ASA_ID

        # check membership
        try:
            has_nft = nft_access.holds_asa(user_address, asa_id)
        except Exception:
            # any RPC/IDX error → fail safe (block) and log
            log_event(domain=domain, action=action, blocked=True,
                      reason="membership check failed", params=params)
            return {"ok": True, "blocked": True, "reason": "membership check failed"}

        if not has_nft:
            log_event(domain=domain, action=action, blocked=True,
                      reason="NFT membership required", params=params)
            return {"ok": True, "blocked": True, "reason": "NFT membership required"}

        # Allowed
        result = {"action": q.action, "params": params}
        log_event(domain=domain, action=action, blocked=False,
                  reason="Allowed by NFT membership", params=params)
        return {"ok": True, "blocked": False, "result": result}

    # default pass-through
    result = {"action": q.action, "params": params}
    log_event(domain=domain, action=action, blocked=False,
              reason=None, params=params)
    return {"ok": True, "blocked": False, "result": result}

@app.get("/")
def root():
    """Root health endpoint for Render and Streamlit."""
    return {"status": "ok", "message": "AFREEGuard AI Backend is running"}
