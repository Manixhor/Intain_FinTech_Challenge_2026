#!/bin/bash
# ============================================
#  LoanVerify — Quick Start
#  Intain FinTech Challenge 2026
# ============================================

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║     LoanVerify — Starting Demo...        ║"
echo "╚══════════════════════════════════════════╝"
echo ""

# Get project root
PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"

# ── Step 1: Setup Backend ──────────────────────
echo "[1/4] Setting up backend..."
cd "$PROJECT_ROOT/backend"

if [ ! -d "venv" ]; then
    echo "  Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate
pip install -r requirements.txt -q 2>/dev/null
python seed.py 2>/dev/null
echo "  ✓ Backend ready"

# ── Step 2: Setup Frontend ─────────────────────
echo "[2/4] Setting up frontend..."
cd "$PROJECT_ROOT/frontend"

if [ ! -d "node_modules" ]; then
    echo "  Installing packages..."
    npm install --silent 2>/dev/null
fi
echo "  ✓ Frontend ready"

# ── Step 3: Start Backend ──────────────────────
echo "[3/4] Starting backend on port 8000..."
cd "$PROJECT_ROOT/backend"
source venv/bin/activate
uvicorn app.main:app --host 127.0.0.1 --port 8000 &
BACKEND_PID=$!
sleep 2

if curl -s http://127.0.0.1:8000/health > /dev/null 2>&1; then
    echo "  ✓ Backend running"
else
    echo "  ✗ Backend failed"
    exit 1
fi

# ── Step 4: Start Frontend ─────────────────────
echo "[4/4] Starting frontend on port 3000..."
cd "$PROJECT_ROOT/frontend"
npm run dev &
FRONTEND_PID=$!
sleep 3

echo ""
echo "╔══════════════════════════════════════════════╗"
echo "║  🚀 LoanVerify is ready!                     ║"
echo "║                                              ║"
echo "║  App:      http://localhost:3000              ║"
echo "║  API Docs: http://localhost:8000/docs         ║"
echo "║                                              ║"
echo "║  Demo Accounts (password: demo123):          ║"
echo "║    analyst  → Upload & view data             ║"
echo "║    reviewer → Resolve exceptions             ║"
echo "║    admin    → Full access                    ║"
echo "║                                              ║"
echo "║  Sample Data: backend/sample_data/           ║"
echo "║    clean_data.csv        (20 records, clean) ║"
echo "║    messy_bank_export.csv (35 records, messy) ║"
echo "║    critical_errors.csv   (20 records, bad)   ║"
echo "║    large_dataset.csv     (100 records)       ║"
echo "║                                              ║"
echo "║  Press Ctrl+C to stop                        ║"
echo "╚══════════════════════════════════════════════╝"
echo ""

# Open browser
if [[ "$OSTYPE" == "darwin"* ]]; then
    open http://localhost:3000
fi

# Cleanup
cleanup() {
    echo ""
    echo "Shutting down..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "Done."
    exit 0
}

trap cleanup SIGINT SIGTERM
wait
