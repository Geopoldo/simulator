#!/usr/bin/env bash
# Script to start both backend (FastAPI) and frontend (Vite) for TULIAN project

# Get the absolute path of the directory containing this script
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# --- Backend setup ---
echo "🚀 Setting up Backend..."
cd "$PROJECT_ROOT/backend"

# Create virtual environment if not exists
if [ ! -d "venv" ]; then
  python3 -m venv venv
fi
source venv/bin/activate

# Install Python dependencies
# Added: python-multipart (required for upload), faker, pandas, openpyxl
echo "📦 Installing backend dependencies..."
if [ -f "requirements.txt" ]; then
  pip install --upgrade pip && pip install -r requirements.txt
else
  pip install --upgrade pip && pip install fastapi uvicorn pydantic pandas openpyxl faker python-multipart
fi

# Run FastAPI server in background
echo "Starting Backend Server..."
uvicorn main:app --host 0.0.0.0 --port 9005 --reload &
BACKEND_PID=$!

echo "✅ Backend started (PID $BACKEND_PID) on http://localhost:9005"

# --- Frontend setup ---
echo "🚀 Setting up Frontend..."
cd "$PROJECT_ROOT/frontend"

# Install Node dependencies
echo "📦 Installing frontend dependencies..."
# Use --legacy-peer-deps to avoid React 19 vs libraries conflict
npm install --legacy-peer-deps

# Run Vite dev server in background
echo "Starting Frontend Server..."
npm run dev &
FRONTEND_PID=$!

echo "✅ Frontend started (PID $FRONTEND_PID). Open http://localhost:5173 in a browser."

# Wait for either process to exit (Ctrl+C will kill both)
wait -n
kill $BACKEND_PID $FRONTEND_PID
