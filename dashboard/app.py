# dashboard/app.py
import streamlit as st
import json, os, time
from pathlib import Path

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

# ---------- Controls ----------
st.sidebar.markdown("### Controls")
refresh_sec = st.sidebar.slider("Auto-refresh (sec)", 1, 10, 3)

# Reset logs
if st.sidebar.button("Reset logs", type="primary"):
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    with open(LOG_PATH, "w", encoding="utf-8") as f:
        pass
    st.success("Logs cleared.")
    st.rerun()

placeholder = st.empty()

def load_logs(limit: int = 2000):
    """Read last events from JSONL file; tolerate mixed/old schemas."""
    if not LOG_PATH.exists():
        return []
    rows = []
    with open(LOG_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except Exception:
                # skip corrupt line
                continue
    return rows[-limit:]

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
    """Flatten for display."""
    return {
        "ts": row.get("ts"),
        "domain": row.get("domain"),
        "action": row.get("action"),
        "blocked": is_blocked(row),
        "reason": row.get("reason"),
        "params": row.get("params"),
    }

# ---------- Live loop ----------
while True:
    rows = [summarize_row(r) for r in load_logs()]

    blocked = [r for r in rows if r["blocked"]]
    allowed = [r for r in rows if not r["blocked"]]

    with placeholder.container():
        st.subheader("Summary")
        c1, c2 = st.columns(2)
        c1.metric("Allowed actions", len(allowed))
        c2.metric("Blocked actions", len(blocked))

        st.subheader("Recent Events")
        if rows:
            # newest first
            st.dataframe(rows[::-1], width="stretch") # avoids the deprecated use_container_width
        else:
            st.write("empty")

    time.sleep(refresh_sec)
