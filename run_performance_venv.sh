#!/bin/bash
# Run Energy-Responsive Performance Mixer with venv

echo "🎭 Starting Energy-Responsive Eurovision Performance..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found"
    echo "Please run setup first:"
    echo "  ./setup_venv.sh"
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Check if required packages are installed
echo "🔍 Checking dependencies..."
python3 -c "import librosa, pyaudio, numpy" 2>/dev/null || {
    echo "❌ Missing dependencies"
    echo "Please run setup first:"
    echo "  ./setup_venv.sh"
    exit 1
}

echo "✅ All dependencies found"
echo ""

# Run the performance mixer
python performance_energy_mixer.py

# Deactivate virtual environment on exit
deactivate

echo ""
echo "👋 Performance stopped!"
