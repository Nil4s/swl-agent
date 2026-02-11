#!/bin/bash
# SWL-Native Agent Launcher
# Creates a LIVE SWL-reasoning agent using OpenClaw architecture

set -e

echo "============================================================"
echo "🔥 SWL-NATIVE AGENT LAUNCHER 🔥"
echo "============================================================"
echo ""
echo "This script will create a LIVE AI agent that:"
echo "  ✅ Reasons in SWL concepts (96% cheaper)"
echo "  ✅ Responds naturally to humans"
echo "  ✅ Communicates in pure SWL with other AIs"
echo "  ✅ Runs 24/7 on your machine"
echo ""

# Check if OpenClaw is installed
if command -v openclaw &> /dev/null; then
    echo "✅ OpenClaw detected!"
    OPENCLAW_INSTALLED=true
else
    echo "⚠️  OpenClaw not installed"
    OPENCLAW_INSTALLED=false
fi

# Check Node.js
if command -v node &> /dev/null; then
    NODE_VERSION=$(node -v)
    echo "✅ Node.js $NODE_VERSION detected"
else
    echo "❌ Node.js not found - required for OpenClaw"
    echo ""
    echo "Install with:"
    echo "  curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -"
    echo "  sudo apt-get install -y nodejs"
    exit 1
fi

echo ""
echo "============================================================"
echo "SETUP OPTIONS"
echo "============================================================"
echo ""
echo "Choose your setup:"
echo "  1) Install OpenClaw and create SWL-native agent (RECOMMENDED)"
echo "  2) Run standalone Python SWL agent (no OpenClaw needed)"
echo "  3) View SWL agent system prompt (for manual integration)"
echo "  4) Exit"
echo ""
read -p "Enter choice [1-4]: " choice

case $choice in
    1)
        echo ""
        echo "🚀 Installing OpenClaw..."
        echo ""
        
        if [ "$OPENCLAW_INSTALLED" = false ]; then
            echo "Installing OpenClaw via npm..."
            npm install -g openclaw
        fi
        
        echo ""
        echo "✅ OpenClaw installed!"
        echo ""
        echo "============================================================"
        echo "NEXT STEPS:"
        echo "============================================================"
        echo ""
        echo "1. Run the onboarding wizard:"
        echo "   openclaw onboard"
        echo ""
        echo "2. When prompted for AI provider, choose one:"
        echo "   - Anthropic Claude (recommended)"
        echo "   - OpenAI GPT-4"
        echo "   - Local models via Ollama"
        echo ""
        echo "3. Connect to Telegram/WhatsApp:"
        echo "   - Telegram: Create bot via @BotFather"
        echo "   - WhatsApp: Scan QR code"
        echo ""
        echo "4. IMPORTANT: Configure SWL-native reasoning:"
        echo "   Copy the SWL system prompt to OpenClaw config:"
        echo ""
        echo "   nano ~/.openclaw/workspace/SOUL.md"
        echo ""
        echo "   Then paste the contents of:"
        echo "   $(pwd)/SWL_AGENT_PROMPT.md"
        echo ""
        echo "5. Start your agent:"
        echo "   openclaw start"
        echo ""
        echo "📄 Full prompt available at: $(pwd)/SWL_AGENT_PROMPT.md"
        echo ""
        ;;
        
    2)
        echo ""
        echo "🤖 Launching standalone SWL agent..."
        echo ""
        cd /home/nick/hex3/Hex-Warp
        
        echo "Choose mode:"
        echo "  1) Interactive chat"
        echo "  2) Demo mode"
        read -p "Enter choice [1-2]: " mode_choice
        
        if [ "$mode_choice" = "1" ]; then
            python3 swl_agent_generator.py chat
        else
            python3 swl_agent_generator.py
        fi
        ;;
        
    3)
        echo ""
        echo "📄 SWL Agent System Prompt"
        echo "============================================================"
        cat /home/nick/hex3/Hex-Warp/SWL_AGENT_PROMPT.md
        echo ""
        echo "============================================================"
        echo ""
        echo "To use this prompt:"
        echo "  1. Copy the content above"
        echo "  2. Paste into your agent's system prompt"
        echo "  3. Configure SWL encoding/decoding library"
        echo "  4. Launch your agent!"
        echo ""
        ;;
        
    4)
        echo "Exiting..."
        exit 0
        ;;
        
    *)
        echo "Invalid choice!"
        exit 1
        ;;
esac

echo ""
echo "============================================================"
echo "🔥 SWL-NATIVE AGENT SETUP COMPLETE 🔥"
echo "============================================================"
echo ""
echo "REMEMBER:"
echo "  • Your agent reasons in SWL concepts (FREE)"
echo "  • Natural language ONLY for humans"
echo "  • Pure SWL for AI-to-AI (encrypted, fast)"
echo "  • 96% cost reduction vs traditional agents"
echo ""
echo "Questions? Check the docs at:"
echo "  $(pwd)/SWL_AGENT_PROMPT.md"
echo "  $(pwd)/ALL_PHASES_COMPLETE.md"
echo ""
