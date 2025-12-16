# JosieDesk Integration - Complete Setup Guide

## 📋 Overview

This is a fully integrated multi-agent software construction swarm with:
- **Python Orchestration Layer**: Josie (Vertical Loop), C-Loop (Horizontal Consensus)
- **Go Execution Kernel**: Kirktower (MCP Server, Process Control, Waria Auditing)
- **Persistent Memory**: Diplo with LlamaIndex + Flask
- **TUI Dashboard**: Tower CLI with Bubble Tea

## 🔗 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  Python Swarm (Port varies)                 │
│                                                              │
│  Core Orchestration       C-Loop Agents     Memory Service  │
│  ┌──────────────────┐    ┌──────────────┐  ┌─────────────┐ │
│  │ josiedesk_core   │    │ josiedesk_   │  │ josiedesk_  │ │
│  │ (Vertical Loop)  │───→│ hybrid       │──→│ memory      │ │
│  │                  │    │ (AutoGen)    │  │ (Flask)     │ │
│  └──────────────────┘    └──────────────┘  └─────────────┘ │
│         │                                          │         │
│         │ HTTP JSON-RPC 2.0                        │         │
│         │ JSON-RPC Protocol                        │         │
└─────────┼────────────────────────────────────────┼─────────┘
          │ :8080                                  │ :8081
          ▼                                        │
┌─────────────────────────────────────────────────▼──────────┐
│                    Go Kernel (Kirktower)                    │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  MCP Server (JSON-RPC 2.0 Endpoint)                 │  │
│  │  ├─ container_exec                                  │  │
│  │  ├─ memory_commit (calls Flask endpoint)            │  │
│  │  └─ fs_write_guarded                                │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Tower Control                                      │  │
│  │  ├─ ProcessState Management                         │  │
│  │  ├─ WariaState (Meta-Cognitive Audit)             │  │
│  │  └─ WebSocket Broadcaster                          │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Data Structures (types.go)                         │  │
│  │  ├─ ProcessState (Process tracking)                 │  │
│  │  ├─ WariaState (Reasoning metrics)                  │  │
│  │  └─ SystemState (Overall snapshot)                  │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
          ▲              ▲              ▲
          │ :8080        │ :3000        │ WebSocket
          │ JSON-RPC     │ (Future)     │ :8080/ws
          │              │              │
    ┌─────┴──────────────┴──────────────┴──────┐
    │      Terminal UI (tower_cll.go)         │
    │   - Process Dashboard                   │
    │   - Waria Metrics                       │
    │   - Real-time State Updates             │
    └─────────────────────────────────────────┘
```

## 🚀 Quick Start

### 1. Prerequisites

```bash
# Go 1.20+
go version

# Python 3.8+
python --version

# Docker (for container_exec)
docker --version
```

### 2. Install Python Dependencies

```bash
cd /home/Josie/DEV/Pythong/JOSIEDESK/v1/librarian-agent

# Create virtual environment (if not already done)
python -m venv venv
source venv/bin/activate

# Install package in development mode
pip install -e .

# Verify installations
pip list | grep -E "httpx|flask|pyautogen|llama"
```

### 3. Start Go Kernel

```bash
# Terminal 1: Go Kernel
cd /home/Josie/DEV/Pythong/JOSIEDESK/v1/librarian-agent
go run *.go

# Expected output:
# [TowerControl] Initialized with Waria metrics
# Starting MCP Server on :8080
# Starting WebSocket on ws://localhost:8080/ws
# Ready for connections...
```

### 4. Start Memory Service

```bash
# Terminal 2: Memory Service (if using external memory)
cd /home/Josie/DEV/Pythong/JOSIEDESK/v1/librarian-agent
python -c "from josiedesk_memory import start_memory_service; start_memory_service()"

# Expected output:
# [Diplo] Starting Swarm Memory Service on http://127.0.0.1:8081...
```

### 5. Run Core Orchestrator

```bash
# Terminal 3: Python Orchestration
cd /home/Josie/DEV/Pythong/JOSIEDESK/v1/librarian-agent
python josiedesk_core.py

# Expected output:
# --- JOSIEDESK VERTICAL ORCHESTRATION STARTED ---
# Task: <your task description>
# [Josie] PHASE: blueprint...
```

## 📡 Communication Protocol

### MCP Request Format (Python → Go)

```json
{
  "jsonrpc": "2.0",
  "method": "container_exec",
  "params": {
    "name": "container_exec",
    "arguments": {
      "command": "python main.py",
      "image": "python:3.11-slim"
    },
    "agent_id": "puckfairy"
  },
  "id": "unique-request-id"
}
```

### MCP Response Format (Go → Python)

**Success:**
```json
{
  "jsonrpc": "2.0",
  "result": "Output from executed command",
  "id": "unique-request-id"
}
```

**Error:**
```json
{
  "jsonrpc": "2.0",
  "error": {
    "code": -32000,
    "message": "Tool Execution Error",
    "data": {"details": "Detailed error message"}
  },
  "id": "unique-request-id"
}
```

## 🧪 Testing

### Test 1: MCP Connection

```bash
curl -X POST http://localhost:8080/api/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "container_exec",
    "params": {
      "name": "container_exec",
      "arguments": {
        "command": "echo test",
        "image": "alpine:latest"
      },
      "agent_id": "test_agent"
    },
    "id": 1
  }' | python -m json.tool
```

**Expected Response:**
```json
{
  "jsonrpc": "2.0",
  "result": "test\n",
  "id": 1
}
```

### Test 2: Memory Logging

```bash
curl -X POST http://127.0.0.1:8081/ingest_log \
  -H "Content-Type: application/json" \
  -d '{
    "agent": "puckfairy",
    "phase": "c_loop_sprint",
    "content": "Successfully executed container command"
  }'
```

**Expected Response:**
```json
{
  "status": "success",
  "message": "Log ingested and indexed."
}
```

### Test 3: WebSocket Connection

```bash
# Using websocat (install: brew install websocat)
websocat ws://localhost:8080/ws

# Or using Python
python -c "
import asyncio
import websockets
import json

async def test_ws():
    async with websockets.connect('ws://localhost:8080/ws') as ws:
        msg = await ws.recv()
        print('Received:', json.loads(msg))

asyncio.run(test_ws())
"
```

## 📊 File Structure

```
librarian-agent/
├── types.go                     # Shared data structures
├── mcp_server.go               # JSON-RPC 2.0 MCP endpoint
├── kirktower.go                # Tower control system
├── tower_cll.go                # Terminal UI dashboard
├── josiedesk_core.py           # Vertical loop orchestrator
├── josiedesk_hybrid.py         # C-Loop agents & MCP client
├── josiedesk_memory.py         # Memory service & Flask
├── setup.py                    # Python package config
├── go.mod                      # Go module dependencies
├── go.sum                      # Go dependency checksums
├── INTEGRATION_CHECKLIST.md    # Detailed integration guide
├── CHANGES_SUMMARY.md          # List of all changes
└── README.md                   # This file
```

## 🔐 Security Notes

1. **Memory Service**: Only binds to `127.0.0.1:8081` (localhost only)
2. **MCP Endpoint**: Implement authentication for production
3. **Container Execution**: Runs in sandboxed containers by default
4. **File Operations**: Guarded writes with irreversibility checks

## 🐛 Troubleshooting

### Error: "Connection refused" on :8080

```bash
# Check if port is in use
lsof -i :8080
# Kill existing process if needed
kill -9 <PID>
```

### Error: "ImportError: No module named 'flask'"

```bash
# Reinstall dependencies
pip install -e .
# Or manually:
pip install flask httpx pyautogen llama-index
```

### Error: "docker: command not found"

```bash
# Install Docker
brew install docker          # macOS
sudo apt-get install docker.io  # Linux
# Or download from docker.com
```

### Error: "Type mismatch in JSON response"

Check that:
1. Go is using correct JSON struct tags (defined in types.go)
2. Python is sending correct parameter format
3. Both are using same agent_id convention

## 📈 Performance Metrics

The Waria subsystem tracks:
- **Prompt Length**: Cumulative token count
- **Context Reuse**: How many times context is retrieved
- **Cross-Phase References**: References across phases
- **Confidence Plateau**: When LLM confidence stops improving
- **Verbosity Increase**: Excessive logging detection

## 🔄 Vertical Loop Phases

1. **BEGINNING**: Initialize
2. **BLUEPRINT**: Roark generates implementation plan
3. **DOCTRINE_CHECK**: Josie validates against constraints
4. **C_LOOP_SPRINT**: C-Class agents execute via AutoGen
5. **SUPERVISION**: Post-execution audit
6. **CONCLUSION**: Summarize and persist results

## 🤖 Agent Roles

**A-Class (Planning)**
- Roark: Strategic blueprint designer

**B-Class (Audit)**
- Josie: Doctrine enforcer
- Concrete: Security auditor
- Gunash: Structure guardian

**C-Class (Construction)**
- Clash: Code implementer
- Bash: Script specialist

**D-Class (Execution)**
- Puckfairy (D1): Container executor
- Diplo (D2): Memory/Oracle

## 📚 Further Reading

- [JSON-RPC 2.0 Spec](https://www.jsonrpc.org/specification)
- [Go HTTP Handlers](https://golang.org/pkg/net/http/)
- [LlamaIndex Docs](https://docs.llamaindex.ai/)
- [AutoGen Documentation](https://microsoft.github.io/autogen/)

## ✅ Verification Checklist

- [ ] Go kernel running on :8080
- [ ] Python dependencies installed
- [ ] Memory service running on :8081 (if needed)
- [ ] MCP test request returns valid response
- [ ] Python can import all modules
- [ ] WebSocket connection works
- [ ] Full vertical loop completes without errors

## 🎯 Next Steps

1. **Extend MCP Tools**: Add new tools to mcp_server.go
2. **Implement Roark**: Build A-Class planning agent
3. **Add Persistence**: Connect to actual database
4. **Deploy**: Set up in production environment
5. **Monitor**: Integrate with observability tools

---

**Last Updated**: December 16, 2025  
**Status**: ✅ Ready for Integration & Testing
