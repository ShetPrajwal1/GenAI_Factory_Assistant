#!/usr/bin/env bash
# run.sh - Helper script to launch both the FastAPI backend and Streamlit frontend

# Ensure we are in the venv environment
source venv/bin/activate

# Create data dir if it doesn't exist
mkdir -p data/temp

echo "========================================="
echo "Starting FastAPI Backend on port 8000..."
echo "========================================="
# Check if uvicorn is actually installed/available
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 & 
BACKEND_PID=$!

sleep 3

echo "========================================="
echo "Starting Streamlit Dashboard on port 8501..."
echo "========================================="
python -m streamlit run frontend/app.py &
FRONTEND_PID=$!

# Handle shutdown gracefully
trap "echo 'Shutting down services...'; kill $BACKEND_PID; kill $FRONTEND_PID; exit" SIGINT SIGTERM EXIT

# Wait for both background processes
wait
