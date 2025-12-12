# AFREEGuard AI — A Security & Governance Layer for Autonomous AI Agents

AFREEGuard AI is a **security, permissions, and audit framework for autonomous AI agents**.

It provides runtime guardrails that ensure AI agents operating in the real world — calling APIs, accessing data, executing transactions, or triggering workflows — do so **safely, transparently, and with accountability**.

This repository contains a **1–3 month Proof of Concept (PoC)** demonstrating the core architecture and safety flow behind AFREEGuard AI.

---

## 🎯 What This PoC Demonstrates

This PoC focuses on **architecture and control**, not production UX.

It includes:

- 🛡️ **Rule-based Guardrail Layer**  
  Runtime policies that approve, block, or flag AI agent actions.

- 🧪 **Adversarial Test Harness**  
  Red-team prompts and fuzzing to simulate unsafe, biased, or manipulated agent behavior.

- 📊 **Monitoring Dashboard**  
  Real-time visibility into agent decisions, risk flags, and blocked actions.

- 🔌 **Agent Integration**  
  A LangChain-based open-weight agent exposed via a FastAPI interface.

The goal is to show **how autonomous AI can be controlled at runtime**, not just evaluated after the fact.

---

## 🚨 Problem We Solve

Autonomous AI agents are increasingly capable of taking **real-world actions**, including:

- Executing transactions  
- Calling APIs  
- Accessing sensitive data  
- Triggering workflows  
- Interacting with other agents  

However, today’s AI systems typically operate with:

1. **No Identity**  
   → Agents cannot be uniquely identified, authenticated, or attributed.

2. **No Permission Boundaries**  
   → Agents can perform sensitive actions without explicit approval or limits.

3. **No Runtime Monitoring**  
   → Unsafe behavior, bias, manipulation, or intent drift goes undetected after deployment.

4. **No Accountability or Auditability**  
   → Actions are often untraceable and unverifiable.

5. **No Built-in Compliance**  
   → Existing AI tooling is not designed for autonomous agents operating under regulatory frameworks  
   (GDPR, EU AI Act, financial compliance).

This creates significant risk for **fintech, enterprises, public services, and society**.

**AFREEGuard AI exists to make autonomous AI agents safe, controllable, and accountable by default.**

---

## ⚖️ Ethics by Design (Operational, Not Declarative)

AFREEGuard treats ethics as an **enforceable runtime property**, not a post-hoc guideline.

Ethical risk emerges when autonomous systems can act without boundaries, oversight, or accountability.  
AFREEGuard operationalizes ethics through technical controls:

- Explicit permission boundaries  
- Human-in-the-loop approvals for high-impact actions  
- Transparent decision logging with reasons  
- Clear attribution of actions to identifiable agents  
- Auditable records for oversight and review  

AFREEGuard does not impose a single moral framework.  
Instead, it enables organizations to **encode their own ethical policies** while keeping humans in control.

---

## 🔗 Blockchain-Agnostic by Design

AFREEGuard AI is **blockchain-agnostic**.

The core security, permissions, and monitoring logic operates **off-chain** and can be deployed in:

- Enterprise environments  
- Regulated or sovereign systems  
- Cloud, VPC, or on-prem deployments  

When immutable, third-party-verifiable audit trails are required, AFREEGuard can optionally anchor events to:

- Algorand  
- Ethereum / EVM chains  
- Cosmos-based chains  
- Hyperledger / private ledgers  
- Traditional off-chain audit systems  

Blockchain integration is **optional**, not a dependency.

---

### Why Algorand Was Used in This PoC

Algorand was selected **solely for the Proof of Concept** because it offers:

- Fast finality and low latency  
- Low transaction costs  
- Strong security guarantees  
- Energy-efficient design  

This made it suitable for rapidly prototyping **immutable audit logging** without imposing blockchain lock-in on the AFREEGuard architecture.

---

## 🧱 PoC Architecture (Simplified)

1. **Agent Input**  
   → User or system triggers an agent action.

2. **Guardrail Engine**  
   → Policies evaluate the action and determine whether to approve, block, or flag it.

3. **Audit Layer (Optional)**  
   → Critical decisions are logged and optionally anchored to a blockchain.

4. **Agent Output**  
   → Safe response plus a traceable decision record.

---

## ⚡ Quick Start

### 1) Install dependencies
```bash
pip install -r requirements.txt

2) Run the agent API (FastAPI)

uvicorn agent.agent:app --reload --port 8000

3) Run the monitoring dashboard (Streamlit)

streamlit run dashboard/app.py

4) Run adversarial tests

python tests/adversarial.py


⸻

📁 Project Structure
	•	agent/agent.py — LangChain-based agent exposed as an API
	•	guardrails/rules.py — Policy and rule definitions
	•	guardrails/engine.py — Guardrail middleware (approve / block logic)
	•	executor/actions.py — Safe action executors
	•	dashboard/app.py — Streamlit monitoring UI
	•	tests/adversarial.py — Red-team prompts and fuzzing harness
	•	data/policies.yaml — Editable policy configuration
	•	logs/ — Runtime JSONL logs (created on first run)

⸻

🧠 Notes
	•	This PoC uses stubbed open-weight model calls to remain offline and reproducible.
	•	Replace the model call with your preferred local or open-weight LLM wrapper.
	•	The emphasis is on runtime safety flow, not final product UX.

⸻

🗺️ Roadmap (High Level)
	•	PoC (current)
Core guardrails, monitoring, and audit flow
	•	V1
Agent identity, permissions engine, structured audit service
	•	V2
Behavioral monitoring, anomaly detection, enterprise deployment options
	•	V3
Multi-agent governance, cross-system trust, optional on-chain registries

⸻

👤 Maintainer

Armand Byamha
Founder & Architect — AFREEGuard AI
AFREE Labs / WOW GLOBAL SOLUTIONS LTD (Scotland)

⸻

🤝 Contributing

Contributions are welcome.
Please open an issue to discuss ideas or submit a pull request.

⸻

📜 License

MIT License — free to use, fork, and contribute.

⸻

✨ AFREEGuard AI is built to ensure autonomous AI systems act safely, transparently, and under human-defined rules.

---

