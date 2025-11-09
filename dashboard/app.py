# dashboard/app.py — AFREEGuard AI Premium Light Dashboard (with Logo in Header)

import os
import time
import json
import socket
from datetime import datetime

import requests
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from dotenv import load_dotenv
from PIL import Image
import base64

# ===== Load environment =====
load_dotenv()

# ===== Helper: Auto-detect backend URL =====
def get_backend_url() -> str:
    host = socket.gethostname()
    default_backend = f"https://{host}-8502.app.github.dev"
    return os.getenv("AFREEGUARD_API_URL", default_backend)

API_URL = get_backend_url()

# ===== Page Config =====
st.set_page_config(
    page_title="AFREEGuard AI – Monitoring Dashboard",
    page_icon="🛡️",
    layout="wide"
)

# ===== Utility: Encode logo to base64 for HTML embedding =====
def get_base64_image(image_path):
    if not os.path.exists(image_path):
        return None
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

logo_path = "dashboard/afreeguard_logo.png"
logo_base64 = get_base64_image(logo_path)

# ===== Premium CSS =====
def load_premium_css():
    st.markdown("""
        <style>
        [data-testid="stAppViewContainer"] {
            background-color: #FFFFFF;
            background-image: linear-gradient(180deg, #FFFFFF 0%, #F8FAFF 100%);
            color: #1A1A1A;
        }
        [data-testid="stSidebar"] {
            background: #F7F9FC;
            border-right: 1px solid #E0E0E0;
        }
        .afg-header {
            display: flex;
            align-items: center;
            gap: 20px;
            padding: 1.2rem 1.5rem;
            background: linear-gradient(90deg, #003366 0%, #0055AA 60%, #FFD700 100%);
            border-radius: 12px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.08);
        }
        .afg-header img {
            height: 60px;
            border-radius: 8px;
            background: #ffffff11;
            padding: 4px;
        }
        .afg-header-text {
            display: flex;
            flex-direction: column;
            justify-content: center;
        }
        .afg-header-text h1 {
            color: white;
            font-weight: 700;
            font-family: 'Montserrat', sans-serif;
            margin: 0;
            font-size: 1.8rem;
        }
        .afg-header-text p {
            color: #E6E6E6;
            font-size: 0.95rem;
            margin-top: 3px;
        }
        .metric-card {
            border-radius: 10px;
            background-color: #FFFFFF;
            border: 1px solid #E0E0E0;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
            padding: 10px;
        }
        .block-table {
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            overflow: hidden;
        }
        a {
            color: #003366 !important;
            text-decoration: none;
        }
        a:hover {
            color: #EAC349 !important;
            text-decoration: underline;
        }
        </style>
    """, unsafe_allow_html=True)

load_premium_css()

# ===== Sidebar =====
st.sidebar.markdown("### 🔗 Backend")
st.sidebar.write(f"`{API_URL}`")

st.sidebar.markdown("### ⚙️ Controls")
refresh_sec = st.sidebar.slider("Auto-refresh (seconds)", 2, 30, 5)

if st.sidebar.button("🧹 Reset Logs"):
    try:
        r = requests.post(f"{API_URL}/api/reset", timeout=10)
        if r.status_code == 200:
            msg = r.json().get("message", "Logs cleared successfully")
            st.sidebar.success(msg)
        else:
            st.sidebar.error(f"Reset failed: {r.status_code}")
    except Exception as e:
        st.sidebar.error(f"Error resetting logs: {e}")

# ===== Backend Check =====
status_placeholder = st.empty()

def check_backend():
    try:
        res = requests.get(f"{API_URL}/api/logs", timeout=5)
        if res.status_code == 200:
            status_placeholder.markdown(
                "<div style='text-align:right; color:#00C851; font-weight:bold;'>🟢 Backend Connected</div>",
                unsafe_allow_html=True
            )
        else:
            status_placeholder.markdown(
                f"<div style='text-align:right; color:#FFBB33; font-weight:bold;'>🟡 Status {res.status_code}</div>",
                unsafe_allow_html=True
            )
    except Exception:
        status_placeholder.markdown(
            "<div style='text-align:right; color:#FF4444; font-weight:bold;'>🔴 Backend not reachable</div>",
            unsafe_allow_html=True
        )

# ===== Fetch Logs =====
def fetch_events(limit: int = 2000):
    try:
        resp = requests.get(f"{API_URL}/api/logs", timeout=10)
        if resp.status_code != 200:
            st.warning(f"⚠️ API returned status {resp.status_code}")
            return []
        data = resp.json()
        return data.get("events", [])[-limit:]
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
    ts = row.get("ts") or row.get("timestamp") or ""
    if isinstance(ts, str):
        ts_str = ts.replace("T", " ").split(".")[0]
    else:
        ts_str = str(ts)
    return {
        "ts": ts_str,
        "action": row.get("action") or row.get("type", "unknown"),
        "blocked": is_blocked(row),
        "reason": row.get("reason", ""),
        "txid": row.get("txid", "N/A"),
        "params": row.get("params", {}),
    }

# ===== Main Dashboard =====
main_placeholder = st.empty()

while True:
    check_backend()
    raw_events = fetch_events()
    rows = [summarize_row(r) for r in raw_events]

    blocked_rows = [r for r in rows if r["blocked"]]
    allowed_rows = [r for r in rows if not r["blocked"]]
    total = len(rows)
    latest_hash = rows[-1]["txid"] if rows else "N/A"

    with main_placeholder.container():
        # === HEADER with logo ===
        if logo_base64:
            st.markdown(f"""
            <div class="afg-header">
                <img src="data:image/png;base64,{logo_base64}" alt="AFREEGuard Logo">
                <div class="afg-header-text">
                    <h1>AFREEGuard AI</h1>
                    <p>Real-time Blockchain Security Monitoring • Algorand TestNet</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="afg-header-text">
                <h1>AFREEGuard AI</h1>
                <p>Real-time Blockchain Security Monitoring • Algorand TestNet</p>
            </div>
            """, unsafe_allow_html=True)

        # === METRICS ===
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("✅ Allowed", len(allowed_rows))
        with c2:
            st.metric("🚫 Blocked", len(blocked_rows))
        with c3:
            st.metric("🔗 Total Events", total)
        with c4:
            short_hash = latest_hash[:10] + "..." if latest_hash != "N/A" else "N/A"
            st.metric("🧱 Latest Block", short_hash)

        st.markdown("---")

        # === CHART ===
        st.subheader("📊 Activity Overview")
        if total > 0:
            fig, ax = plt.subplots(figsize=(5, 2.5))
            labels = ["Allowed", "Blocked"]
            values = [len(allowed_rows), len(blocked_rows)]
            bar_colors = ["#0055AA", "#FFD700"]
            ax.bar(labels, values, color=bar_colors, edgecolor="#003366")
            ax.set_facecolor("#FFFFFF")
            fig.patch.set_facecolor("#FFFFFF")
            ax.tick_params(colors="#1A1A1A")
            ax.spines["bottom"].set_color("#E0E0E0")
            ax.spines["left"].set_color("#E0E0E0")
            ax.set_title("Events by Decision", color="#003366", fontsize=12, fontweight="bold")
            st.pyplot(fig)
            plt.close(fig)
        else:
            st.info("No blockchain events yet. Trigger a transaction to see activity.")

        # === TABLE ===
        st.subheader("🧱 Recent Events")
        if total > 0:
            df = pd.DataFrame(rows[::-1])
            df.rename(columns={
                "ts": "Time",
                "action": "Action",
                "blocked": "Blocked",
                "reason": "Reason",
                "txid": "Block Hash",
                "params": "Params"
            }, inplace=True)

            def fmt_hash(h):
                if not h or h == "N/A":
                    return "N/A"
                url = f"https://testnet.explorer.perawallet.app/tx/{h}"
                return f'<a href="{url}" target="_blank">{h[:12]}…</a>'

            df["Block Hash"] = df["Block Hash"].apply(fmt_hash)

            def highlight_row(row):
                return [
                    "background-color: #F6FFF6; color:#1A1A1A;" if not row["Blocked"]
                    else "background-color: #FFF0F0; color:#1A1A1A;"
                ] * len(row)

            styled = (
                df.style.apply(highlight_row, axis=1)
                .set_table_styles([
                    {"selector": "thead th", "props": [
                        ("background-color", "#F5F7FA"),
                        ("color", "#003366"),
                        ("font-weight", "600"),
                        ("border-bottom", "1px solid #E0E0E0")
                    ]},
                    {"selector": "tbody td", "props": [
                        ("border", "1px solid #E0E0E0"),
                        ("padding", "6px 8px")
                    ]}
                ])
            )

            st.markdown("<div class='block-table'>", unsafe_allow_html=True)
            st.markdown(styled.to_html(), unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("No blockchain logs yet.")

        # === FOOTER ===
        st.markdown("---")
        st.markdown("""
        <div style="text-align:center; color:#777777; font-size:0.8rem; padding:10px 0;">
            Powered by <span style="color:#FFD700;">AFREE Labs</span> | 
            Built on <span style="color:#0055AA;">Algorand TestNet</span> | 
            © 2025 WOW GLOBAL SOLUTIONS LTD. Member of Fintech Scotland, UK.<br>
            <a href="https://testnet.explorer.perawallet.app/" target="_blank">🔗 View on Algorand Pera Explorer</a>
        </div>
        """, unsafe_allow_html=True)

    # === REFRESH LOOP ===
    time.sleep(refresh_sec)
    st.rerun()