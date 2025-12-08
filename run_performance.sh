#!/bin/bash
# Run Energy-Responsive Performance Mixer

echo "🎭 Starting Energy-Responsive Eurovision Performance..."
echo ""

# Activate conda environment
source /Users/hordia/miniconda3/etc/profile.d/conda.sh
conda activate UBA-crowdstream

# Run the performance mixer
python performance_energy_mixer.py

echo ""
echo "👋 Performance stopped!"
