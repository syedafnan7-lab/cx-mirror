#!/usr/bin/env bash
set -e

echo "================================================================"
echo "CX MIRROR — Linux/macOS Bootstrap & Launch Sequence"
echo "================================================================"

if [ ! -d "venv" ]; then
    echo "[1/4] Creating Python virtual environment..."
    python3 -m venv venv
fi

echo "[1/4] Activating venv..."
source venv/bin/activate

echo "[2/4] Installing Python requirements..."
pip install -r backend/requirements.txt
playwright install chromium

echo "[3/4] Installing Frontend dependencies..."
cd frontend
npm install
cd ..

echo "[4/4] Generating Golden Mockup Baseline..."
python scripts/generate_golden.py

echo "================================================================"
echo "Bootstrap Complete! Run: ./scripts/start_all.sh"
echo "================================================================"

