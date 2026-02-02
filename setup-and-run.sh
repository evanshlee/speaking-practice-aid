#!/bin/bash

# Speaking Practice Aid - Complete Setup and Run Script
# This script installs all dependencies (backend + frontend) and runs both servers

# Color definitions
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Project directories
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
CLIENT_DIR="$PROJECT_DIR/client"
SERVER_DIR="$PROJECT_DIR/server"
VENV_DIR="$PROJECT_DIR/venv"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Speaking Practice Aid${NC}"
echo -e "${BLUE}  Complete Setup & Run${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check prerequisites
echo -e "${BLUE}Checking prerequisites...${NC}"
echo ""

MISSING_DEPS=0

# Check Python
if command -v python3 &>/dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
    
    if [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -ge 9 ]; then
        echo -e "${GREEN}✓ Python $PYTHON_VERSION${NC}"
    else
        echo -e "${RED}✗ Python 3.9+ required (found: $PYTHON_VERSION)${NC}"
        echo -e "  Install with: ${YELLOW}brew install python@3.11${NC} or ${YELLOW}pyenv install 3.11${NC}"
        MISSING_DEPS=1
    fi
else
    echo -e "${RED}✗ Python 3.9+ not found${NC}"
    echo -e "  Install with: ${YELLOW}brew install python@3.11${NC} or ${YELLOW}pyenv install 3.11${NC}"
    MISSING_DEPS=1
fi

# Check Node.js
if command -v node &>/dev/null; then
    NODE_VERSION=$(node --version)
    echo -e "${GREEN}✓ Node.js $NODE_VERSION${NC}"
else
    echo -e "${RED}✗ Node.js not found${NC}"
    echo -e "  Install with: ${YELLOW}brew install node${NC}"
    MISSING_DEPS=1
fi

# Check FFmpeg
if command -v ffmpeg &>/dev/null; then
    FFMPEG_VERSION=$(ffmpeg -version 2>&1 | head -n1 | awk '{print $3}')
    echo -e "${GREEN}✓ FFmpeg $FFMPEG_VERSION${NC}"
else
    echo -e "${RED}✗ FFmpeg not found${NC}"
    echo -e "  Install with: ${YELLOW}brew install ffmpeg${NC}"
    MISSING_DEPS=1
fi

if [ $MISSING_DEPS -eq 1 ]; then
    echo ""
    echo -e "${RED}Please install missing prerequisites and try again.${NC}"
    exit 1
fi

echo -e "${GREEN}All prerequisites satisfied!${NC}"
echo ""

# Check if virtual environment exists
if [ ! -d "$VENV_DIR" ]; then
    echo -e "${YELLOW}[1/4] Creating Python virtual environment...${NC}"
    python3 -m venv "$VENV_DIR"
    if [ $? -ne 0 ]; then
        echo -e "${RED}Failed to create virtual environment. Please ensure Python 3.9+ is installed.${NC}"
        exit 1
    fi
    echo -e "${GREEN}      ✓ Virtual environment created${NC}"
else
    echo -e "${GREEN}[1/4] Virtual environment already exists${NC}"
fi
echo ""

# Install backend dependencies
echo -e "${YELLOW}[2/4] Installing backend dependencies...${NC}"
source "$VENV_DIR/bin/activate"
pip install -q -r "$SERVER_DIR/requirements.txt"
if [ $? -eq 0 ]; then
    echo -e "${GREEN}      ✓ Backend dependencies installed${NC}"
else
    echo -e "${RED}      ✗ Failed to install backend dependencies${NC}"
    exit 1
fi
echo ""

# Install frontend dependencies
echo -e "${YELLOW}[3/4] Installing frontend dependencies...${NC}"
cd "$CLIENT_DIR"
npm install --silent
if [ $? -eq 0 ]; then
    echo -e "${GREEN}      ✓ Frontend dependencies installed${NC}"
else
    echo -e "${RED}      ✗ Failed to install frontend dependencies${NC}"
    exit 1
fi
echo ""

# Cleanup all background processes on exit
cleanup() {
    echo ""
    echo -e "${RED}Shutting down servers...${NC}"
    kill $CLIENT_PID 2>/dev/null
    kill $SERVER_PID 2>/dev/null
    exit 0
}
trap cleanup SIGINT SIGTERM

# Start backend server
echo -e "${GREEN}[4/4] Starting servers...${NC}"
echo ""
echo -e "${GREEN}  → Starting Backend Server (FastAPI)...${NC}"
cd "$SERVER_DIR"
source "$VENV_DIR/bin/activate"
python main.py &
SERVER_PID=$!
echo -e "      Backend PID: $SERVER_PID"
echo -e "      Backend URL: http://localhost:8000"
echo ""

# Start client server
echo -e "${GREEN}  → Starting Client Server (Vite)...${NC}"
cd "$CLIENT_DIR"
npm run dev &
CLIENT_PID=$!
echo -e "      Client PID: $CLIENT_PID"
echo ""

echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}✓ Setup complete! Both servers are running!${NC}"
echo -e "  Frontend: ${BLUE}http://localhost:5173${NC}"
echo -e "  Backend:  ${BLUE}http://localhost:8000${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "Press ${RED}Ctrl+C${NC} to stop both servers."
echo ""

# Wait until processes terminate
wait
