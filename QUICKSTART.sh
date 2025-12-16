#!/bin/bash
# JOSIEDESK QUICK START GUIDE

echo "=== JosieDesk System Initialization ==="
echo ""
echo "Step 1: Install Python dependencies"
echo "  cd /home/Josie/DEV/Pythong/JOSIEDESK/v1/librarian-agent"
echo "  pip install -e ."
echo ""

echo "Step 2: Start Kirktower Control Kernel (Go)"
echo "  cd /home/Josie/DEV/Pythong/JOSIEDESK/v1/librarian-agent"
echo "  go run *.go"
echo "  # Expected: Listening on http://localhost:8080"
echo ""

echo "Step 3: Start Diplo Memory Service (Python Flask)"
echo "  # In another terminal:"
echo "  cd /home/Josie/DEV/Pythong/JOSIEDESK/v1/librarian-agent"
echo "  python3 josiedesk_memory.py"
echo "  # Expected: Listening on http://127.0.0.1:8081"
echo ""

echo "Step 4: Run orchestration (Python)"
echo "  # In another terminal:"
echo "  cd /home/Josie/DEV/Pythong/JOSIEDESK/v1/librarian-agent"
echo "  python3 josiedesk_core.py"
echo ""

echo "=== API ENDPOINTS ==="
echo ""
echo "Kirktower Control Kernel (Port 8080):"
echo "  - MCP Tool Calls:  POST http://localhost:8080/api/mcp"
echo "  - System State:    GET  http://localhost:8080/api/state"
echo "  - Waria Updates:   POST http://localhost:8080/api/waria"
echo "  - WebSocket CLI:   WS   ws://localhost:8080/ws"
echo ""

echo "Diplo Memory Service (Port 8081):"
echo "  - Ingest Logs:     POST http://127.0.0.1:8081/ingest_log"
echo ""

echo "=== EXAMPLE MCP CALL (curl) ==="
echo ""
echo 'curl -X POST http://localhost:8080/api/mcp \\'
echo '  -H "Content-Type: application/json" \\'
echo '  -d '"'"'{'
echo '    "jsonrpc": "2.0",'
echo '    "method": "container_exec",'
echo '    "params": {'
echo '      "name": "container_exec",'
echo '      "arguments": {'
echo '        "image": "alpine:latest",'
echo '        "command": "echo Hello from Kirktower"'
echo '      },'
echo '      "agent_id": "test-agent"'
echo '    },'
echo '    "id": "1"'
echo '  }'"'"''
echo ""

echo "=== TROUBLESHOOTING ==="
echo ""
echo "Port 8080 already in use:"
echo "  lsof -i :8080"
echo "  kill -9 <PID>"
echo ""

echo "Python import errors:"
echo "  pip install --upgrade httpx flask pyautogen llama-index"
echo ""

echo "Go build errors:"
echo "  go mod tidy"
echo "  go mod download"
echo ""
