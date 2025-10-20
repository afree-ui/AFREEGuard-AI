# dashboard/app.py
import os
import streamlit as st
import requests
import json, time
from pathlib import Path
import matplotlib.pyplot as plt

from dotenv import load_dotenv
load_dotenv()

st.sidebar.write("🔍 API URL Loaded:", os.getenv("AFREEGUARD_API_URL"))

st.markdown("""
    <style>
    /* ===== Global AFREEGuard AI Theme ===== */
    body {
        background-color: #FFFFFF;
    }

    /* Buttons */
    div.stButton > button {
        background-color: #003366;
        color: white;
        border-radius: 6px;
        border: none;
        padding: 0.5em 1em;
        font-weight: bold;
    }
    div.stButton > button:hover {
        background-color: #FFD700;
        color: #003366;
    }

    /* Table headers */
    thead tr th {
        background-color: #003366 !important;
        color: white !important;
    }

    /* Summary counters */
    .css-1dp5vir, .css-12w0qpk {
        border: 2px solid #003366 !important;
        color: #FFD700 !important;
        font-weight: bold !important;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# Where the agent writes JSONL events
LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
LOG_PATH = LOG_DIR / "events.jsonl"
from PIL import Image


# Load logo
logo = Image.open("dashboard/afreeguard_logo.png")

# Create two columns for logo + title
col1, col2 = st.columns([1, 5])  # Adjust proportions if needed

with col1:
    st.image(logo, width=80)  # smaller logo on the left

with col2:
    st.markdown(
        "<h1 style='margin-bottom: 0px; color:#003366;'>AFREEGuard AI</h1>"
        "<h3 style='margin-top: 0px; color:#FFD700;'>Monitoring Dashboard</h3>",
        unsafe_allow_html=True
    )
# === Connection Status Indicator ===
base_url = os.getenv("AFREEGUARD_API_URL", "http://localhost:8502")
status_placeholder = st.empty()

import requests
import pandas as pd

st.markdown("### 🧠 Latest Blockchain Logs")

try:
    api_url = os.getenv("AFREEGUARD_API_URL", "http://localhost:8502")
    response = requests.get(f"{api_url}/api/logs")

    if response.status_code == 200:
        data = response.json().get("events", [])

        if data:
            df = pd.DataFrame(data)

            # Display summary cards
            #allowed = len(df[df["blocked"] == False])
            #blocked = len(df[df["blocked"] == True])
            #latest_tx = df.iloc[-1]["txid"] if not df.empty else "N/A"

            #c1, c2, c3 = st.columns(3)
            #c1.metric("✅ Allowed", allowed)
            #c2.metric("🚫 Blocked", blocked)
            #c3.metric("🔗 Latest Hash", latest_tx[:10] + "...")

            # Display logs table
            #st.dataframe(df[["ts", "action", "blocked", "reason", "txid"]])

        else:
            st.info("No blockchain logs yet.")
    else:
        st.error("Failed to fetch logs from backend.")
except Exception as e:
    st.error(f"Error: {e}")

def check_backend():
    try:
        res = requests.get(f"{base_url}/", timeout=5)
        if res.status_code == 200:
            status_placeholder.success("🟢 Backend Connected")
        else:
            status_placeholder.warning(f"🟡 Backend responded with {res.status_code}")
    except Exception:
        status_placeholder.error("🔴 Backend not reachable")

# Initial check
check_backend()
# ---------- Controls ----------
st.sidebar.markdown("### Controls")
refresh_sec = st.sidebar.slider("Auto-refresh (sec)", 1, 10, 3)

# Reset logs via backend API
# ✅ Reset logs via backend API (fixed)
if st.sidebar.button("🔄 Refresh Blockchain Logs", type="primary"):
    st.info("Fetching latest blockchain transactions...")
    time.sleep(1)
    st.rerun()
    try:
        api_url = os.getenv("AFREEGUARD_API_URL", "http://localhost:8502").strip("/")
        reset_url = f"{api_url}/api/reset"

        st.sidebar.write(f"🛰️ Sending POST to: {reset_url}")

        res = requests.post(reset_url)

        if res.status_code == 200:
            msg = res.json().get("message", "Logs cleared successfully!")
            st.success(f"✅ {msg}")
            time.sleep(1)
            st.rerun()
        else:
            st.warning(f"⚠️ Could not reset logs (status {res.status_code}) — {res.text}")
    except Exception as e:
        st.error(f"❌ Error resetting logs: {e}")

placeholder = st.empty()

def fetch_events(limit: int = 2000):
    """Fetch blockchain events from AFREEGuard AI backend API."""
    import os

    base_url = os.getenv("AFREEGUARD_API_URL", "http://localhost:8502")
    API_URL = f"{base_url}/api/logs"
    try:
        response = requests.get(API_URL, timeout=10)
        if response.status_code != 200:
            st.warning(f"⚠️ API returned status {response.status_code}")
            return []
        data = response.json()
        events = data.get("events", [])
        return events[-limit:]
    except json.JSONDecodeError:
        st.error("⚠️ API returned invalid JSON (maybe empty response).")
        return []
    except Exception as e:
        st.error(f"⚠️ Error fetching events: {e}")
        return []

def is_blocked(row: dict) -> bool:
    """Return True if event is blocked; handle old/new shapes."""
    # new schema
    if "blocked" in row:
        return bool(row.get("blocked"))
    # old schema with decision.allow
    try:
        return not bool(row["decision"]["allow"])
    except Exception:
        return False

def summarize_row(row: dict) -> dict:
    """Flatten for display including blockchain hash."""
    return {
        "ts": row.get("ts", "").replace("T", " ").split(".")[0],
        "action": row.get("action"),
        "blocked": is_blocked(row),
        "reason": row.get("reason"),
        "txid": row.get("txid", "N/A"),   # ✅ Add this line
        "params": row.get("params"),
    }

# ---------- Live loop ----------
while True:
    check_backend()  # verify backend is live
    rows = [summarize_row(r) for r in fetch_events()]
    blocked = [r for r in rows if r["blocked"]]
    allowed = [r for r in rows if not r["blocked"]]

    with placeholder.container():
        if rows:
            latest_hash = rows[-1].get("txid", "N/A")

            # ✅ Highlight latest block
            st.markdown(
                f"<div style='background-color:#003366; color:white; padding:8px; border-radius:6px;'>"
                f"🧱 <b>Latest Block Recorded:</b> "
                f"<a href='https://testnet.algoscan.app/tx/{latest_hash}' target='_blank' "
                f"style='color:#FFD700; text-decoration:none;'>{latest_hash}</a>"
                f"</div>",
                unsafe_allow_html=True
            )

            # === Real-time metrics refresh ===
            c1, c2, c3 = st.columns(3)
            c1.metric("✅ Allowed", len(allowed))
            c2.metric("🚫 Blocked", len(blocked))
            latest_hash = rows[-1].get("txid", "N/A")
            c3.metric("🔗 Latest Hash", latest_hash[:10] + "...")

            # ✅ Event Overview Chart
            fig, ax = plt.subplots(figsize=(4, 2))
            labels = ['Allowed', 'Blocked']
            values = [len(allowed), len(blocked)]
            colors = ['#ccffcc', '#ffcccc']
            ax.bar(labels, values, color=colors)
            ax.set_title("Event Overview")
            ax.set_ylabel("Count")
            st.pyplot(fig)
            plt.close(fig)

            # ✅ Recent Events Table
            import pandas as pd
            st.subheader("Recent Events")

            df = pd.DataFrame(rows[::-1])
            df.rename(columns={
                "ts": "Time",
                "action": "Action",
                "blocked": "Blocked",
                "reason": "Reason",
                "txid": "Block Hash",
                "params": "Params"
            }, inplace=True)

            df["Block Hash"] = df["Block Hash"].apply(
                lambda h: f"[{h}](https://testnet.algoscan.app/tx/{h})" if h != "N/A" else "N/A"
            )

            st.markdown("**Click the Block Hash to view on AlgoScan TestNet Explorer.**")

            def highlight_row(row):
                color = '#ccffcc' if not row['Blocked'] else '#ffcccc'
                return [f'background-color: {color}'] * len(row)

            styled_df = df.style.apply(highlight_row, axis=1)
            st.dataframe(styled_df, use_container_width=True)

        else:
            st.info("No blockchain logs yet.")

    # Wait before refreshing and re-run loop
    time.sleep(refresh_sec)
    st.rerun()