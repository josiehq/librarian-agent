# Phase 1: D-Rank Agent Deployment

## Overview
Phase 1 establishes the foundational D-class agents (Puckfairy, Diplo, Waria) in a VPS environment, creating the triangular communication pattern that powers the entire system.

**Status**: Checkpoint 1 of 2  
**Deployment Type**: Monolithic (no containers)  
**Environment**: VPS + Local Machine + GitHub Codespaces

---

## Agent Roster - D Class

### D1: Puckfairy
- **Role**: User Terminal Interface Agent
- **Primary Function**: Direct user interaction via terminal
- **Capabilities**: 
  - Terminal command execution
  - User query handling
  - Workflow orchestration initiation
  - Status reporting to user
- **Tools**: 
  - tower_cll.go (temporary CLI interface)
  - Neovim MCP (Phase 1)
- **Note**: Can be substituted temporarily by Claude Pro API, Gemini API, or Ollama

### D2: Diplo
- **Role**: Memory & Integration Daemon
- **Primary Function**: Git integration, change detection, and logging coordination
- **Capabilities**:
  - Narnia CLI wrapper integration
  - Recent changes detection
  - User prompt for action decisions
  - Logging pipeline coordination
  - Smart caching (Phase 2+)
- **Tools**:
  - Narnia CLI (~/DEV/Pythong/NARNIA/)
  - GitHub MCP (Phase 1)
- **Daemon**: Runs as background service

### D3: Waria
- **Role**: Build & Infrastructure Daemon
- **Primary Function**: tower_cll.go construction and infrastructure management
- **Capabilities**:
  - tower_cll.go building
  - Kirktower.go construction (Phase 1 completion)
  - Infrastructure adaptability
  - Fabric MCP integration
- **Tools**:
  - Fabric MCP (https://github.com/ksylvan/fabric-mcp)
- **Daemon**: Runs as background service
- **Priority**: Maximum flexibility for various server sizes/types/LLM models

---

## Architecture: The Triangle

```
        D1 (Puckfairy)
       /              \
      /    Logging     \
     /    Pipeline      \
    /                    \
D2 (Diplo) --------- D3 (Waria)
   Memory              Build
```

### Communication Pattern
The triangle is the most powerful shape in nature:

1. **D1 ↔ D2**: User commands → Narnia/Git actions → Status reports
2. **D1 ↔ D3**: User requests → Build commands → Progress updates  
3. **D2 ↔ D3**: Change logs → Build triggers → Deployment confirmations

### Logging Pipeline
- D1 has access to user terminal (like Copilot)
- D2 manages memory, caching, and git state
- D3 builds infrastructure and reports build status
- All three maintain synchronized logs across VPS, local machine, and GitHub

---

## Deployment Sequence

### Prerequisites
- VPS with SSH access
- Local machine with development environment
- GitHub Codespaces access
- Narnia CLI tool (~/DEV/Pythong/NARNIA/)

### Step 1: VPS Initial Setup
```bash
# SSH into VPS
ssh user@your-vps-ip

# Create deployment directory
mkdir -p ~/librarian-agent-deploy
cd ~/librarian-agent-deploy

# Clone repository
git clone https://github.com/josiehq/librarian-agent.git
cd librarian-agent
```

### Step 2: Deploy D-Class Agents

#### 2a: Deploy D1 Puckfairy (Terminal Agent)
```bash
# Setup D1 environment
cd agents/D/Puckfairy
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt  # Create this

# Configure API keys
export PUCKFAIRY_API_KEY="your-api-key"
export PUCKFAIRY_MODEL="claude-3-5-sonnet-20241022"

# Start D1 (interactive mode)
python3 -m puckfairy.main --mode terminal
```

#### 2b: Deploy D2 Diplo (Memory Daemon)
```bash
# In separate terminal/tmux session
cd agents/D/Diplo

# Install Narnia CLI integration
# Ensure Narnia is accessible from VPS
git clone https://github.com/your-repo/narnia.git ~/narnia
cd ~/narnia && ./install.sh

# Configure D2
export DIPLO_API_KEY="your-api-key"
export DIPLO_MODEL="gpt-4"
export NARNIA_PATH="$HOME/narnia"

# Start D2 as daemon
python3 -m diplo.main --daemon --mode git-monitor
```

#### 2c: Deploy D3 Waria (Build Daemon)
```bash
# In third terminal/tmux session
cd agents/D/Waria

# Configure D3
export WARIA_API_KEY="your-api-key"
export WARIA_MODEL="gpt-4"

# Start D3 as daemon
python3 -m waria.main --daemon --mode builder
```

### Step 3: Build tower_cll.go
```bash
# D3 Waria handles this, but manual fallback:
cd go/cli
go build -o tower_cll tower_cll.go

# Verify build
./tower_cll --version
```

---

## MCP Server Integration (Monolithic)

### Setup mcp_server.go
```bash
cd go/kernel
go mod download

# Build MCP server
go build -o mcp_server mcp_server.go types.go kirktower.go

# Start MCP server
./mcp_server --port 8080 &
```

### Phase 1 MCP Tools

#### For D1 Puckfairy: Neovim MCP
**Service**: Neovim integration via MCP  
**Purpose**: File editing and code navigation  
**Authentication**: Local socket connection  
**API Docs**: https://neovim.io/doc/user/api.html

**Configuration**:
```json
{
  "tool": "neovim-mcp",
  "agent": "D1-Puckfairy",
  "socket": "/tmp/nvim-mcp.sock",
  "capabilities": ["edit", "navigate", "search"]
}
```

**Output**: File modifications, cursor positions, buffer contents

#### For D2 Diplo: GitHub & Narnia MCP
**Service**: GitHub API + Narnia CLI wrapper  
**Purpose**: Git operations, change detection, PR management  
**Authentication**: GitHub PAT token  
**API Docs**: 
- https://docs.github.com/en/rest
- Narnia internal docs (in ~/DEV/Pythong/NARNIA/docs/)

**Configuration**:
```json
{
  "tool": "github-narnia-mcp",
  "agent": "D2-Diplo",
  "github_token": "${GITHUB_TOKEN}",
  "narnia_path": "${HOME}/narnia/narnia",
  "capabilities": [
    "detect_changes",
    "create_pr",
    "review_changes",
    "sync_branches"
  ]
}
```

**Output**: Change diffs, commit logs, PR status, branch info

#### For D3 Waria: Fabric MCP
**Service**: Fabric - AI-powered CLI patterns  
**Purpose**: Code generation, build automation, pattern application  
**Authentication**: API key for LLM providers  
**API Docs**: https://github.com/ksylvan/fabric-mcp

**Configuration**:
```json
{
  "tool": "fabric-mcp",
  "agent": "D3-Waria",
  "fabric_path": "${HOME}/.local/bin/fabric",
  "patterns": [
    "create_code_mod",
    "improve_code",
    "write_docs"
  ],
  "llm_provider": "openai"
}
```

**Output**: Generated code, build scripts, documentation, refactored code

---

## Bilateral SSH Tunneling

### Local ↔ VPS Tunnel
```bash
# On local machine
ssh -N -L 8080:localhost:8080 user@vps-ip &
ssh -N -R 9090:localhost:9090 user@vps-ip &
```

### GitHub Codespaces ↔ VPS Tunnel
```bash
# In Codespaces
gh cs ssh --server-port 8080 -- -L 8080:localhost:8080 -R 9090:localhost:9090
```

### Triangle Communication Setup
```
Local Machine (Port 9090) ←→ VPS (Port 8080) ←→ GitHub Codespaces (Port 7070)
         ↑                                                    ↓
         └───────────────── Direct tunnel ─────────────────→
```

---

## Checkpoint 1 Success Criteria

### Communication Tests
- [ ] D1 can receive user commands in terminal
- [ ] D2 can detect git changes via Narnia
- [ ] D3 can build tower_cll.go successfully
- [ ] All three agents can log to shared pipeline
- [ ] SSH tunnels are stable and bidirectional

### Concurrent Build Tests
This is the first major concurrency test:

1. **Diplo builds mcp_server.go** (simultaneously)
2. **Waria builds kirktower.go** (simultaneously)
3. **Puckfairy assists user** with installation coordination

**Success**: Both builds complete without conflicts, agents maintain communication throughout.

### Verification Commands
```bash
# Check D1 status
curl http://localhost:8080/api/agents/D1/status

# Check D2 status and Narnia integration
curl http://localhost:8080/api/agents/D2/status
curl http://localhost:8080/api/agents/D2/narnia/changes

# Check D3 status and build queue
curl http://localhost:8080/api/agents/D3/status
curl http://localhost:8080/api/agents/D3/builds

# Check logging triangle
curl http://localhost:8080/api/logs/triangle
```

---

## Terminal Notification

When Checkpoint 1 is reached, Puckfairy (D1) will notify the user:

```
═══════════════════════════════════════════════════════════
  CHECKPOINT 1 REACHED - D-RANK DEPLOYMENT COMPLETE
═══════════════════════════════════════════════════════════

✓ D1 Puckfairy: Terminal interface active
✓ D2 Diplo: Memory daemon running, Narnia integrated
✓ D3 Waria: Build daemon running, tower_cll.go deployed

✓ Triangular communication established:
  - VPS ↔ Local Machine ↔ GitHub Codespaces
  
✓ Concurrent build test passed:
  - mcp_server.go built by Diplo
  - kirktower.go built by Waria
  
✓ MCP tools integrated:
  - Neovim (D1)
  - GitHub + Narnia (D2)
  - Fabric (D3)

═══════════════════════════════════════════════════════════
  Ready for Checkpoint 2 (B-Rank Deployment)
═══════════════════════════════════════════════════════════

Proceed? (y/n): _
```

---

## Troubleshooting

### Issue: Agent can't connect to MCP server
```bash
# Check if MCP server is running
ps aux | grep mcp_server

# Check port availability
netstat -tulpn | grep 8080

# Restart MCP server
pkill mcp_server
cd ~/librarian-agent-deploy/librarian-agent/go/kernel
./mcp_server --port 8080 --log-level debug &
```

### Issue: Narnia not detecting changes
```bash
# Verify Narnia installation
which narnia
narnia --version

# Test Narnia manually
cd ~/librarian-agent-deploy/librarian-agent
narnia status

# Check D2 Diplo logs
tail -f ~/librarian-agent-deploy/logs/diplo.log
```

### Issue: SSH tunnel drops
```bash
# Use autossh for persistent tunnels
autossh -M 0 -N -L 8080:localhost:8080 user@vps-ip

# Monitor tunnel health
watch -n 5 'netstat -an | grep 8080'
```

---

## Resources & Dependencies

### Required Software
- Python 3.10+
- Go 1.21+
- Git 2.40+
- OpenSSH 8.0+
- tmux or screen (for daemon management)

### Python Packages
```
anthropic>=0.18.0
openai>=1.10.0
requests>=2.31.0
asyncio>=3.4.3
websockets>=12.0
pydantic>=2.5.0
```

### Go Modules
```
github.com/gorilla/mux
github.com/gorilla/websocket
github.com/joho/godotenv
```

### External Tools
- Narnia CLI: ~/DEV/Pythong/NARNIA/
- Fabric: https://github.com/danielmiessler/fabric

### API Keys Required
- Anthropic/Claude API key (for D1 if using Claude)
- OpenAI API key (for D2, D3)
- GitHub Personal Access Token
- Any additional LLM provider keys

---

## Next Steps

After completing Checkpoint 1:
1. User chooses to proceed to Checkpoint 2 or stop/save
2. If proceeding: Begin Phase 2 (B-Rank Deployment)
3. If stopping: Gracefully shut down daemons, save state
4. Puckfairy prompts user for decision

**Proceed to**: [PHASE_2_B_RANK_DEPLOYMENT.md](./PHASE_2_B_RANK_DEPLOYMENT.md)
