#!/bin/bash
# Setup script for arXiv Daily Paper Reader Skill

echo "🔧 Setting up arXiv Daily Paper Reader Skill..."

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ uv is not installed. Please install uv first:"
    echo "   curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

echo "✅ uv found"

# Install dependencies
echo "📦 Installing dependencies..."
uv sync

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Make scripts executable
echo "🔐 Making scripts executable..."
chmod +x arxiv_cli.py

echo "✅ Setup complete!"
echo ""
echo "Usage:"
echo "  uv run arxiv_cli.py                    # Default usage"
echo "  uv run arxiv_cli.py --help            # Show options"
echo "  uv run arxiv_cli.py --count 5         # Get 5 papers per category"
echo "  uv run arxiv_cli.py --preview-only    # Preview without saving"