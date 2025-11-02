#!/bin/bash

# Setup script for LLM Hallucination Research Project
# Run this after cloning/creating the project

echo "=========================================="
echo "LLM Hallucination Research - Setup"
echo "=========================================="
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version

if [ $? -ne 0 ]; then
    echo "❌ Python 3 not found. Please install Python 3.6 or higher."
    exit 1
fi

echo "✓ Python 3 found"
echo ""

# Create virtual environment
echo "Creating virtual environment..."
if [ -d "venv" ]; then
    echo "⚠ Virtual environment already exists. Skipping..."
else
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"
echo ""

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip
echo ""

# Install dependencies
echo "Installing dependencies..."
echo "This may take 5-10 minutes..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "⚠ Some packages failed to install. Trying essential packages only..."
    pip install numpy pandas google-generativeai groq matplotlib
fi

echo "✓ Dependencies installed"
echo ""

# Create necessary directories
echo "Creating directories..."
mkdir -p data/raw
mkdir -p data/processed
mkdir -p data/benchmarks
mkdir -p data/results
mkdir -p results/factual_qa
mkdir -p results/model_comparison
mkdir -p results/mitigation
mkdir -p results/plots
mkdir -p notebooks
mkdir -p tests

echo "✓ Directories created"
echo ""

# Copy config template
echo "Setting up configuration..."
if [ -f "configs/api_keys.json" ]; then
    echo "⚠ API keys config already exists. Skipping..."
else
    cp configs/api_keys.example.json configs/api_keys.json
    echo "✓ Created configs/api_keys.json"
    echo "⚠ IMPORTANT: Edit configs/api_keys.json with your API keys!"
fi
echo ""

# Create .gitignore
echo "Creating .gitignore..."
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/

# API Keys (NEVER COMMIT!)
configs/api_keys.json

# Results and data
results/
data/results/
*.csv
*.json
!configs/*.example.json

# Notebooks
.ipynb_checkpoints/

# LaTeX
paper/*.aux
paper/*.log
paper/*.pdf
paper/*.out
paper/*.bbl
paper/*.blg
paper/*.synctex.gz

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db
EOF

echo "✓ .gitignore created"
echo ""

# Create empty __init__.py files
echo "Creating package structure..."
touch src/__init__.py
touch src/models/__init__.py
touch src/detection/__init__.py
touch src/evaluation/__init__.py
touch src/mitigation/__init__.py
touch src/utils/__init__.py
touch experiments/__init__.py
touch experiments/factual_qa/__init__.py
touch experiments/reasoning/__init__.py
touch experiments/math/__init__.py

echo "✓ Package structure created"
echo ""

# Test setup
echo "Testing setup..."
python3 -c "import sys; print(f'Python version: {sys.version}')"
python3 -c "import numpy; print(f'NumPy version: {numpy.__version__}')"
python3 -c "import pandas; print(f'Pandas version: {pandas.__version__}')"

echo ""
echo "=========================================="
echo "✅ Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Get API keys:"
echo "   - Gemini: https://makersuite.google.com/app/apikey"
echo "   - Groq: https://console.groq.com/"
echo ""
echo "2. Edit configs/api_keys.json with your keys"
echo ""
echo "3. Test your setup:"
echo "   python src/models/llm_wrapper.py"
echo ""
echo "4. Run your first experiment:"
echo "   python experiments/factual_qa/run_factual_test.py --model gemini"
echo ""
echo "5. Read QUICKSTART.md for detailed instructions"
echo ""
echo "Good luck with your research! 🚀"
