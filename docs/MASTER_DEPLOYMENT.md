# Librarian Agent - Comprehensive Deployment Guide

## 🎯 Quick Reference

**Project**: Librarian Agent - Multi-Agent C2 System  
**Architecture**: Hierarchical 13-agent swarm with GUI  
**Deployment**: Phased monolithic approach (no containers in v1)  
**Environment**: VPS + Local Machine + GitHub Codespaces  

---

## 📋 Complete Agent Roster

| Class | Rank | Name | Role | Tools | Status |
|-------|------|------|------|-------|--------|
| **D** | D1 | Puckfairy | User Terminal Interface | Neovim MCP → Bash (C1) | Foundation |
| **D** | D2 | Diplo | Memory & Logging Daemon | GitHub+Narnia MCP → Gunash (C2) | Foundation |
| **D** | D3 | Waria | Build & Infrastructure | Fabric MCP | Foundation |
| **B** | B1 | Raw | Web Automation & Scraping | Selenium+Playwright MCP | Builder |
| **B** | B2 | Vision | Visual Design & Figma | Figma MCP | Builder |
| **B** | B3 | Concrete | Data Validation & Testing | Amazon MCP + Visual Sovereign | Builder |
| **B** | B4 | Kirktower | Infrastructure Core | kirktower.go | Builder |
| **C** | C1 | Bash | Automation & Scripting | Neovim MCP (from D1) | Control |
| **C** | C2 | Gunash | Git Operations | Narnia+GitHub MCP (from D2) | Control |
| **C** | C3 | Clash | Remote Code Editor | VSCode MCP | Control |
| **A** | A1 | Roark | Strategic Planning | Full system access | Command |
| **A** | A2 | Josie | Workflow Orchestration | Full system access | Command |
| **A** | A3 | Athena | GUI Command Center | RAG + OpenUI | Command |

**Total**: 13 agents (12 operational + 1 GUI)

---

## 🗺️ Deployment Roadmap

```
Phase 1 (D-Rank) ──► Phase 2 (B-Rank) ──► Phase 3 (C-Rank) ──► Phase 4 (A-Rank)
   Checkpoint 1          Checkpoint 2         Advanced             Complete
   Foundation            Tools + Testing      Hierarchies          GUI + C2
   3 agents              +4 agents (7 total)  +3 agents (10)       +3 agents (13)
```

### Phase 1: D-Rank Foundation
- **Agents**: D1 Puckfairy, D2 Diplo, D3 Waria
- **Goal**: Establish triangular communication pattern
- **Key Achievement**: Concurrent build test (mcp_server.go + kirktower.go)
- **Tools**: Neovim, GitHub+Narnia, Fabric MCP
- **Checkpoint**: Triangle communication verified

### Phase 2: B-Rank Builders
- **Agents**: B1 Raw, B2 Vision, B3 Concrete, B4 Kirktower
- **Goal**: Specialized tools and Visual Sovereign testing
- **Key Achievement**: First child build test
- **Tools**: Selenium+Playwright, Figma, Amazon MCP
- **Checkpoint**: Visual Sovereign validated

### Phase 3: C-Rank Control
- **Agents**: C1 Bash, C2 Gunash, C3 Clash
- **Goal**: Hierarchies, tool exchanges, complex operations
- **Key Achievement**: Startup automation and subordinate relationships
- **Tools**: Tool ownership transfers + VSCode MCP
- **Checkpoint**: 10 agents coordinated

### Phase 4: A-Rank Command
- **Agents**: A1 Roark, A2 Josie, A3 Athena
- **Goal**: GUI implementation and C2 server
- **Key Achievement**: Complete system with visual interface
- **Tools**: Custom OpenUI, Advanced RAG
- **Checkpoint**: 13-agent swarm operational

---

## 🛠️ Required Tools & Services

### MCP Tools

| Tool | Agent | Purpose | URL/Docs | Auth Required |
|------|-------|---------|----------|---------------|
| **Neovim MCP** | D1→C1 | File editing | https://neovim.io/doc/user/api.html | No |
| **GitHub MCP** | D2→C2 | Git operations | https://docs.github.com/en/rest | GitHub PAT |
| **Fabric MCP** | D3 | AI patterns/builds | https://github.com/ksylvan/fabric-mcp | LLM API key |
| **Selenium+Playwright** | B1 | Browser automation | https://playwright.dev/python/docs/api | No |
| **Figma MCP** | B2 | Design integration | https://www.figma.com/developers/api | Figma PAT |
| **Amazon MCP** | B3 | Product data | https://mcpservers.org/servers/r123singh/amazon-mcp-server | AWS PA API |
| **VSCode MCP** | C3 | Remote editing | https://code.visualstudio.com/api | GitHub PAT |

### External Tools

| Tool | Location | Purpose | Status |
|------|----------|---------|--------|
| **Narnia** | ~/DEV/Pythong/NARNIA/ | GitHub CLI wrapper | User's existing tool |
| **Visual Sovereign** | ~/DEV/GoRillah/PARAH | E-commerce tool | User's existing tool |
| **OpenUI Fork** | ~/DEV/openui | GUI framework | To be forked |

### Infrastructure

| Component | Technology | Port | Purpose |
|-----------|-----------|------|---------|
| **MCP Server** | Go (mcp_server.go) | 8080 | Central coordination |
| **Kirktower** | Go (kirktower.go) | - | B4 agent infrastructure |
| **Tower CLI** | Go (tower_cll.go) | - | Temporary CLI (Phase 1) |
| **GUI Frontend** | React/OpenUI | 3000 | User interface |
| **RAG Backend** | Python/ChromaDB | - | Athena intelligence |
| **Redis** | Redis Server | 6379 | Diplo caching |

---

## 🔑 Required API Keys & Credentials

### LLM Providers
```bash
# Anthropic/Claude (recommended for most agents)
export ANTHROPIC_API_KEY="sk-ant-..."

# OpenAI (alternative/backup)
export OPENAI_API_KEY="sk-..."

# Gemini (alternative)
export GEMINI_API_KEY="..."

# Ollama (local, no key needed)
# Just ensure ollama is running: ollama serve
```

### External Services
```bash
# GitHub (required)
export GITHUB_TOKEN="ghp_..."  # Needs: repo, workflow, codespace scopes

# Figma (Phase 2)
export FIGMA_ACCESS_TOKEN="..."
export FIGMA_TEAM_ID="..."
export FIGMA_PROJECT_ID="..."

# Amazon Product Advertising API (Phase 2)
export AMAZON_ACCESS_KEY="..."
export AMAZON_SECRET_KEY="..."
export AMAZON_PARTNER_TAG="..."
```

### Agent-Specific Keys
```bash
# Set per-agent keys (or use shared)
export PUCKFAIRY_API_KEY="$ANTHROPIC_API_KEY"
export DIPLO_API_KEY="$OPENAI_API_KEY"
export WARIA_API_KEY="$OPENAI_API_KEY"
# ... etc for all agents
```

---

## 📊 Hierarchies & Relationships

### Command Structure

```
User Interface (GUI - Athena A3)
        ↓
    Puckfairy (D1) ──────┐
        ↓                 │ Superior
    Bash (C1)             │
    Subordinate ──────────┘

    Gunash (C2) ──────┐
        ↓              │ Superior
    Clash (C3)         │
    Subordinate ───────┘
```

### Tool Ownership Flow

```
Phase 1 Initial:
  D1 Puckfairy: Neovim MCP
  D2 Diplo: GitHub + Narnia MCP
  D3 Waria: Fabric MCP

Phase 3 Transfer:
  D1 Puckfairy: [none] (delegates to Bash)
  ↓ TRANSFERS TO ↓
  C1 Bash: Neovim MCP ✓

  D2 Diplo: [caching/logging only]
  ↓ TRANSFERS TO ↓
  C2 Gunash: GitHub + Narnia MCP ✓

  C3 Clash: VSCode MCP (new) ✓
```

---

## 🌐 Network Architecture

### Triangular Communication

```
┌────────────────┐         SSH Tunnel         ┌────────────────┐
│ Local Machine  │◄─────────────────────────►│      VPS       │
│  Port: 9090    │       (bidirectional)      │   Port: 8080   │
└────────┬───────┘                            └───────┬────────┘
         │                                            │
         │ SSH Tunnel                     SSH Tunnel  │
         │ (bidirectional)              (bidirectional)
         │                                            │
         │         ┌────────────────────┐            │
         └────────►│ GitHub Codespaces  │◄───────────┘
                   │    Port: 7070      │
                   └────────────────────┘
```

### SSH Tunnel Commands

```bash
# Local → VPS
autossh -M 0 -N -L 8080:localhost:8080 -R 9090:localhost:9090 user@vps-ip &

# Codespaces → VPS
gh cs ssh -- -N -L 8080:localhost:8080 -R 7070:localhost:7070 user@vps-ip &

# Local → Codespaces (direct)
gh cs ssh -- -N -L 7070:localhost:7070 -R 9090:localhost:9090 &
```

---

## 📦 Installation Checklist

### System Requirements

**Minimum**:
- OS: Ubuntu 20.04+ / Debian 11+ / similar Linux
- CPU: 4 cores
- RAM: 8GB
- Storage: 50GB free
- Network: Stable internet connection

**Recommended**:
- OS: Ubuntu 24.04 LTS
- CPU: 8 cores
- RAM: 16GB
- Storage: 100GB SSD
- Network: Low-latency connection

### Software Stack

```bash
# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install base packages
sudo apt-get install -y \
  git curl wget \
  build-essential \
  python3 python3-pip python3-venv \
  golang-go \
  nodejs npm \
  redis-server \
  tmux screen \
  autossh \
  chromium-browser \
  libnss3 libxss1 libasound2

# Verify versions
python3 --version  # Should be 3.10+
go version         # Should be 1.21+
node --version     # Should be 18+
```

### GitHub CLI Setup

```bash
# Install GitHub CLI
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | \
  sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | \
  sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
sudo apt update
sudo apt install gh -y

# Authenticate
gh auth login
```

---

## 🚀 Quick Start Guide

### 1. Clone Repository

```bash
# On VPS
mkdir -p ~/librarian-agent-deploy
cd ~/librarian-agent-deploy
git clone https://github.com/josiehq/librarian-agent.git
cd librarian-agent
```

### 2. Setup Python Environment

```bash
# Create master venv (optional, or per-agent)
python3 -m venv ~/librarian-venv
source ~/librarian-venv/bin/activate
pip install --upgrade pip

# Install common dependencies
pip install anthropic openai requests asyncio websockets pydantic
```

### 3. Build Go Components

```bash
cd go/kernel
go mod download
go build -o mcp_server mcp_server.go types.go kirktower.go
go build -o kirktower kirktower.go types.go

cd ../cli
go build -o tower_cll tower_cll.go

# Verify builds
./mcp_server --version
./kirktower --version
./tower_cll --version
```

### 4. Setup Narnia (if not already done)

```bash
# Assuming Narnia is on local machine, sync to VPS
rsync -avz ~/DEV/Pythong/NARNIA/ user@vps-ip:~/narnia/

# On VPS, install Narnia
cd ~/narnia
./install.sh  # Or whatever the install process is
```

### 5. Start Phase 1 (Foundation)

```bash
# Start MCP server
cd ~/librarian-agent-deploy/librarian-agent/go/kernel
./mcp_server --port 8080 &

# Start D2 Diplo
cd ~/librarian-agent-deploy/librarian-agent/agents/D/Diplo
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
export DIPLO_API_KEY="$OPENAI_API_KEY"
python3 -m diplo.main --daemon --mode git-monitor &

# Start D3 Waria
cd ~/librarian-agent-deploy/librarian-agent/agents/D/Waria
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
export WARIA_API_KEY="$OPENAI_API_KEY"
python3 -m waria.main --daemon --mode builder &

# Start D1 Puckfairy (interactive)
cd ~/librarian-agent-deploy/librarian-agent/agents/D/Puckfairy
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
export PUCKFAIRY_API_KEY="$ANTHROPIC_API_KEY"
python3 -m puckfairy.main --mode terminal
```

---

## 📁 Complete Directory Structure

```
librarian-agent/
├── agents/
│   ├── A/
│   │   ├── Athena/         # A3 - GUI Agent
│   │   │   ├── brain/
│   │   │   │   └── rag_engine.py
│   │   │   ├── exemplar/
│   │   │   ├── profile/
│   │   │   │   └── api.py
│   │   │   └── tools/
│   │   ├── Josie/          # A2 - Orchestrator
│   │   │   ├── brain/
│   │   │   ├── exemplar/
│   │   │   ├── profile/
│   │   │   └── tools/
│   │   ├── Roark/          # A1 - Strategist
│   │   │   ├── brain/
│   │   │   ├── exemplar/
│   │   │   ├── profile/
│   │   │   └── tools/
│   │   ├── brain/          # A-class shared
│   │   ├── exemplar/
│   │   ├── profile/
│   │   └── tools/
│   ├── B/
│   │   ├── Concrete/       # B3 - Validator
│   │   ├── Kirktower/      # B4 - Infrastructure
│   │   ├── Raw/            # B1 - Scraper
│   │   ├── Vision/         # B2 - Designer
│   │   ├── brain/
│   │   ├── exemplar/
│   │   ├── profile/
│   │   └── tools/
│   ├── C/
│   │   ├── Bash/           # C1 - Automation
│   │   ├── Clash/          # C3 - Remote Editor
│   │   ├── Gunash/         # C2 - Git Control
│   │   ├── brain/
│   │   ├── exemplar/
│   │   ├── profile/
│   │   └── tools/
│   └── D/
│       ├── Diplo/          # D2 - Memory
│       ├── Puckfairy/      # D1 - User Interface
│       ├── Waria/          # D3 - Builder
│       ├── brain/
│       ├── exemplar/
│       ├── profile/
│       └── tools/
├── config/
├── docs/
│   ├── MASTER_DEPLOYMENT.md         # This file
│   ├── PHASE_1_D_RANK_DEPLOYMENT.md
│   ├── PHASE_2_B_RANK_DEPLOYMENT.md
│   ├── PHASE_3_C_RANK_DEPLOYMENT.md
│   └── PHASE_4_A_RANK_GUI.md
├── go/
│   ├── cli/
│   │   └── tower_cll.go
│   └── kernel/
│       ├── kirktower.go
│       ├── mcp_server.go
│       └── types.go
├── py/
│   ├── common/
│   ├── memory/
│   │   └── diplo.py
│   └── orchestration/
│       ├── c_loop.py
│       └── josie.py
├── scripts/
│   ├── QUICKSTART.sh
│   └── test_mcp.sh
├── main.py
├── setup.py
└── README.md
```

---

## 🔍 Verification & Testing

### Check Agent Status

```bash
# Query all agents
curl http://localhost:8080/api/agents | jq

# Check specific agent
curl http://localhost:8080/api/agents/D1 | jq

# View logs
curl http://localhost:8080/api/logs?agent=D2&limit=50 | jq
```

### Test Triangular Communication

```bash
# From local machine, test VPS
curl http://localhost:8080/api/ping

# From Codespaces, test VPS
curl http://localhost:8080/api/ping

# Check tunnel health
netstat -an | grep -E "8080|9090|7070"
```

### Test MCP Tools

```bash
# Test Neovim MCP
curl -X POST http://localhost:8080/api/tools/neovim-mcp/test

# Test GitHub MCP
curl -X POST http://localhost:8080/api/tools/github-narnia-mcp/test

# Test Fabric MCP
curl -X POST http://localhost:8080/api/tools/fabric-mcp/test
```

---

## 🎛️ Control & Monitoring

### tmux Session Layout

```bash
# Create master session
tmux new-session -d -s librarian

# Create windows
tmux new-window -t librarian:1 -n 'MCP Server'
tmux new-window -t librarian:2 -n 'D-Class'
tmux new-window -t librarian:3 -n 'B-Class'
tmux new-window -t librarian:4 -n 'C-Class'
tmux new-window -t librarian:5 -n 'A-Class'
tmux new-window -t librarian:6 -n 'Logs'

# Split D-Class window into 3 panes
tmux select-window -t librarian:2
tmux split-window -h
tmux split-window -v

# Attach
tmux attach-session -t librarian
```

### Systemd Services (Optional)

Create service files for agents to auto-start:

```bash
# /etc/systemd/system/librarian-mcp.service
[Unit]
Description=Librarian Agent MCP Server
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/home/your-user/librarian-agent-deploy/librarian-agent/go/kernel
ExecStart=/home/your-user/librarian-agent-deploy/librarian-agent/go/kernel/mcp_server --port 8080
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable: `sudo systemctl enable librarian-mcp && sudo systemctl start librarian-mcp`

---

## 🐛 Common Issues & Solutions

### Issue: Port already in use

```bash
# Find process using port 8080
lsof -i :8080

# Kill it
kill -9 <PID>

# Or use different port
./mcp_server --port 8081
```

### Issue: Agent won't start - API key invalid

```bash
# Verify key is set
echo $PUCKFAIRY_API_KEY

# Test key directly
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"claude-3-5-sonnet-20241022","max_tokens":10,"messages":[{"role":"user","content":"test"}]}'
```

### Issue: SSH tunnel drops

```bash
# Use autossh with monitoring
autossh -M 0 -o "ServerAliveInterval 30" -o "ServerAliveCountMax 3" \
  -N -L 8080:localhost:8080 -R 9090:localhost:9090 user@vps-ip

# Or use tmux/screen to keep alive
screen -dmS ssh_tunnel autossh -M 0 -N -L 8080:localhost:8080 user@vps-ip
```

### Issue: Out of memory

```bash
# Check memory usage
free -h

# Identify memory hogs
ps aux --sort=-%mem | head -10

# Restart agents selectively
# Or increase VPS RAM
```

### Issue: Logs filling disk

```bash
# Check disk usage
df -h

# Rotate logs manually
cd ~/librarian-agent-deploy/logs
find . -name "*.log" -mtime +7 -exec gzip {} \;

# Or configure Diplo's log rotation in Phase 2+
```

---

## 📚 Additional Resources

### Official Documentation
- **MCP Specification**: [MCP_ARCHITECTURE.md](./MCP_ARCHITECTURE.md)
- **Quick Reference**: [MCP_QUICK_REFERENCE.sh](./MCP_QUICK_REFERENCE.sh)
- **Integration Notes**: [INTEGRATION_NOTES.md](./INTEGRATION_NOTES.md)
- **Changes Summary**: [CHANGES_SUMMARY.md](./CHANGES_SUMMARY.md)

### External Links
- OpenAI API: https://platform.openai.com/docs
- Anthropic Claude API: https://docs.anthropic.com/
- GitHub REST API: https://docs.github.com/en/rest
- Figma API: https://www.figma.com/developers/api
- Playwright: https://playwright.dev/
- ChromaDB: https://docs.trychroma.com/

### Community & Support
- GitHub Issues: https://github.com/josiehq/librarian-agent/issues
- Discord: (if available)
- Email: (if applicable)

---

## 🎓 Learning Path

### For New Users

1. **Start with Phase 1**: Understand the D-class foundation
2. **Read MCP docs**: Understand how tools work
3. **Test locally first**: Before VPS deployment
4. **One phase at a time**: Don't rush to Phase 4
5. **Monitor logs**: Understand what agents are doing

### For Developers

1. **Review architecture**: Understand hierarchies
2. **Study agent profiles**: See `/agents/*/profile/api.py`
3. **Explore MCP tools**: Check `go/kernel/mcp_server.go`
4. **Customize agents**: Modify brain/exemplar/tools
5. **Contribute**: Fork, improve, PR

### For Advanced Users

1. **Dynamic agent spawning**: Implement new agent creation
2. **Container orchestration**: Migrate to Docker/K8s
3. **Multi-user support**: Add authentication/authorization
4. **Plugin system**: Create modular tool plugins
5. **Scale horizontally**: Deploy across multiple VPS

---

## 🏆 Success Metrics

### Phase 1 Success
- ✅ 3 D-class agents running
- ✅ Triangle communication established
- ✅ Concurrent build test passed
- ✅ MCP server operational

### Phase 2 Success
- ✅ 7 agents running (D + B classes)
- ✅ Visual Sovereign tested
- ✅ Diplo caching operational
- ✅ 3 specialized MCP tools integrated

### Phase 3 Success
- ✅ 10 agents running (D + B + C classes)
- ✅ Hierarchies established
- ✅ Tool ownership transferred
- ✅ Startup automation working

### Phase 4 Success
- ✅ 13 agents running (full swarm)
- ✅ GUI operational
- ✅ C2 server functional
- ✅ RAG intelligence active

---

## 📞 Contact & Support

**Project Maintainer**: josiehq  
**Repository**: https://github.com/josiehq/librarian-agent  
**License**: (Specify license)  

For issues, questions, or contributions, please open an issue on GitHub.

---

## 🎉 Congratulations!

You now have a complete reference for deploying the Librarian Agent system. Follow the phases sequentially, test thoroughly at each checkpoint, and build your way to a fully operational 13-agent swarm with GUI.

**Remember**: This isn't even our final form. The system is designed to evolve, scale, and improve over time.

**Good luck, and happy agent coordination!** 🚀
