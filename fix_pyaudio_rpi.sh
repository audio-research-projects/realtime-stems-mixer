#!/bin/bash
# Fix PyAudio in venv by adding system packages path
# Run this if PyAudio import fails after setup

echo "🔧 Fixing PyAudio for Raspberry Pi venv..."
echo ""

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found"
    echo "Please run ./setup_venv_rpi.sh first"
    exit 1
fi

# Activate venv
source venv/bin/activate

# Get venv site-packages directory
VENV_SITE=$(python3 -c "import site; print(site.getsitepackages()[0])")

if [ -z "$VENV_SITE" ]; then
    echo "❌ Could not determine venv site-packages directory"
    exit 1
fi

echo "📍 venv site-packages: $VENV_SITE"
echo ""

# Add system packages path
echo "📦 Adding system packages to venv..."
echo "/usr/lib/python3/dist-packages" > "$VENV_SITE/system-packages.pth"

echo "✅ System packages path added"
echo ""

# Test PyAudio
echo "🧪 Testing PyAudio import..."
python3 -c "import pyaudio; print('✅ PyAudio works!'); p = pyaudio.PyAudio(); print(f'✅ Found {p.get_device_count()} audio devices')" 2>&1 || {
    echo ""
    echo "❌ PyAudio still not working"
    echo ""
    echo "Please install system PyAudio:"
    echo "  sudo apt-get install python3-pyaudio"
    echo ""
    echo "Then run this script again"
    exit 1
}

echo ""
echo "✅ PyAudio is now working in venv!"
echo ""
echo "You can now run:"
echo "  source venv/bin/activate"
echo "  python performance_energy_mixer.py"
