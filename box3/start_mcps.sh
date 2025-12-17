#!/bin/bash
# Box 3 MCP Wrappers Startup Script

set -e

echo "🚀 Starting Box 3 MCP Wrappers"
echo "=============================="

# Check if Ollama is running
echo "Checking Ollama..."
if ! curl -s http://localhost:11434/api/tags > /dev/null; then
    echo "❌ Ollama not running! Start with: ollama serve"
    exit 1
fi
echo "✅ Ollama running"

# Check if models are installed
echo ""
echo "Checking models..."

models=("nemotron-ocr-v1" "whisper-large-v3" "olmo-3-7b-think")
for model in "${models[@]}"; do
    if ollama list | grep -q "$model"; then
        echo "✅ $model installed"
    else
        echo "⚠️  $model not found. Install with: ollama pull $model"
    fi
done

# Install Python dependencies if needed
if [ ! -d "venv" ]; then
    echo ""
    echo "Creating Python virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    
    # Install Playwright browsers
    playwright install chromium
    
    echo "✅ Dependencies installed"
else
    source venv/bin/activate
fi

# Start MCP wrappers in background
echo ""
echo "Starting MCP services..."

# Port 8083: Vision MCP
python3 vision_mcp.py &
VISION_PID=$!
echo "✅ Vision MCP started (PID $VISION_PID) on port 8083"

# Wait a moment for startup
sleep 2

# Port 8084: Voice MCP
python3 voice_mcp.py &
VOICE_PID=$!
echo "✅ Voice MCP started (PID $VOICE_PID) on port 8084"

sleep 2

# Port 8085: Browser MCP
python3 browser_mcp.py &
BROWSER_PID=$!
echo "✅ Browser MCP started (PID $BROWSER_PID) on port 8085"

sleep 2

# Check health endpoints
echo ""
echo "Health checks..."
curl -s http://localhost:8083/health | jq '.status' || echo "⚠️  Vision MCP not responding"
curl -s http://localhost:8084/health | jq '.status' || echo "⚠️  Voice MCP not responding"
curl -s http://localhost:8085/health | jq '.status' || echo "⚠️  Browser MCP not responding"

echo ""
echo "=============================="
echo "✅ Box 3 MCP Wrappers Ready!"
echo ""
echo "Endpoints:"
echo "  Vision:  http://localhost:8083"
echo "  Voice:   http://localhost:8084"
echo "  Browser: http://localhost:8085"
echo ""
echo "PIDs: Vision=$VISION_PID Voice=$VOICE_PID Browser=$BROWSER_PID"
echo "Stop with: kill $VISION_PID $VOICE_PID $BROWSER_PID"
echo ""
echo "Logs: tail -f /tmp/box3_*.log"

# Keep script running
wait
