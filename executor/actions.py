from typing import Dict, Any

def tutor_answer(params: Dict[str, Any]) -> str:
    topic = params.get("topic", "general")
    return f"Here is a helpful explanation about {topic} suitable for a student."

def finance_information(params: Dict[str, Any]) -> str:
    query = params.get("query", "")
    return ("This is general financial information, not advice. "
            "Key factors to research include fees, risk tolerance, and diversification.")

def web3_propose_vote(params: Dict[str, Any]) -> str:
    proposal = params.get("proposal", "N/A")
    return f"Drafted a governance proposal summary: {proposal[:160]}"