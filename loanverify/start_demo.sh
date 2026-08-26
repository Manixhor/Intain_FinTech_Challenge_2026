#!/bin/bash
# ============================================
#  LoanVerify — Demo Launcher
#  Intain FinTech Challenge 2026
# ============================================

set -e

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║     LoanVerify — Demo Launcher           ║"
echo "║     Intain FinTech Challenge 2026        ║"
echo "╚══════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# ── Step 1: Backend Setup ──────────────────────
echo -e "${YELLOW}[1/4] Setting up backend...${NC}"

cd "$(dirname "$0")/backend"

# Create venv if needed
if [ ! -d "venv" ]; then
    echo "  Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate

# Install dependencies
echo "  Installing Python dependencies..."
pip install -r requirements.txt -q 2>/dev/null

# Seed demo users
echo "  Seeding demo users..."
python seed.py 2>/dev/null

echo -e "  ${GREEN}✓ Backend ready${NC}"

# ── Step 2: Frontend Setup ─────────────────────
echo -e "${YELLOW}[2/4] Setting up frontend...${NC}"

cd "$(dirname "$0")/frontend"

if [ ! -d "node_modules" ]; then
    echo "  Installing npm packages..."
    npm install --silent 2>/dev/null
fi

echo -e "  ${GREEN}✓ Frontend ready${NC}"

# ── Step 3: Start Backend ──────────────────────
echo -e "${YELLOW}[3/4] Starting backend server (port 8000)...${NC}"

cd "$(dirname "$0")/backend"
source venv/bin/activate
uvicorn app.main:app --host 127.0.0.1 --port 8000 &
BACKEND_PID=$!
sleep 2

# Verify backend
if curl -s http://127.0.0.1:8000/health > /dev/null 2>&1; then
    echo -e "  ${GREEN}✓ Backend running at http://localhost:8000${NC}"
    echo -e "  ${GREEN}  API docs at http://localhost:8000/docs${NC}"
else
    echo -e "  ${RED}✗ Backend failed to start${NC}"
    exit 1
fi

# ── Step 4: Start Frontend ─────────────────────
echo -e "${YELLOW}[4/4] Starting frontend server (port 3000)...${NC}"

cd "$(dirname "$0")/frontend"
npm run dev &
FRONTEND_PID=$!
sleep 3

echo -e "  ${GREEN}✓ Frontend running at http://localhost:3000${NC}"

# ── Open Browser ───────────────────────────────
echo ""
echo "╔══════════════════════════════════════════╗"
echo "║  🚀 Demo is ready!                       ║"
echo "║                                          ║"
echo "║  App:      http://localhost:3000          ║"
echo "║  API Docs: http://localhost:8000/docs     ║"
echo "║                                          ║"
echo "║  Demo accounts (password: demo123):      ║"
echo "║    analyst  — Upload & view data         ║"
echo "║    reviewer — Resolve exceptions         ║"
echo "║    admin    — Full access                ║"
echo "║                                          ║"
echo "║  Sample data: backend/sample_data/       ║"
echo "║                                          ║"
echo "║  Press Ctrl+C to stop all servers        ║"
echo "╚══════════════════════════════════════════╝"
echo ""

# Open browser (macOS)
if [[ "$OSTYPE" == "darwin"* ]]; then
    open http://localhost:3000
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    xdg-open http://localhost:3000 2>/dev/null || true
fi

# ── Cleanup on exit ────────────────────────────
cleanup() {
    echo ""
    echo "Shutting down servers..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "Done."
    exit 0
}

trap cleanup SIGINT SIGTERM

# Wait for Ctrl+C
wait
