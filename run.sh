#!/bin/bash
# =========================================
# AFREEGuard AI Launcher Script
# =========================================

echo "🔁 Stopping any existing Python processes..."
sudo pkill -f python || true

echo "🚀 Starting AFREEGuard backend (Flask)..."
nohup python3 server.py > backend.log 2>&1 &

sleep 5  # wait for backend to start

echo "🌍 Checking Flask port..."
if ! sudo lsof -i:8502 > /dev/null; then
    echo "❌ Flask did not start properly on port 8502."
    exit 1
fi
echo "✅ Flask backend running on port 8502."

echo "💻 Starting Streamlit frontend..."
nohup python3 -m streamlit run dashboard/app.py > streamlit.log 2>&1 &

echo "✅ Streamlit dashboard starting on port 8501."
echo ""
echo "🎯 All systems running! Access AFREEGuard AI at:"
echo "   http://127.0.0.1:8501 (local preview)"
echo "   https://<your-codespace-name>-8501.app.github.dev (public URL)"