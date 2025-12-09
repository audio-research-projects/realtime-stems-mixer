#!/bin/bash
# Setup Virtual Environment for Performance Energy Mixer

set -e  # Exit on error

echo "🎭 Setting up Performance Energy Mixer Environment"
echo "=================================================="
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✅ Found Python $PYTHON_VERSION"
echo ""

# Create virtual environment
VENV_DIR="venv"

if [ -d "$VENV_DIR" ]; then
    echo "⚠️  Virtual environment already exists at ./$VENV_DIR"
    read -p "Do you want to recreate it? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🗑️  Removing old virtual environment..."
        rm -rf "$VENV_DIR"
    else
        echo "Using existing virtual environment"
    fi
fi

if [ ! -d "$VENV_DIR" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
    echo "✅ Virtual environment created at ./$VENV_DIR"
fi

echo ""
echo "🔧 Activating virtual environment..."
source "$VENV_DIR/bin/activate"

echo "📥 Upgrading pip..."
pip install --upgrade pip

echo ""
echo "📥 Installing dependencies from requirements.txt..."
echo "This may take a few minutes..."
echo ""

# Check if requirements.txt exists
if [ ! -f "requirements.txt" ]; then
    echo "❌ requirements.txt not found"
    exit 1
fi

# Special handling for PyAudio on different platforms
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "ℹ️  macOS detected"
    echo "Checking for portaudio..."
    if ! brew list portaudio &>/dev/null; then
        echo "⚠️  portaudio not found"
        echo "Installing portaudio via Homebrew..."
        brew install portaudio || {
            echo ""
            echo "⚠️  Failed to install portaudio"
            echo "Please install manually: brew install portaudio"
        }
    else
        echo "✅ portaudio already installed"
    fi
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "ℹ️  Linux detected"
    echo "If PyAudio installation fails, install system dependencies:"
    echo "  sudo apt-get install python3-pyaudio portaudio19-dev"
fi

echo ""
echo "📦 Installing Python packages..."
pip install -r requirements.txt || {
    echo ""
    echo "⚠️  Some packages failed to install"
    echo "Trying to install core dependencies only..."
    pip install numpy scipy librosa soundfile python-osc
    echo ""
    echo "Attempting PyAudio separately..."
    pip install pyaudio || {
        echo "⚠️  PyAudio installation failed"
        echo "Please install system dependencies and try again"
    }
}

echo ""
echo "=================================================="
echo "✅ Setup completed successfully!"
echo ""
echo "📋 Installed packages:"
pip list | grep -E "numpy|scipy|librosa|soundfile|pyaudio|python-osc"
echo ""
echo "🚀 To use the environment:"
echo "   source venv/bin/activate"
echo ""
echo "🎭 To run the performance mixer:"
echo "   ./run_performance_venv.sh"
echo ""
echo "🛑 To deactivate the environment:"
echo "   deactivate"
echo ""
