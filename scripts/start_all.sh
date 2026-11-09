#!/usr/bin/env bash
# CX MIRROR — Start All Services

trap 'kill $(jobs -p)' EXIT

echo "[*] Starting CX Mirror Backend on http://127.0.0.1:8000..."
./venv/bin/uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 &

echo "[*] Starting CX Mirror Frontend on http://127.0.0.1:5173..."
cd frontend && npm run dev -- --host 127.0.0.1 --port 5173 &

wait

