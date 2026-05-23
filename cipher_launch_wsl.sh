#!/bin/bash
# ============================================================
# CIPHER SOVEREIGN — WSL2 LAUNCHER
# Run in WSL2/Ubuntu terminal
# ============================================================

RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
GRAY='\033[0;37m'
NC='\033[0m'

echo ""
echo -e "  ${RED}⬡ CIPHER SOVEREIGN v2.0 — WSL2 LAUNCHER${NC}"
echo -e "  ${GRAY}Where chaos meets clarity.${NC}"
echo ""

CIPHER_DIR="$HOME/cipher"
mkdir -p "$CIPHER_DIR"

# ---- PYTHON DEPS ----
echo -e "  ${CYAN}[1/4] Installing Python dependencies...${NC}"
pip3 install fastapi uvicorn httpx duckduckgo-search python-dotenv aiohttp --break-system-packages -q
echo -e "  ${GREEN}✓ Dependencies ready${NC}"

# ---- OLLAMA CHECK ----
echo ""
echo -e "  ${CYAN}[2/4] Checking Ollama...${NC}"

# Try localhost first (Windows Ollama accessible from WSL2)
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo -e "  ${GREEN}✓ Ollama accessible at localhost:11434${NC}"
    OLLAMA_URL="http://localhost:11434"
elif curl -s http://host.docker.internal:11434/api/tags > /dev/null 2>&1; then
    echo -e "  ${GREEN}✓ Ollama accessible via host.docker.internal${NC}"
    OLLAMA_URL="http://host.docker.internal:11434"
else
    echo -e "  ${YELLOW}⚠ Ollama not detected. Install options:${NC}"
    echo -e "  ${GRAY}  A) Install on Windows: https://ollama.com/download${NC}"
    echo -e "  ${GRAY}  B) Install in WSL2: curl -fsSL https://ollama.com/install.sh | sh${NC}"
    echo ""
    read -p "  Install Ollama in WSL2 now? (y/n): " install_ollama
    if [ "$install_ollama" = "y" ]; then
        curl -fsSL https://ollama.com/install.sh | sh
        ollama serve &
        sleep 3
        OLLAMA_URL="http://localhost:11434"
        echo -e "  ${GREEN}✓ Ollama installed and running${NC}"
    else
        OLLAMA_URL="http://localhost:11434"
        echo -e "  ${YELLOW}  Cloud fallback will be used${NC}"
    fi
fi

# ---- PULL MODELS ----
echo ""
echo -e "  ${CYAN}[3/4] Model setup...${NC}"

if curl -s $OLLAMA_URL/api/tags > /dev/null 2>&1; then
    MODELS=$(curl -s $OLLAMA_URL/api/tags | python3 -c "import sys,json; m=json.load(sys.stdin).get('models',[]); [print(x['name']) for x in m]" 2>/dev/null)
    
    if [ -z "$MODELS" ]; then
        echo -e "  ${YELLOW}No models found. Pulling DeepSeek R1:8B (best reasoning/size ratio)...${NC}"
        ollama pull deepseek-r1:8b
    else
        echo -e "  ${GREEN}Models available:${NC}"
        echo "$MODELS" | while read m; do echo -e "  ${GRAY}  · $m${NC}"; done
    fi
    
    # Offer upgrades
    echo ""
    echo -e "  ${CYAN}Recommended models for maximum Cipher performance:${NC}"
    echo -e "  ${GRAY}  1) deepseek-r1:32b  — Best reasoning (20GB VRAM)${NC}"
    echo -e "  ${GRAY}  2) deepseek-r1:14b  — Great reasoning (9GB VRAM)${NC}"
    echo -e "  ${GRAY}  3) deepseek-r1:8b   — Fast reasoning (5GB VRAM)${NC}"
    echo -e "  ${GRAY}  4) llama3.3:70b     — General powerhouse (40GB RAM)${NC}"
    echo -e "  ${GRAY}  5) qwen2.5:32b      — Strong + fast (18GB RAM)${NC}"
    echo -e "  ${GRAY}  6) skip${NC}"
    echo ""
    read -p "  Pull additional model? (1-6): " model_choice
    case $model_choice in
        1) ollama pull deepseek-r1:32b ;;
        2) ollama pull deepseek-r1:14b ;;
        3) ollama pull deepseek-r1:8b ;;
        4) ollama pull llama3.3:70b ;;
        5) ollama pull qwen2.5:32b ;;
        *) echo -e "  ${GRAY}Skipping.${NC}" ;;
    esac
fi

# ---- COPY FILES ----
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cp "$SCRIPT_DIR/cipher_server.py" "$CIPHER_DIR/" 2>/dev/null && echo -e "  ${GREEN}✓ Server copied${NC}"
cp "$SCRIPT_DIR/cipher_command_center_v2.html" "$CIPHER_DIR/" 2>/dev/null && echo -e "  ${GREEN}✓ Dashboard copied${NC}"

# ---- LAUNCH ----
echo ""
echo -e "  ${CYAN}[4/4] Launching Cipher...${NC}"
echo ""
echo -e "  ${RED}┌─────────────────────────────────────────┐${NC}"
echo -e "  ${RED}│  CIPHER SOVEREIGN — OPERATIONAL         │${NC}"
echo -e "  ${RED}│  Local API:  http://localhost:3131       │${NC}"
echo -e "  ${RED}│  Status:     http://localhost:3131/status│${NC}"
echo -e "  ${RED}│  Open dashboard HTML in your browser     │${NC}"
echo -e "  ${RED}└─────────────────────────────────────────┘${NC}"
echo ""

cd "$CIPHER_DIR"
export OLLAMA_URL="$OLLAMA_URL"
python3 cipher_server.py
