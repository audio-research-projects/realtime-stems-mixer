#!/bin/bash
# Setup Virtual Environment for Performance Energy Mixer - Raspberry Pi
# Optimized for ARM architecture (Raspberry Pi 3/4/5)

set -e  # Exit on error

echo "🎭 Setting up Performance Energy Mixer for Raspberry Pi"
echo "========================================================"
echo ""

# Check if running on ARM
ARCH=$(uname -m)
if [[ ! "$ARCH" =~ ^(arm|aarch64) ]]; then
    echo "⚠️  This script is optimized for ARM architecture (Raspberry Pi)"
    echo "Current architecture: $ARCH"
    echo "Consider using setup_venv.sh instead"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "✅ Detected ARM architecture: $ARCH"
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    echo "Installing Python 3..."
    sudo apt-get update
    sudo apt-get install -y python3 python3-pip python3-venv
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✅ Found Python $PYTHON_VERSION"
echo ""

# Install system dependencies FIRST
echo "📦 Installing system dependencies..."
echo "This will require sudo privileges"
echo ""

# Update package list
sudo apt-get update

# Install audio system dependencies
echo "Installing audio libraries..."
sudo apt-get install -y \
    portaudio19-dev \
    python3-pyaudio \
    libsndfile1 \
    libasound2-dev \
    libatlas-base-dev \
    libportaudio2 \
    || {
        echo "⚠️  Some packages failed to install"
        echo "Continuing anyway..."
    }

# Install build tools (needed for some Python packages)
echo ""
echo "Installing build tools..."
sudo apt-get install -y \
    build-essential \
    python3-dev \
    libffi-dev \
    || echo "⚠️  Build tools installation incomplete"

echo ""
echo "✅ System dependencies installed"
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
pip install --upgrade pip setuptools wheel

echo ""
echo "📥 Installing Python packages from requirements-rpi.txt..."
echo "This may take 10-20 minutes on Raspberry Pi..."
echo ""

# Check if requirements-rpi.txt exists
if [ ! -f "requirements-rpi.txt" ]; then
    echo "❌ requirements-rpi.txt not found"
    echo "Using minimal installation..."

    # Install core packages one by one
    echo "Installing numpy (this may take a while)..."
    pip install "numpy>=1.20.0,<2.0.0" || pip install numpy

    echo "Installing scipy..."
    pip install "scipy>=1.7.0,<1.12.0" || pip install scipy

    echo "Installing librosa..."
    pip install "librosa>=0.10.0,<0.11.0" || pip install librosa

    echo "Installing soundfile..."
    pip install soundfile

    echo "Installing python-osc..."
    pip install python-osc
else
    # Install from requirements-rpi.txt
    pip install -r requirements-rpi.txt || {
        echo ""
        echo "⚠️  Some packages failed to install from requirements-rpi.txt"
        echo "Installing core dependencies individually..."
        pip install numpy scipy librosa soundfile python-osc || {
            echo "❌ Failed to install core dependencies"
            exit 1
        }
    }
fi

echo ""
echo "📦 Installing PyAudio from system package..."
# PyAudio debe estar instalado desde sistema (python3-pyaudio)
# Verificar que esté disponible
python3 -c "import pyaudio" 2>/dev/null && {
    echo "✅ PyAudio available from system"
} || {
    echo "⚠️  PyAudio not found"
    echo "Attempting to create symlink..."

    # Buscar pyaudio en el sistema
    SYSTEM_PYAUDIO=$(python3 -c "import sys; print([p for p in sys.path if 'dist-packages' in p][0])" 2>/dev/null)

    if [ -n "$SYSTEM_PYAUDIO" ] && [ -d "$SYSTEM_PYAUDIO/pyaudio" ]; then
        VENV_SITE=$(python3 -c "import site; print(site.getsitepackages()[0])")
        ln -s "$SYSTEM_PYAUDIO/pyaudio" "$VENV_SITE/" 2>/dev/null || true
        ln -s "$SYSTEM_PYAUDIO"/_portaudio* "$VENV_SITE/" 2>/dev/null || true
        echo "✅ PyAudio symlink created"
    else
        echo "❌ Could not find system PyAudio"
        echo "Install with: sudo apt-get install python3-pyaudio"
    fi
}

echo ""
echo "========================================================"
echo "✅ Setup completed!"
echo ""
echo "📋 Verification:"
python3 -c "
import sys
try:
    import numpy
    print('✅ numpy:', numpy.__version__)
except:
    print('❌ numpy not found')

try:
    import scipy
    print('✅ scipy:', scipy.__version__)
except:
    print('❌ scipy not found')

try:
    import librosa
    print('✅ librosa:', librosa.__version__)
except:
    print('❌ librosa not found')

try:
    import soundfile
    print('✅ soundfile:', soundfile.__version__)
except:
    print('❌ soundfile not found')

try:
    import pyaudio
    print('✅ pyaudio available')
except:
    print('❌ pyaudio not found')

try:
    from pythonosc import udp_client
    print('✅ python-osc available')
except:
    print('❌ python-osc not found')
"

echo ""
echo "⚡ Performance Notes for Raspberry Pi:"
echo "   - Disable time-stretching in config for better performance"
echo "   - Use lower sample rate (22050 or 16000) if needed"
echo "   - Monitor CPU usage with: htop"
echo ""
echo "🚀 To run the performance mixer:"
echo "   source venv/bin/activate"
echo "   python performance_energy_mixer.py"
echo ""
echo "🛑 To deactivate:"
echo "   deactivate"
echo ""
