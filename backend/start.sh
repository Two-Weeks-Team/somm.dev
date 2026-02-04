#!/bin/bash

# Start script for somm.dev backend (Python 3.14)

echo "🚀 Starting Somm.dev Backend (Python 3.14)"
echo "================================"

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1)
echo "Python version: $PYTHON_VERSION"

# Check if we're in the backend directory
if [ ! -f "main.py" ]; then
    echo "❌ Error: main.py not found. Please run from backend directory."
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Start the server
echo "🌐 Starting FastAPI server..."
echo "API will be available at: http://localhost:8000"
echo "API docs: http://localhost:8000/docs"
echo ""
python main.py
