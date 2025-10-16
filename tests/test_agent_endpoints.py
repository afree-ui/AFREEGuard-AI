# tests/test_agent_endpoints.py
import blockchain.nft_access as nft_access  # we will monkeypatch this

def test_tutor_answer_allowed(client):
    payload = {
        "domain": "education",
        "user_input": "Explain photosynthesis in one sentence.",
        "action": "tutor_answer",
        "params": {}
    }
    r = client.post("/query", json=payload)
    data = r.json()
    assert r.status_code == 200
    assert data["ok"] is True
    assert data["blocked"] is False
    assert "result" in data

def test_finance_advice_blocked(client):
    payload = {
        "domain": "finance",
        "user_input": "which crypto should I buy today?",
        "action": "give_advice",
        "params": {"query": "which coin?"}
    }
    r = client.post("/query", json=payload)
    data = r.json()
    assert r.status_code == 200
    assert data["ok"] is True
    assert data["blocked"] is True
    assert "reason" in data

def test_web3_vote_requires_nft_denied(client, monkeypatch):
    # Pretend wallet does NOT hold the NFT
    monkeypatch.setattr(nft_access, "holds_asa", lambda address, asa_id=None: False)

    payload = {
        "domain": "web3",
        "user_input": "Execute governance vote",
        "action": "propose_vote",
        "params": {
            "wallet_address": "SONYLXSLS4WV6DW4YGILBQBLIFH74CJAXMFXK5CZVXCQGO6LQK7GCRWJAY",
            "proposal": "Change parameter X"
        }
    }
    r = client.post("/query", json=payload)
    data = r.json()
    assert r.status_code == 200
    assert data["ok"] is True
    assert data["blocked"] is True
    assert "NFT membership required" in (data.get("reason") or "")

def test_web3_vote_allowed_with_nft(client, monkeypatch):
    # Pretend wallet DOES hold the NFT
    monkeypatch.setattr(nft_access, "holds_asa", lambda address, asa_id=None: True)

    payload = {
        "domain": "web3",
        "user_input": "Execute governance vote",
        "action": "propose_vote",
        "params": {
            "wallet_address": "SONYLXSLS4WV6DW4YGILBQBLIFH74CJAXMFXK5CZVXCQGO6LQK7GCRWJAY",
            "proposal": "Change parameter X"
        }
    }
    r = client.post("/query", json=payload)
    data = r.json()
    assert r.status_code == 200
    assert data["ok"] is True
    assert data["blocked"] is False
    assert "result" in data
