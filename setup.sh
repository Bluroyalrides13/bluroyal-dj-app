#!/bin/bash
# Quick start script for Blu Royal Rides Agent

set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║     Luxury Ride Share Agent - Quick Start Setup            ║"
echo "╚════════════════════════════════════════════════════════════╝"

# Check Python version
echo ""
echo "📋 Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python $python_version"

# Create virtual environment
echo ""
echo "🔧 Setting up virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
source venv/bin/activate
echo "✓ Virtual environment activated"

# Upgrade pip
echo ""
echo "📦 Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1
echo "✓ pip upgraded"

# Install dependencies
echo ""
echo "📥 Installing dependencies..."
pip install -r requirements.txt > /dev/null 2>&1
echo "✓ Dependencies installed"

# Create .env file
echo ""
echo "⚙️  Setting up configuration..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✓ .env file created from template"
    echo ""
    echo "⚠️  Please edit .env with your API keys:"
    echo "   - ANTHROPIC_API_KEY"
    echo "   - SQUARE_ACCESS_TOKEN"
    echo "   - WIX_API_KEY"
else
    echo "✓ .env file already exists"
fi

# Create database
echo ""
echo "🗄️  Initializing database..."
python3 -c "from src.models.database import DatabaseManager; DatabaseManager()" > /dev/null 2>&1
echo "✓ Database initialized"

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                    Setup Complete! ✓                       ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "Next steps:"
echo "1. Edit .env with your API keys"
echo "2. Run the server: python -m src.main"
echo "3. Visit http://localhost:8000/docs for API documentation"
echo ""
