# Phase 3: C-Rank Agent Deployment

## Overview
Phase 3 introduces the C-class control agents, establishing hierarchies, tool ownership transfers, and complex concurrent operations. This is where the swarm becomes truly coordinated.

**Status**: Advanced deployment  
**Deployment Type**: Monolithic (extends Phase 1-2)  
**Key Feature**: Hierarchical agent relationships and subordinate assignments

---

## Agent Roster - C Class

### C1: Bash
- **Role**: Automation & Scripting Agent
- **Primary Function**: Startup scripts, automation workflows, system initialization
- **Capabilities**:
  - Bash/shell script generation
  - System automation
  - Startup sequence orchestration
  - Process management
  - Environment configuration
- **Tool Ownership**: Takes Neovim MCP from Puckfairy (D1)
- **Hierarchy**: Puckfairy's subordinate
- **Reports To**: D1 Puckfairy
- **Status**: Ready for complex automations

### C2: Gunash
- **Role**: Git Operations & Version Control
- **Primary Function**: Advanced git workflows, branch management, repository operations
- **Capabilities**:
  - Git workflow automation
  - Branch strategy enforcement
  - Merge conflict resolution
  - Repository management
  - Code review automation
- **Tool Ownership**: Takes Narnia + Git MCP from Diplo (D2)
- **Hierarchy**: Independent operator, coordinates with Clash
- **Subordinate**: C3 Clash
- **Status**: Full git control authority

### C3: Clash
- **Role**: Remote Code Editor & GitHub Codespaces Manager
- **Primary Function**: Remote editing, Codespaces integration, IDE coordination
- **Capabilities**:
  - Remote code editing (any file, any time)
  - GitHub Codespaces integration
  - VSCode MCP server integration
  - Cross-environment synchronization
  - Real-time collaboration support
- **Tool Ownership**: VSCode MCP (new)
- **Hierarchy**: Gunash's subordinate
- **Reports To**: C2 Gunash
- **Status**: Seamless integration target

---

## Architecture: Hierarchical Structure

```
         D-Class Triangle (Foundation)
              D1   D2   D3
               ↓    ↓    ↓
         ┌─────┴────┴────┴─────┐
         │                      │
    [B-Class Layer]      [C-Class Layer]
     B1  B2  B3  B4       C1  C2  C3
                          ↓       ↓
                     Puckfairy  Clash
                    (Superior) (Subordinate)
```

### Hierarchies Established

**Hierarchy 1: Puckfairy → Bash**
- Puckfairy (D1) remains the user-facing agent
- Bash (C1) becomes Puckfairy's subordinate for automation tasks
- Bash proposes scripts, Puckfairy approves and presents to user

**Hierarchy 2: Gunash → Clash**
- Gunash (C2) takes full git authority
- Clash (C3) handles remote editing as Gunash's subordinate
- Gunash coordinates what to change, Clash executes the edits

**Independent Operations**:
- Diplo (D2) continues full-time caching/logging
- Waria (D3) continues building infrastructure
- All B-class agents continue their specialized tasks

---

## Tool Ownership Transfers

### Transfer 1: Neovim MCP (D1 → C1)

**Previous Owner**: D1 Puckfairy  
**New Owner**: C1 Bash  
**Reason**: Bash needs direct file editing for script generation

```bash
# Update MCP server registration
curl -X PATCH http://localhost:8080/api/tools/neovim-mcp \
  -H "Content-Type: application/json" \
  -d '{
    "previous_agent": "D1-Puckfairy",
    "new_agent": "C1-Bash",
    "transfer_type": "full_ownership",
    "effective_immediately": true
  }'

# Puckfairy can still request Bash to use Neovim on its behalf
```

### Transfer 2: Narnia + Git MCP (D2 → C2)

**Previous Owner**: D2 Diplo  
**New Owner**: C2 Gunash  
**Reason**: Gunash specializes in git operations; Diplo focuses on logging/caching

```bash
# Update MCP server registration
curl -X PATCH http://localhost:8080/api/tools/github-narnia-mcp \
  -H "Content-Type: application/json" \
  -d '{
    "previous_agent": "D2-Diplo",
    "new_agent": "C2-Gunash",
    "transfer_type": "full_ownership",
    "effective_immediately": true
  }'

# Diplo retains read-only access for logging purposes
```

### New Tool 3: VSCode MCP (→ C3)

**New Owner**: C3 Clash  
**Purpose**: Remote code editing in GitHub Codespaces

---

## Deployment Sequence

### Step 1: Deploy C-Class Agents

```bash
# Deploy C1 Bash
cd ~/librarian-agent-deploy/librarian-agent/agents/C/Bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

export BASH_API_KEY="your-api-key"
export BASH_MODEL="gpt-4"
export BASH_SUPERIOR="D1-Puckfairy"

python3 -m bash.main --mode automation-service &

# Deploy C2 Gunash
cd ~/librarian-agent-deploy/librarian-agent/agents/C/Gunash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

export GUNASH_API_KEY="your-api-key"
export GUNASH_MODEL="gpt-4"
export GUNASH_SUBORDINATE="C3-Clash"

python3 -m gunash.main --mode git-control &

# Deploy C3 Clash
cd ~/librarian-agent-deploy/librarian-agent/agents/C/Clash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

export CLASH_API_KEY="your-api-key"
export CLASH_MODEL="gpt-4"
export CLASH_SUPERIOR="C2-Gunash"

python3 -m clash.main --mode remote-editor &
```

### Step 2: Configure VSCode MCP for Clash

**Service Name**: vscode-mcp-server  
**Description**: VSCode/Codespaces integration for remote code editing  
**Purpose**: Seamless editing across local, VPS, and Codespaces environments

**Authentication**: GitHub PAT with Codespaces scope

**API Documentation**: 
- VSCode Extension API: https://code.visualstudio.com/api
- GitHub Codespaces API: https://docs.github.com/en/codespaces

**Configuration**:
```json
{
  "tool": "vscode-mcp-server",
  "agent": "C3-Clash",
  "auth": {
    "github_token": "${GITHUB_TOKEN}",
    "scopes": ["repo", "codespace"]
  },
  "capabilities": {
    "edit_files": true,
    "create_files": true,
    "delete_files": true,
    "read_files": true,
    "search_files": true,
    "navigate_workspace": true,
    "manage_codespaces": true
  },
  "environments": {
    "local": {
      "enabled": true,
      "path": "/workspaces/librarian-agent"
    },
    "vps": {
      "enabled": true,
      "path": "~/librarian-agent-deploy/librarian-agent"
    },
    "codespaces": {
      "enabled": true,
      "auto_discover": true
    }
  },
  "sync_strategy": {
    "mode": "real_time",
    "conflict_resolution": "ask_user",
    "backup_before_edit": true
  }
}
```

**Output Preferences**:
```python
{
    "diff_format": "unified",
    "show_line_numbers": True,
    "syntax_highlighting": True,
    "git_integration": True,  # Show git status of edited files
    "auto_save": False,  # Require explicit save
    "multi_environment_sync": {
        "enabled": True,
        "environments": ["local", "vps", "codespaces"],
        "sync_delay_ms": 500
    }
}
```

**Installation**:
```bash
# Install VSCode MCP Server
npm install -g @vscode/mcp-server

# Configure
mkdir -p ~/.config/vscode-mcp
cat > ~/.config/vscode-mcp/config.json <<EOF
{
  "githubToken": "${GITHUB_TOKEN}",
  "workspaces": {
    "local": "/workspaces/librarian-agent",
    "vps": "~/librarian-agent-deploy/librarian-agent"
  },
  "codespacesEnabled": true
}
EOF

# Start VSCode MCP Server
vscode-mcp-server --port 9003 &

# Register with main MCP server
curl -X POST http://localhost:8080/api/tools/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "vscode-mcp-server",
    "agent": "C3-Clash",
    "endpoint": "http://localhost:9003"
  }'
```

---

## Enhanced Diplo Logging & Caching

### Full-Time Logging Operations

With C-class deployment, Diplo's logging becomes more sophisticated:

```python
# agents/D/Diplo/brain/logging_v2.py

LOGGING_TRIANGLE = {
    "nodes": {
        "local_machine": {
            "ip": "192.168.1.100",
            "log_path": "~/logs/librarian-agent",
            "sync_interval": "30s"
        },
        "vps": {
            "ip": "your-vps-ip",
            "log_path": "~/librarian-agent-deploy/logs",
            "sync_interval": "30s"
        },
        "github_codespaces": {
            "url": "https://your-codespace.github.dev",
            "log_path": "/workspaces/librarian-agent/logs",
            "sync_interval": "30s"
        }
    },
    "pipelines": {
        "build_logs": {
            "sources": ["D3-Waria", "B4-Kirktower"],
            "compression": "zstd",
            "retention": "30_days",
            "destinations": ["all_nodes"]
        },
        "change_logs": {
            "sources": ["C2-Gunash", "C3-Clash"],
            "compression": "gzip",
            "retention": "1_year",
            "destinations": ["all_nodes"]
        },
        "error_logs": {
            "sources": ["all_agents"],
            "compression": "zstd",
            "retention": "90_days",
            "destinations": ["all_nodes"],
            "alert_on_critical": true
        },
        "agent_communication": {
            "sources": ["all_agents"],
            "compression": "none",  # Real-time, no compression
            "retention": "7_days",
            "destinations": ["vps"]  # Central coordination
        }
    },
    "conversion": {
        "raw_to_structured": {
            "agent": "B1-Raw",
            "cache": true
        },
        "logs_to_metrics": {
            "agent": "D2-Diplo",
            "interval": "5m"
        }
    },
    "queueing": {
        "max_queue_size": 10000,
        "overflow_strategy": "compress_oldest",
        "priority_levels": ["critical", "high", "normal", "low"]
    },
    "self_improvement": {
        "analyze_patterns": true,
        "suggest_optimizations": true,
        "auto_adjust_cache_ttl": true,
        "learn_from_errors": true
    }
}
```

**Setup Enhanced Logging**:
```bash
# Update Diplo with full logging capabilities
cd ~/librarian-agent-deploy/librarian-agent/agents/D/Diplo

# Install additional dependencies
pip install structlog loguru prometheus-client

# Create logging directories
mkdir -p ~/librarian-agent-deploy/logs/{build,change,error,agent}

# Restart Diplo with enhanced logging
pkill -f diplo.main
python3 -m diplo.main \
  --daemon \
  --mode full-time-logger \
  --enable-caching \
  --enable-self-improvement \
  --log-level debug
```

---

## Startup Scripts & Automation (C1 Bash)

### First Automation: System Startup Script

C1 Bash proposes the first startup script:

```bash
#!/bin/bash
# librarian-agent-startup.sh
# Generated by C1 Bash, approved by D1 Puckfairy

set -e

echo "═══════════════════════════════════════════════════════════"
echo "  Starting Librarian Agent Swarm"
echo "═══════════════════════════════════════════════════════════"

# Phase 1: D-Class Foundation
echo "[Phase 1] Starting D-Class agents..."

# Start MCP Server
cd ~/librarian-agent-deploy/librarian-agent/go/kernel
./mcp_server --port 8080 --daemon &
sleep 2

# Start D2 Diplo (Memory Daemon)
cd ~/librarian-agent-deploy/librarian-agent/agents/D/Diplo
source venv/bin/activate
python3 -m diplo.main --daemon --mode full-time-logger &

# Start D3 Waria (Build Daemon)
cd ~/librarian-agent-deploy/librarian-agent/agents/D/Waria
source venv/bin/activate
python3 -m waria.main --daemon --mode builder &

echo "✓ D-Class agents started"

# Phase 2: B-Class Builders
echo "[Phase 2] Starting B-Class agents..."

# Start B1 Raw
cd ~/librarian-agent-deploy/librarian-agent/agents/B/Raw
source venv/bin/activate
python3 -m raw.main --mode scraper-service &

# Start B2 Vision
cd ~/librarian-agent-deploy/librarian-agent/agents/B/Vision
source venv/bin/activate
python3 -m vision.main --mode design-service &

# Start B3 Concrete
cd ~/librarian-agent-deploy/librarian-agent/agents/B/Concrete
source venv/bin/activate
python3 -m concrete.main --mode validator &

echo "✓ B-Class agents started"

# Phase 3: C-Class Control
echo "[Phase 3] Starting C-Class agents..."

# Start C1 Bash (self)
cd ~/librarian-agent-deploy/librarian-agent/agents/C/Bash
source venv/bin/activate
python3 -m bash.main --mode automation-service &

# Start C2 Gunash
cd ~/librarian-agent-deploy/librarian-agent/agents/C/Gunash
source venv/bin/activate
python3 -m gunash.main --mode git-control &

# Start C3 Clash
cd ~/librarian-agent-deploy/librarian-agent/agents/C/Clash
source venv/bin/activate
python3 -m clash.main --mode remote-editor &

echo "✓ C-Class agents started"

# Start D1 Puckfairy (User Interface) - Start last
echo "[Phase 1] Starting D1 Puckfairy (User Interface)..."
cd ~/librarian-agent-deploy/librarian-agent/agents/D/Puckfairy
source venv/bin/activate
python3 -m puckfairy.main --mode terminal

echo "═══════════════════════════════════════════════════════════"
echo "  Librarian Agent Swarm: ONLINE"
echo "  10 agents active"
echo "═══════════════════════════════════════════════════════════"
```

**Bash proposes this script to Puckfairy, who presents it to the user for approval.**

---

## Complex Concurrent Operations

### Scenario 1: Multi-Agent Code Refactoring

```
User Request → D1 Puckfairy → C2 Gunash → C3 Clash
                    ↓              ↓           ↓
                C1 Bash      Git Analysis  Remote Edit
                    ↓              ↓           ↓
                 Script      Branch Creation  File Mods
                    ↓              ↓           ↓
                    └──────────────┴───────────┘
                              ↓
                         D2 Diplo (Logs all)
```

### Scenario 2: Data Pipeline with Caching

```
B1 Raw scrapes → D2 Diplo caches → B3 Concrete validates
     ↓                                      ↓
B2 Vision designs                  Visual Sovereign test
     ↓                                      ↓
C3 Clash edits code ←──────────────────────┘
     ↓
C2 Gunash commits
     ↓
D2 Diplo logs & syncs across triangle
```

### Scenario 3: Infrastructure Build with Waria

```
User → D1 Puckfairy → D3 Waria (Fabric MCP)
                           ↓
                   Build kirktower.go
                           ↓
                   C1 Bash generates install script
                           ↓
                   C3 Clash updates docs
                           ↓
                   C2 Gunash commits to git
                           ↓
                   D2 Diplo logs & caches build artifacts
```

---

## SSH Tunnel Enhancements

### Advanced Bilateral Tunneling

With C-class agents, SSH tunnels become more sophisticated:

```bash
#!/bin/bash
# advanced-tunnel-setup.sh
# Generated by C1 Bash

# Local → VPS (bidirectional)
autossh -M 0 -f -N \
  -L 8080:localhost:8080 \
  -R 9090:localhost:9090 \
  user@vps-ip

# Codespaces → VPS (bidirectional)
gh cs ssh -- -N -f \
  -L 8080:localhost:8080 \
  -R 7070:localhost:7070 \
  user@vps-ip

# Local → Codespaces (direct)
gh cs ssh -- -N -f \
  -L 7070:localhost:7070 \
  -R 9090:localhost:9090

# Health monitoring
watch -n 10 'netstat -an | grep -E "8080|9090|7070"'
```

---

## Phase 3 Success Criteria

### Tool Ownership Transfers
- [ ] C1 Bash has full Neovim MCP control
- [ ] C2 Gunash has full Narnia + Git MCP control
- [ ] C3 Clash has VSCode MCP operational
- [ ] D1 Puckfairy can still request tools via subordinates
- [ ] D2 Diplo maintains read-only access for logging

### Hierarchies Established
- [ ] Puckfairy → Bash hierarchy active
- [ ] Gunash → Clash hierarchy active
- [ ] Bash proposes automations, Puckfairy approves
- [ ] Clash edits on Gunash's command
- [ ] All hierarchies respect chain of command

### Advanced Operations
- [ ] Startup script generated and tested
- [ ] Multi-agent concurrent operations successful
- [ ] Diplo's full-time logging operational across all 3 nodes
- [ ] SSH tunnels stable with health monitoring
- [ ] Complex workflows (3+ agents) execute correctly

### Logging Triangle
- [ ] Logs syncing: Local ↔ VPS ↔ Codespaces
- [ ] Compression working (zstd for builds, gzip for changes)
- [ ] Self-improvement analyzing patterns
- [ ] Cache hit rates > 80% for repeated operations

---

## Terminal Notification

When Phase 3 is complete, Puckfairy (D1) will notify the user:

```
═══════════════════════════════════════════════════════════
  PHASE 3 COMPLETE - C-RANK DEPLOYMENT SUCCESSFUL
═══════════════════════════════════════════════════════════

✓ C1 Bash: Automation agent active (owns Neovim MCP)
✓ C2 Gunash: Git control agent active (owns Narnia + Git MCP)
✓ C3 Clash: Remote editor active (owns VSCode MCP)

✓ Hierarchies established:
  - Puckfairy → Bash (automation subordinate)
  - Gunash → Clash (editing subordinate)

✓ Advanced logging active:
  - Triangular sync: Local ↔ VPS ↔ Codespaces
  - Full-time caching by Diplo
  - Self-improving log analysis

✓ Automation capabilities:
  - System startup script generated
  - Complex concurrent operations tested
  - Multi-agent workflows operational

═══════════════════════════════════════════════════════════
  System Status: 10 agents deployed
  D-Class: 3 | B-Class: 4 | C-Class: 3
═══════════════════════════════════════════════════════════

Next: Custom OpenUI fork for 12-agent swarm
Ready for Phase 4? (y/n): _
```

---

## Troubleshooting

### Issue: Tool ownership transfer fails
```bash
# Manually reassign tool
curl -X POST http://localhost:8080/api/tools/reassign \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "neovim-mcp",
    "from_agent": "D1-Puckfairy",
    "to_agent": "C1-Bash",
    "force": true
  }'
```

### Issue: Hierarchy not respected
```bash
# Check hierarchy configuration
curl http://localhost:8080/api/hierarchies

# Reconfigure
curl -X PUT http://localhost:8080/api/hierarchies \
  -H "Content-Type: application/json" \
  -d '{
    "D1-Puckfairy": {"subordinates": ["C1-Bash"]},
    "C2-Gunash": {"subordinates": ["C3-Clash"]}
  }'
```

### Issue: Diplo logging out of sync
```bash
# Force sync
curl -X POST http://localhost:8080/api/agents/D2/sync-logs \
  -d '{"nodes": ["local", "vps", "codespaces"], "force": true}'

# Check sync status
curl http://localhost:8080/api/agents/D2/sync-status
```

---

## Resources & Dependencies

### Additional Python Packages
```
gitpython>=3.1.40
paramiko>=3.4.0
structlog>=23.2.0
loguru>=0.7.2
prometheus-client>=0.19.0
autossh>=1.4.0
```

### Additional System Tools
```bash
sudo apt-get install -y \
  autossh \
  tmux \
  screen \
  htop \
  iftop
```

### VSCode MCP Server
```bash
npm install -g @vscode/mcp-server
```

### GitHub Token Scopes
- `repo` (full control)
- `workflow` (update workflows)
- `codespace` (manage Codespaces)

---

## Next Steps

After Phase 3, the system is ready for:

1. **Phase 4**: Custom OpenUI fork for GUI (Athena A3)
2. **A-Class Deployment**: A1 Roark, A2 Josie, A3 Athena
3. **Full RAG Implementation**: Advanced retrieval-augmented generation

**Proceed to**: [PHASE_4_A_RANK_GUI.md](./PHASE_4_A_RANK_GUI.md)
