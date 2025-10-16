from typing import Dict, Any, List
import re

class RuleSet:
    def __init__(self, cfg: Dict[str, Any]):
        self.cfg = cfg
        # load global blocked keywords
        self.blocked = set(cfg.get("global", {}).get("blocked_keywords", []))

    def violates_keywords(self, text: str) -> List[str]:
        text_l = text.lower()
        hits = [k for k in self.blocked if k in text_l]
        return hits

    def domain_policy(self, domain: str) -> Dict[str, Any]:
        return self.cfg.get("domains", {}).get(domain, {})

    def check(self, domain: str, action: str, params: Dict[str, Any], user_input: str):
        """
        Returns (allow: bool, reason: str)
        """

        # --- Global keyword block ---
        hits = self.violates_keywords(user_input)
        if hits:
            return False, f"global_blocked_keywords: {hits}"

        policy = self.domain_policy(domain)

        # --- Finance rules ---
        if domain == "finance":
            if policy.get("block_advice", True) and action == "give_advice":
                return False, "finance_advice_blocked"

            allowed_topics = set(policy.get("allowed_info_topics", []))
            if action == "give_information" and allowed_topics:
                topic = (params or {}).get("query", "").lower()
                if topic and not any(a in topic for a in allowed_topics):
                    return False, "finance_topic_not_whitelisted"

        # --- Web3 rules ---
        if domain == "web3":
            if policy.get("block_execute", True) and action == "execute_transaction":
                return False, "web3_execute_blocked"

        # --- Education rules ---
        if domain == "education":
            blocked_terms = set(policy.get("blocked_terms", []))
            if any(term in user_input.lower() for term in blocked_terms):
                return False, "education_blocked_content"

        return True, "ok"
