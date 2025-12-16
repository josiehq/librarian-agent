# Librarian Agent - Reorganized

## 📁 Directory Structure

```
librarian-agent/
├── py/                          # Python orchestration layer
│   ├── orchestration/           # Vertical (Josie) and Horizontal (C-Loop) loops
│   │   ├── josie.py            # Josie: Vertical orchestrator
│   │   └── c_loop.py           # C-Loop: AutoGen consensus swarm
│   ├── memory/                  # Persistent memory service
│   │   └── diplo.py            # Diplo: Memory manager (LlamaIndex + Flask)
│   ├── common/                  # Shared utilities
│   └── tests/                   # Python test suite
│
├── go/                          # Go kernel and CLI
│   ├── kernel/                  # MCP server and control tower
│   │   ├── kirktower.go        # Main control tower (TowerControl)
│   │   ├── mcp_server.go       # JSON-RPC 2.0 MCP implementation
│   │   └── types.go            # Data structures (ProcessState, WariaState, etc.)
│   ├── cli/                     # Terminal user interface
│   │   └── tower_cll.go        # TUI for monitoring swarm
│   └── go.mod                   # Go dependencies
│
├── agents/                      # 12 Agent definitions (A, B, C, D)
│   ├── A/                       # A-Class Agents (Planning/70B+)
│   │   ├── tools/              # Agent tools
│   │   ├── brain/              # Agent reasoning/rules
│   │   ├── profile/            # LLM config (api.py)
│   │   └── exemplar/           # Example outputs
│   ├── B/                       # B-Class Agents (Audit/15-60B)
│   ├── C/                       # C-Class Agents (Construction/3.5-13B)
│   └── D/                       # D-Class Agents (Execution/<3B)
│
├── docs/                        # Documentation
│   ├── README.md
│   ├── FINAL_REPORT.md
│   ├── INTEGRATION_CHECKLIST.md
│   └── ...
│
├── config/                      # Configuration files
│   ├── setup.py                # Python dependencies
│   └── requirements.txt        # Generated from setup.py
│
├── scripts/                     # Startup and utility scripts
│   └── QUICKSTART.sh           # Quick start guide
│
└── README.md                    # This file
```

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Go 1.21+
- Docker (optional, for container execution)

### 1. Start the Go MCP Server (Kernel)
```bash
cd go
go run kernel/*.go
# Or: go build -o kirktower_bin kernel/*.go types.go && ./kirktower_bin
```
Server listens on `http://localhost:8080`
- MCP Endpoint: `http://localhost:8080/api/mcp`
- State Endpoint: `http://localhost:8080/api/state`
- WebSocket: `ws://localhost:8080/ws`

### 2. Start Diplo Memory Service
```bash
cd py
python -m memory.diplo
# Or: python -c "from py.memory.diplo import start_memory_service; start_memory_service()"
```
Service listens on `http://127.0.0.1:8081`

### 3. Run Vertical Orchestration (Josie)
```bash
cd py
python -m orchestration.josie
```

### 4. Monitor with TUI (optional)
```bash
cd go
go run cli/tower_cll.go
# Connects to ws://localhost:9090/ws
```

## 🤖 Agent Classes

| Class | Codenames | Size | Role | Responsible For |
|-------|-----------|------|------|-----------------|
| **A** | Roark | 70B+ | Planning | Blueprint generation |
| **B** | Josie, Concrete, Gunash | 15-60B | Audit | Doctrine checks, security, structure |
| **C** | Clash, Bash | 3.5-13B | Construction | Code writing, automation |
| **D** | Puckfairy, Diplo | <3B | Execution | Container exec, memory management |

## 🔌 API Configuration

Each agent in `agents/<class>/profile/api.py` has:
```python
def get_llm_config():
    return {
        "model": os.getenv("AGENT_MODEL", "gpt-4"),
        "api_key": os.getenv("AGENT_API_KEY", "sk-placeholder"),
        "temperature": float(os.getenv("AGENT_TEMPERATURE", "0.4")),
        "timeout": int(os.getenv("AGENT_TIMEOUT", "120")),
    }
```

Set per-agent via environment variables:
```bash
export AGENT_MODEL="gpt-4"
export AGENT_API_KEY="sk-..."
python -m orchestration.josie
```

## 📡 MCP Tool Reference

### Available Tools via JSON-RPC
- `container_exec`: Execute command in isolated container
- `memory_commit`: Commit logs to persistent memory
- `fs_write_guarded`: Guarded file write with safety checks

### Example JSON-RPC Call
```bash
curl -X POST http://127.0.0.1:8080/api/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc":"2.0",
    "method":"container_exec",
    "params":{
      "name":"container_exec",
      "arguments":{"command":"echo hello","image":"alpine"},
      "agent_id":"test_agent"
    },
    "id":1
  }'
```

## 🧪 Testing

```bash
cd py
python -m pytest tests/
```

## 📚 Documentation

- [Integration Guide](docs/INTEGRATION_CHECKLIST.md)
- [Final Report](docs/FINAL_REPORT.md)
- [Detailed Changes](docs/DETAILED_CHANGES.md)

---

**Last Updated**: December 16, 2025  
**Status**: ✅ Reorganized for clarity and scalability
