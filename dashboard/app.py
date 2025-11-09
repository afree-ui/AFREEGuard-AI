# dashboard/app.py
import os
import streamlit as st
import requests
import json, time
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
import socket
from dotenv import load_dotenv
from PIL import Image

# ===== Load environment =====
load_dotenv()

# ===== Helper: Auto-detect backend URL =====
# Detect Codespace URL or fallback to .env setting

def get_backend_url():
    host = socket.gethostname()
    # Auto-detect Codespace backend URL
    return f"https://{host}-8502.app.github.dev"

API_URL = os.getenv("AFREEGUARD_API_URL", get_backend_url())
st.sidebar.write(f"🔗 Connected API URL: {API_URL}")

# ===== Styling =====
st.markdown("""
<style>
body { background-color: #FFFFFF; }
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
thead tr th {
    background-color: #003366 !important;
    color: white !important;
}
.css-1dp5vir, .css-12w0qpk {
    border: 2px solid #003366 !important;
    color: #FFD700 !important;
    font-weight: bold !important;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# ===== Logo & Title =====
logo = Image.open("dashboard/afreeguard_logo.png")
col1, col2 = st.columns([1, 5])
with col1:
    st.image(logo, width=80)
with col2:
    st.markdown(
        "<h1 style='margin-bottom: 0px; color:#003366;'>AFREEGuard AI</h1>"
        "<h3 style='margin-top: 0px; color:#FFD700;'>Monitoring Dashboard</h3>",
        unsafe_allow_html=True
    )

# ===== Connection Status =====
status_placeholder = st.empty()

def check_backend():
    """Ping backend and update status indicator."""
    try:
        res = requests.get(f"{API_URL}/api/logs", timeout=5)
        if res.status_code == 200:
            status_placeholder.success("🟢 Backend Connected")
        else:
            status_placeholder.warning(f"🟡 Backend responded with {res.status_code}")
    except Exception:
        status_placeholder.error("🔴 Backend not reachable")

# ===== Controls =====
st.sidebar.markdown("### ⚙️ Controls")
refresh_sec = st.sidebar.slider("Auto-refresh (sec)", 1, 10, 3)

# ===== Reset Logs =====
if st.sidebar.button("🧹 Reset Logs", type="primary"):
    try:
        response = requests.post(f"{API_URL}/api/reset", timeout=10)
        if response.status_code == 200:
            msg = response.json().get("message", "Logs cleared successfully!")
            st.success(f"🧹 {msg}")
        else:
            st.error(f"Error resetting logs: {response.text}")
    except Exception as e:
        st.error(f"Error resetting logs: {e}")

# ===== Fetch Logs =====
def fetch_events(limit: int = 2000):
    try:
        response = requests.get(f"{API_URL}/api/logs", timeout=10)
        if response.status_code != 200:
            st.warning(f"⚠️ API returned status {response.status_code}")
            return []
        data = response.json()
        return data.get("events", [])[-limit:]
    except json.JSONDecodeError:
        st.error("⚠️ API returned invalid JSON.")
        return []
    except Exception as e:
        st.error(f"⚠️ Error fetching events: {e}")
        return []

# ===== Helpers =====
def is_blocked(row: dict) -> bool:
    if "blocked" in row:
        return bool(row.get("blocked"))
    try:
        return not bool(row["decision"]["allow"])
    except Exception:
        return False

def summarize_row(row: dict) -> dict:
    return {
        "ts": row.get("ts", "").replace("T", " ").split(".")[0],
        "action": row.get("action"),
        "blocked": is_blocked(row),
        "reason": row.get("reason"),
        "txid": row.get("txid", "N/A"),
        "params": row.get("params"),
    }

# ===== Main Dashboard Loop =====
placeholder = st.empty()

while True:
    check_backend()
    rows = [summarize_row(r) for r in fetch_events()]
    blocked = [r for r in rows if r["blocked"]]
    allowed = [r for r in rows if not r["blocked"]]

    with placeholder.container():
        if rows:
            latest_hash = rows[-1].get("txid", "N/A")
            st.markdown(
                f"<div style='background-color:#003366; color:white; padding:8px; border-radius:6px;'>"
                f"🧱 <b>Latest Block Recorded:</b> "
                f"<a href='https://testnet.algoscan.app/tx/{latest_hash}' target='_blank' "
                f"style='color:#FFD700; text-decoration:none;'>{latest_hash}</a>"
                f"</div>",
                unsafe_allow_html=True
            )

            # Metrics
            c1, c2, c3 = st.columns(3)
            c1.metric("✅ Allowed", len(allowed))
            c2.metric("🚫 Blocked", len(blocked))
            c3.metric("🔗 Latest Hash", latest_hash[:10] + "...")

            # Chart
            fig, ax = plt.subplots(figsize=(4, 2))
            ax.bar(["Allowed", "Blocked"], [len(allowed), len(blocked)], color=["#ccffcc", "#ffcccc"])
            ax.set_title("Event Overview")
            st.pyplot(fig)
            plt.close(fig)

            # Table
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
            def highlight_row(row):
                color = '#ccffcc' if not row['Blocked'] else '#ffcccc'
                return [f'background-color: {color}'] * len(row)
            st.dataframe(df.style.apply(highlight_row, axis=1), use_container_width=True)
        else:
            st.info("No blockchain logs yet.")

    time.sleep(refresh_sec)
    st.rerun()