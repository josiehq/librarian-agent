# JosieDesk Integration Checklist

## System Architecture Overview

```
┌─ Python Swarm (josiedesk_*.py) ─┐
│                                   │
│  Core (Vertical Loop)             │
│  ├─ josiedesk_core.py (Josie)    │
│  ├─ Roark A-Class → Blueprint    │
│  ├─ DoctrineCheck (B-Class)      │
│  └─ C-Loop Sprint (C/D-Class)    │
│                                   │
│  Hybrid Runtime (C/D-Class)       │
│  ├─ josiedesk_hybrid.py           │
│  ├─ Puckfairy (D1 - Executor)    │
│  ├─ Diplo (D2 - Memory)          │
│  ├─ Clash/Bash (C-Class Devs)    │
│  └─ Gunash/Concrete (B-Class)    │
│                                   │
│  Memory Service (Diplo D2)        │
│  └─ josiedesk_memory.py           │
│     ├─ LlamaIndex Storage        │
│     └─ Flask REST API (8081)     │
│                                   │
└───────────────────────────────────┘
              │ HTTP JSON-RPC 2.0
              ▼
┌─ Go Kernel (Kirktower) ───────────┐
│                                    │
│  MCP Server (Port 8080)           │
│  ├─ container_exec                │
│  ├─ memory_commit                 │
│  └─ fs_write_guarded              │
│                                    │
│  Tower Control (State Mgmt)       │
│  ├─ Process Management            │
│  ├─ Waria (Meta-Cognitive Audit) │
│  └─ WebSocket Broadcast (CLI)    │
│                                    │
│  Types (Shared Structs)          │
│  ├─ ProcessState                  │
│  ├─ WariaState                    │
│  └─ SystemState                   │
│                                    │
│  CLI (tower_cll.go)              │
│  └─ TUI Dashboard                 │
│                                    │
└────────────────────────────────────┘
```

## Dependency Matching Status

### ✅ Fixed Issues

1. **[FIXED]** Duplicate struct definitions
   - Removed duplicates from `kirktower.go` 
   - Kept single source of truth in `types.go`
   - tower_cll.go mirrors for CLI compilation

2. **[FIXED]** MCP Protocol Mismatch
   - Go mcp_server now accepts TWO formats:
     - Python format: `{name, arguments, agent_id}`
     - Go format: `[args_map, agent_id_string]`
   - Intelligent parsing in `ServeHTTP()`

3. **[FIXED]** Tool Argument Structure
   - `container_exec` expects: `{command, image}`
   - `memory_commit` expects: `{log_type, content}`
   - `fs_write_guarded` expects: `{path, content, force_override}`
   - All Python wrappers updated to match

4. **[FIXED]** Agent ID Tracking
   - All MCP tools now include `agent_id` parameter
   - Puckfairy (D1) → agent_id="puckfairy"
   - Diplo (D2) → agent_id="diplo"
   - Clash/Bash (C-Class) → agent_id="clash"/"bash"

5. **[FIXED]** Python Dependencies
   - Added `flask>=2.3.0` to setup.py
   - Added `pyautogen>=0.2.0` to setup.py
   - Kept `httpx>=0.24.0` for async HTTP calls
   - Kept llama-index dependencies

### 🔄 Communication Flow (HTTP JSON-RPC 2.0)

#### Request Format (Python → Go)
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
  "id": "a1b2c3d4"
}
```

#### Response Format (Go → Python)
```json
{
  "jsonrpc": "2.0",
  "result": "Script executed successfully...",
  "id": "a1b2c3d4"
}
```

OR on error:
```json
{
  "jsonrpc": "2.0",
  "error": {
    "code": -32000,
    "message": "Tool Execution Error",
    "data": {"details": "Error message"}
  },
  "id": "a1b2c3d4"
}
```

### 🔗 Integration Points

#### 1. Python → Go (MCP Calls)
- **Endpoint**: `http://localhost:8080/api/mcp`
- **Tools Available**:
  - `container_exec` - Execute in sandbox
  - `memory_commit` - Log to Diplo
  - `fs_write_guarded` - Safe file writes

#### 2. Go → Python (Memory Logging)
- **Endpoint**: `http://127.0.0.1:8081/ingest_log` (internal only)
- **When**: After MCP tool execution
- **Data**: agent, phase, content

#### 3. WebSocket (TUI CLI)
- **Endpoint**: `ws://localhost:8080/ws`
- **Broadcast**: SystemState (process/Waria updates)
- **Consumer**: tower_cll.go (Terminal UI)

### 📦 Package Dependencies

**Python** (setup.py):
```
httpx>=0.24.0          # Async HTTP client
flask>=2.3.0           # Memory service REST
llama-index>=0.9.0     # Vector storage
pyautogen>=0.2.0       # Multi-agent framework
asyncio-contextmanager # Async utilities
```

**Go** (go.mod):
```
github.com/gorilla/websocket   # WebSocket server
github.com/charmbracelet/bubbletea  # TUI (tower_cll)
github.com/charmbracelet/lipgloss   # TUI styling
```

### ✅ Verification Checklist

- [x] types.go contains all struct definitions
- [x] mcp_server.go imports types correctly
- [x] kirktower.go references structs from types.go (no duplication)
- [x] tower_cll.go mirrors structs for CLI build
- [x] MCP protocol supports both Python and Go formats
- [x] Python call_mcp_tool includes agent_id
- [x] All tool functions have agent_id parameter
- [x] Memory service endpoint documented
- [x] setup.py has all required packages
- [x] Async/await chain properly implemented

### 🚀 Startup Order

1. **Start Go Kernel**:
   ```bash
   go run *.go
   # Starts HTTP server on :8080
   # Starts WebSocket on ws://localhost:8080/ws
   ```

2. **Start Memory Service**:
   ```bash
   python -m josiedesk_memory
   # Starts Flask on http://127.0.0.1:8081
   # Only accessible locally (security)
   ```

3. **Start Python Swarm**:
   ```bash
   python josiedesk_core.py
   # Creates task
   # Calls Kirktower via HTTP JSON-RPC
   ```

### 🧪 Testing

**Test MCP Connection**:
```bash
curl -X POST http://localhost:8080/api/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "container_exec",
    "params": {
      "name": "container_exec",
      "arguments": {"command": "echo test", "image": "alpine"},
      "agent_id": "test_agent"
    },
    "id": 1
  }'
```

**Test Memory Logging**:
```bash
curl -X POST http://127.0.0.1:8081/ingest_log \
  -H "Content-Type: application/json" \
  -d '{
    "agent": "diplo",
    "phase": "c_loop",
    "content": "Test log entry"
  }'
```

## Status: ✅ READY FOR INTEGRATION

All dependencies are matched and code paths verified for proper communication.
