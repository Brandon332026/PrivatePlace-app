#!/bin/bash

# Adult Classified Ads Platform - Start Script

# Get the directory where the script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

# Use APP_PORT environment variable or default to 3000
PORT=${APP_PORT:-3000}

echo "Starting Adult Classifieds Platform on port $PORT..."

# Kill any existing process on the port
lsof -ti:$PORT | xargs kill -9 2>/dev/null || true

# Start Streamlit with uv
uv run streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
