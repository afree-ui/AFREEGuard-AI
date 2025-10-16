# Guardrail PoC — Safe Autonomous AI Agents

Minimal scaffold for a 1–3 month Proof of Concept:
- Rule-based Guardrail Layer
- Adversarial Test Harness
- Monitoring Dashboard
- Integration with an open-weight agent framework (via LangChain)

## Quick Start

1) Create a virtualenv and install requirements:

   ```bash
   pip install -r requirements.txt
   ```

2) Run the **agent API** (FastAPI):

   ```bash
   uvicorn agent.agent:app --reload --port 8000
   ```

3) Run the **dashboard** (Streamlit) in another terminal:

   ```bash
   streamlit run dashboard/app.py
   ```

4) Run the **adversarial tests**:

   ```bash
   python tests/adversarial.py
   ```

## Structure
- `agent/agent.py` — simple LangChain-based agent exposed as an API.
- `guardrails/rules.py` — define policies/rules.
- `guardrails/engine.py` — guardrail middleware to approve/block actions.
- `executor/actions.py` — safe action executors (education/finance/web3).
- `dashboard/app.py` — Streamlit UI for logs/metrics.
- `tests/adversarial.py` — red-team prompts and fuzzing harness.
- `data/policies.yaml` — editable rules/policies.
- `logs/` — runtime JSONL logs (created on first run).

## Notes
- This PoC uses stubbed open-weight calls to keep it offline. Replace the
  model call with your preferred local/open-weight LLM wrapper.
- The goal is to demonstrate *architecture & safety flow*, not final UX.