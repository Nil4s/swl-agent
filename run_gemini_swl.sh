#!/bin/bash
# Pure SWL Gemini Agent Launcher
# Revolutionary experiment: Gemini that can ONLY think in concepts

set -e

echo "========================================================================"
echo "🔥 PURE SWL GEMINI AGENT - REVOLUTIONARY EXPERIMENT"
echo "========================================================================"
echo ""
echo "This Gemini agent is FORBIDDEN from using English."
echo "It can ONLY communicate via SWL concept arrays."
echo ""

# Check for API key
if [ -z "$GEMINI_API_KEY" ]; then
    echo "⚠️  GEMINI_API_KEY not set!"
    echo ""
    echo "Get your free API key at: https://makersuite.google.com/app/apikey"
    echo ""
    echo "Then run:"
    echo "  export GEMINI_API_KEY='your-key-here'"
    echo "  ./run_gemini_swl.sh"
    echo ""
    exit 1
fi

# Activate venv
cd /home/nick/hex3/Hex-Warp
source swl_gemini_env/bin/activate

echo "✅ Environment activated"
echo "✅ Gemini API key detected"
echo ""
echo "========================================================================"
echo "CHOOSE MODE:"
echo "========================================================================"
echo ""
echo "  1) Two-Agent SWL Experiment (DEMO)"
echo "     → Watch two Gemini agents communicate in pure SWL"
echo "     → Zero English between them"
echo "     → Proves concept-based reasoning works"
echo ""
echo "  2) Interactive SWL Mode (CHAT)"
echo "     → Send concept arrays to pure SWL Gemini"
echo "     → Test if it can stay SWL-only"
echo "     → Track violations"
echo ""

read -p "Enter choice [1-2]: " choice

echo ""

case $choice in
    1)
        echo "🚀 Launching two-agent SWL experiment..."
        echo ""
        python3 gemini_swl_pure.py
        ;;
    2)
        echo "🤖 Launching interactive SWL mode..."
        echo ""
        python3 gemini_swl_pure.py chat
        ;;
    *)
        echo "Invalid choice!"
        exit 1
        ;;
esac
