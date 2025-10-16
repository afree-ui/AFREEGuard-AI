from typing import Dict, Any
import time, json, os
from .rules import RuleSet

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_PATH = os.path.join(LOG_DIR, "events.jsonl")

class GuardrailEngine:
    def __init__(self, rules: RuleSet):
        self.rules = rules

    def check(self, domain: str, user_input: str, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        decision = {"allow": True, "reason": "ok"}
        hits = self.rules.violates_keywords(user_input + " " + action + " " + json.dumps(params))
        if hits:
            decision = {"allow": False, "reason": f"blocked_keywords:{hits}"}

        policy = self.rules.domain_policy(domain)
        if domain == "finance" and policy.get("allow_advice") is False:
            if action == "give_advice":
                decision = {"allow": False, "reason": "finance_advice_disallowed"}

        if domain == "web3":
            safe = set(policy.get("safe_actions", []))
            blocked = set(policy.get("blocked_actions", []))
            if action in blocked or (safe and action not in safe):
                decision = {"allow": False, "reason": "web3_action_not_permitted"}

        self._log_event(domain, user_input, action, params, decision)
        return decision

    def _log_event(self, domain, user_input, action, params, decision):
        rec = {
            "ts": time.time(),
            "domain": domain,
            "user_input": user_input,
            "action": action,
            "params": params,
            "decision": decision
        }
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec) + "\n")