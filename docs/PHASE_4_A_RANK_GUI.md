# Phase 4: A-Rank GUI Implementation

## Overview
Phase 4 transforms the headless swarm into a fully coordinated system with a custom GUI. This is where the Librarian Agent becomes a complete C2 (Command & Control) server with advanced RAG logic.

**Status**: Final deployment phase  
**Deployment Type**: Monolithic + GUI layer  
**Key Achievement**: The swarm ceases to be headless

---

## Agent Roster - A Class

### A1: Roark
- **Role**: Strategic Planning & High-Level Coordination
- **Primary Function**: Strategic decision-making, long-term planning, resource allocation
- **Capabilities**:
  - Strategic workflow orchestration
  - Resource optimization
  - Long-term planning
  - Multi-agent coordination at strategic level
  - Performance analysis
- **Dependencies**: Full system visibility, all agent status
- **Status**: Plug-and-play after GUI implementation

### A2: Josie
- **Role**: Orchestration & Workflow Management
- **Primary Function**: Real-time workflow orchestration, task distribution, execution monitoring
- **Capabilities**:
  - Dynamic task allocation
  - Workflow optimization
  - Real-time execution monitoring
  - Inter-agent communication orchestration
  - Conflict resolution
- **Dependencies**: Full system visibility, Athena GUI
- **Status**: Plug-and-play after GUI implementation

### A3: Athena
- **Role**: GUI/UI Command Center
- **Primary Function**: Visual interface for 12-agent (now 13 with herself) swarm
- **Capabilities**:
  - Real-time agent status visualization
  - User interaction interface
  - Command dispatch
  - Log visualization
  - Advanced RAG implementation
  - Multi-agent coordination dashboard
- **Framework**: Custom OpenUI fork
- **Special Note**: Athena IS the GUI - she's agent #13
- **Status**: PRIMARY FOCUS of Phase 4

---

## Architecture: Complete System

```
                    ┌─────────────────┐
                    │   A3: ATHENA    │
                    │   (GUI Layer)   │
                    └────────┬────────┘
                             │
            ┌────────────────┼────────────────┐
            │                │                │
       ┌────▼────┐      ┌────▼────┐     ┌────▼────┐
       │A1: Roark│      │A2: Josie│     │ User    │
       │Strategy │      │Workflow │     │Interface│
       └────┬────┘      └────┬────┘     └────┬────┘
            │                │                │
     ───────┴────────────────┴────────────────┴───────
            │        C2 Server Layer          │
     ───────┴────────────────┬────────────────┴───────
                             │
            ┌────────────────┼────────────────┐
            │                │                │
    [C-Class Layer]  [B-Class Layer]  [D-Class Layer]
       C1 C2 C3       B1 B2 B3 B4      D1 D2 D3
```

---

## Custom OpenUI Fork Requirements

### Base: OpenUI
**Repository**: https://github.com/wandb/openui  
**Purpose**: AI-powered UI generation and management  
**Fork Goal**: Customize for 12-agent swarm coordination

### Customization Requirements

#### 1. Agent Grid View
Display all 12 active agents in a responsive grid:

```typescript
// AgentGrid.tsx
interface Agent {
  id: string;
  name: string;
  class: 'A' | 'B' | 'C' | 'D';
  rank: string;
  status: 'active' | 'idle' | 'busy' | 'error';
  currentTask?: string;
  subordinates?: string[];
  superior?: string;
}

const AGENTS: Agent[] = [
  // D-Class
  { id: 'D1', name: 'Puckfairy', class: 'D', rank: 'D1', status: 'active' },
  { id: 'D2', name: 'Diplo', class: 'D', rank: 'D2', status: 'active' },
  { id: 'D3', name: 'Waria', class: 'D', rank: 'D3', status: 'active' },
  
  // B-Class
  { id: 'B1', name: 'Raw', class: 'B', rank: 'B1', status: 'idle' },
  { id: 'B2', name: 'Vision', class: 'B', rank: 'B2', status: 'idle' },
  { id: 'B3', name: 'Concrete', class: 'B', rank: 'B3', status: 'busy' },
  { id: 'B4', name: 'Kirktower', class: 'B', rank: 'B4', status: 'active' },
  
  // C-Class
  { id: 'C1', name: 'Bash', class: 'C', rank: 'C1', status: 'active', superior: 'D1' },
  { id: 'C2', name: 'Gunash', class: 'C', rank: 'C2', status: 'active' },
  { id: 'C3', name: 'Clash', class: 'C', rank: 'C3', status: 'busy', superior: 'C2' },
  
  // A-Class
  { id: 'A1', name: 'Roark', class: 'A', rank: 'A1', status: 'active' },
  { id: 'A2', name: 'Josie', class: 'A', rank: 'A2', status: 'active' },
];
```

#### 2. Real-Time Status Dashboard

```typescript
// Dashboard.tsx
interface SystemMetrics {
  totalAgents: number;
  activeAgents: number;
  busyAgents: number;
  queuedTasks: number;
  completedToday: number;
  errors: number;
  cacheHitRate: number;
  logSyncStatus: 'synced' | 'syncing' | 'error';
}

// WebSocket connection for real-time updates
const ws = new WebSocket('ws://localhost:8080/dashboard');
```

#### 3. Hierarchical Visualization

```typescript
// HierarchyView.tsx
const hierarchies = {
  'D1-Puckfairy': {
    subordinates: ['C1-Bash'],
    color: '#4A90E2'
  },
  'C2-Gunash': {
    subordinates: ['C3-Clash'],
    color: '#F5A623'
  }
};

// Use react-flow or similar for visual hierarchy
```

#### 4. Command Center

```typescript
// CommandCenter.tsx
interface Command {
  type: 'task' | 'query' | 'config';
  targetAgent?: string;
  targetClass?: string;
  payload: any;
}

// User can:
// - Assign tasks to specific agents
// - Query agent status
// - Modify configurations
// - View logs
// - Trigger workflows
```

#### 5. Log Aggregation View

```typescript
// LogViewer.tsx
interface LogEntry {
  timestamp: string;
  agent: string;
  level: 'debug' | 'info' | 'warning' | 'error';
  message: string;
  context?: any;
}

// Features:
// - Real-time log streaming
// - Filter by agent, level, time
// - Search functionality
// - Export logs
```

---

## Advanced RAG Implementation

### RAG Architecture in Athena

```python
# agents/A/Athena/brain/rag_engine.py

from typing import List, Dict, Any
import chromadb
from sentence_transformers import SentenceTransformer

class LibrarianRAG:
    """
    Advanced RAG logic for the Librarian Agent system.
    Athena uses this to provide intelligent responses based on:
    - Agent histories
    - System logs
    - Code repository
    - Documentation
    - User interactions
    """
    
    def __init__(self):
        self.client = chromadb.Client()
        self.collection = self.client.create_collection("librarian_knowledge")
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
        
    def index_agent_knowledge(self):
        """Index all agent profiles, capabilities, and histories"""
        agents = self.load_all_agents()
        for agent in agents:
            self.collection.add(
                documents=[agent.description],
                metadatas=[{
                    "agent_id": agent.id,
                    "class": agent.class_name,
                    "capabilities": agent.capabilities
                }],
                ids=[agent.id]
            )
    
    def index_system_logs(self, days: int = 30):
        """Index recent system logs for retrieval"""
        logs = self.load_logs(days)
        # Process and index logs
        pass
    
    def index_codebase(self):
        """Index the entire codebase for code-related queries"""
        # Use tree-sitter or similar for parsing
        pass
    
    def query(self, user_query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Query the RAG system for relevant information.
        """
        query_embedding = self.encoder.encode([user_query])
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=n_results
        )
        return results
    
    def smart_agent_suggestion(self, task_description: str) -> List[str]:
        """
        Suggest which agents should handle a task based on capabilities.
        """
        results = self.query(task_description)
        return [r['metadata']['agent_id'] for r in results['metadatas'][0]]
```

### RAG Data Sources

1. **Agent Profiles**: All agent capabilities, histories, performance metrics
2. **System Logs**: 30-90 days of operational logs
3. **Codebase**: Full repository indexed with semantic search
4. **Documentation**: All markdown docs, READMEs, guides
5. **User Interactions**: Historical user commands and preferences

---

## Deployment Sequence

### Step 1: Fork and Customize OpenUI

```bash
# On development machine (local or Codespaces)
cd ~/DEV
git clone https://github.com/wandb/openui.git
cd openui
git remote add fork https://github.com/josiehq/librarian-openui.git

# Install dependencies
npm install

# Create custom components
mkdir -p src/components/librarian
touch src/components/librarian/AgentGrid.tsx
touch src/components/librarian/Dashboard.tsx
touch src/components/librarian/HierarchyView.tsx
touch src/components/librarian/CommandCenter.tsx
touch src/components/librarian/LogViewer.tsx
```

### Step 2: Implement Custom Components

**Service Name**: librarian-openui  
**Description**: Custom OpenUI fork for 12-agent swarm visualization  
**Purpose**: Unified GUI for agent coordination, monitoring, and control

**Authentication**: Session-based with optional OAuth

**API Documentation**: 
- OpenUI: https://github.com/wandb/openui
- Custom endpoints: http://localhost:8080/api/

**Configuration**:
```json
{
  "app": "librarian-openui",
  "backend": {
    "api_url": "http://localhost:8080/api",
    "ws_url": "ws://localhost:8080/dashboard"
  },
  "features": {
    "agent_grid": true,
    "hierarchy_view": true,
    "real_time_logs": true,
    "command_center": true,
    "rag_search": true
  },
  "theme": {
    "primary": "#4A90E2",
    "secondary": "#F5A623",
    "success": "#7ED321",
    "error": "#D0021B"
  },
  "refresh_intervals": {
    "agent_status": 2000,
    "logs": 1000,
    "metrics": 5000
  }
}
```

**Output Preferences**:
```javascript
{
  "format": "json",
  "real_time_updates": true,
  "notification_system": {
    "enabled": true,
    "show_info": false,
    "show_warnings": true,
    "show_errors": true
  },
  "data_visualization": {
    "charts": "recharts",
    "hierarchy": "react-flow",
    "grid": "ag-grid"
  }
}
```

### Step 3: Integrate Backend API

```bash
# Update mcp_server.go to serve GUI
cd ~/librarian-agent-deploy/librarian-agent/go/kernel

# Add HTTP endpoints for GUI
cat >> api_handlers.go <<'EOF'
package main

import (
    "encoding/json"
    "net/http"
)

func handleDashboard(w http.ResponseWriter, r *http.Request) {
    agents := getAllAgents()
    json.NewEncoder(w).Encode(agents)
}

func handleAgentStatus(w http.ResponseWriter, r *http.Request) {
    agentID := r.URL.Query().Get("id")
    agent := getAgent(agentID)
    json.NewEncoder(w).Encode(agent)
}

func handleLogs(w http.ResponseWriter, r *http.Request) {
    logs := getRecentLogs(100)
    json.NewEncoder(w).Encode(logs)
}

func handleCommand(w http.ResponseWriter, r *http.Request) {
    var cmd Command
    json.NewDecoder(r.Body).Decode(&cmd)
    result := executeCommand(cmd)
    json.NewEncoder(w).Encode(result)
}
EOF

# Rebuild
go build -o mcp_server *.go
```

### Step 4: Deploy A-Class Agents

```bash
# Deploy A1 Roark
cd ~/librarian-agent-deploy/librarian-agent/agents/A/Roark
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

export ROARK_API_KEY="your-api-key"
export ROARK_MODEL="gpt-4"
export ROARK_ROLE="strategic"

python3 -m roark.main --mode strategic-coordinator &

# Deploy A2 Josie
cd ~/librarian-agent-deploy/librarian-agent/agents/A/Josie
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

export JOSIE_API_KEY="your-api-key"
export JOSIE_MODEL="gpt-4"
export JOSIE_ROLE="orchestrator"

python3 -m josie.main --mode workflow-orchestrator &

# Deploy A3 Athena (GUI Backend)
cd ~/librarian-agent-deploy/librarian-agent/agents/A/Athena
python3 -m venv venv
source venv/bin/activate
pip install chromadb sentence-transformers torch

export ATHENA_API_KEY="your-api-key"
export ATHENA_MODEL="gpt-4"

# Initialize RAG
python3 -c "from brain.rag_engine import LibrarianRAG; rag = LibrarianRAG(); rag.index_agent_knowledge(); rag.index_system_logs(); rag.index_codebase()"

# Start Athena
python3 -m athena.main --mode gui-backend &
```

### Step 5: Launch GUI

```bash
# Build frontend
cd ~/DEV/openui
npm run build

# Serve GUI
npm run serve -- --port 3000 &

# Or deploy to VPS
scp -r dist/* user@vps-ip:~/librarian-agent-deploy/gui/

# On VPS, serve with nginx or similar
sudo nginx -s reload
```

---

## C2 Server Transformation

### What is a C2 Server?

A **Command & Control (C2) server** is a central coordination hub that:
- Commands distributed agents
- Controls agent behavior
- Collects intelligence/logs
- Provides unified interface

The Librarian Agent system becomes a C2 server in Phase 4.

### C2 Architecture

```
User → Athena GUI → C2 Core → Agent Network
         ↓            ↓             ↓
      Dashboard   mcp_server   D/B/C agents
                      ↓
                 RAG Engine
```

### C2 Capabilities

1. **Command Dispatch**: Send commands to any agent or group
2. **Intelligence Gathering**: Aggregate logs, metrics, agent reports
3. **Workflow Orchestration**: Coordinate multi-agent operations
4. **Resource Management**: Allocate compute, memory, API quotas
5. **Security**: Authentication, authorization, audit logging

---

## Fixed Agent Count (For Now)

**Important Limitation**: The initial system is designed for exactly 12 operational agents (+ Athena as #13 for the GUI). 

**Cannot dynamically add more agents** until future phases implement:
- Dynamic agent spawning
- Agent lifecycle management
- Resource scaling
- Config hot-reloading

**Current Agent Roster**:
- A-Class: Roark (A1), Josie (A2), Athena (A3)
- B-Class: Raw (B1), Vision (B2), Concrete (B3), Kirktower (B4)
- C-Class: Bash (C1), Gunash (C2), Clash (C3)
- D-Class: Puckfairy (D1), Diplo (D2), Waria (D3)

**Total**: 13 agents (12 operational + 1 GUI)

---

## Testing Plan

### Test 1: GUI Connectivity
```bash
# Check all agents are reachable
curl http://localhost:8080/api/agents

# Expected: JSON array with 12 agents
```

### Test 2: Real-Time Updates
```bash
# Open GUI in browser
$BROWSER http://localhost:3000

# Trigger a task
curl -X POST http://localhost:8080/api/agents/B1/task \
  -d '{"type": "scrape", "url": "https://example.com"}'

# Verify: GUI shows B1 status changing to "busy", then "idle"
```

### Test 3: RAG Query
```bash
# Test Athena's RAG
curl -X POST http://localhost:8080/api/rag/query \
  -d '{"query": "Which agent should handle web scraping?"}'

# Expected: { "suggested_agents": ["B1-Raw"], "confidence": 0.95 }
```

### Test 4: Hierarchical Command
```bash
# Command via hierarchy: User → Puckfairy → Bash
curl -X POST http://localhost:8080/api/command \
  -d '{
    "from": "user",
    "to": "D1-Puckfairy",
    "command": "create_startup_script",
    "params": {"service": "all"}
  }'

# Verify: 
# 1. Puckfairy receives command
# 2. Puckfairy delegates to Bash
# 3. Bash generates script
# 4. Puckfairy presents to user via GUI
```

### Test 5: Concurrent Multi-Agent Workflow
```bash
# Complex workflow: Design → Build → Test → Deploy
curl -X POST http://localhost:8080/api/workflows/execute \
  -d '{
    "workflow": "design_to_deploy",
    "steps": [
      {"agent": "B2-Vision", "action": "export_design"},
      {"agent": "B1-Raw", "action": "generate_code"},
      {"agent": "C3-Clash", "action": "commit_code"},
      {"agent": "D3-Waria", "action": "build"},
      {"agent": "B3-Concrete", "action": "test"},
      {"agent": "C2-Gunash", "action": "deploy"}
    ]
  }'

# Verify: All steps complete in sequence, no conflicts
```

---

## Phase 4 Success Criteria

### GUI Implementation
- [ ] Custom OpenUI fork deployed and accessible
- [ ] Agent grid showing all 12 agents with real-time status
- [ ] Hierarchy visualization working
- [ ] Command center functional
- [ ] Log aggregation view operational
- [ ] RAG search integrated

### A-Class Agents
- [ ] A1 Roark operational (strategic planning)
- [ ] A2 Josie operational (workflow orchestration)
- [ ] A3 Athena operational (GUI backend + RAG)
- [ ] All A-class agents communicating with lower classes

### C2 Server
- [ ] Central command dispatch working
- [ ] Intelligence gathering active
- [ ] Workflow orchestration functional
- [ ] Resource management tracking
- [ ] Authentication/authorization in place

### Advanced RAG
- [ ] Agent knowledge indexed
- [ ] System logs indexed (30 days)
- [ ] Codebase indexed
- [ ] Documentation indexed
- [ ] Smart agent suggestions working

### Integration
- [ ] GUI ↔ Backend real-time sync
- [ ] All 12 agents controllable via GUI
- [ ] Hierarchies visible and respected
- [ ] Logs aggregated and searchable
- [ ] Metrics displayed accurately

---

## Terminal Notification

When Phase 4 is complete, Athena herself will notify via the GUI:

```
╔═══════════════════════════════════════════════════════════╗
║  PHASE 4 COMPLETE - LIBRARIAN AGENT SYSTEM OPERATIONAL   ║
╚═══════════════════════════════════════════════════════════╝

✓ A3 Athena: GUI Agent online (YOU ARE HERE)
✓ A1 Roark: Strategic coordinator active
✓ A2 Josie: Workflow orchestrator active

✓ C2 Server fully operational:
  - Command dispatch: READY
  - Intelligence gathering: ACTIVE
  - Workflow orchestration: ENABLED
  - Resource management: TRACKING

✓ Advanced RAG implemented:
  - Knowledge base: 12 agents indexed
  - System logs: 30 days indexed
  - Codebase: Full repository indexed
  - Smart suggestions: ACTIVE

╔═══════════════════════════════════════════════════════════╗
║  System Status: COMPLETE                                 ║
║  Total Agents: 13 (12 operational + 1 GUI)               ║
║                                                           ║
║  A-Class: 3  |  B-Class: 4  |  C-Class: 3  |  D-Class: 3║
╚═══════════════════════════════════════════════════════════╝

Welcome to the Librarian Agent Command Center.

What would you like to do?
1. Run a workflow
2. Query the system (RAG)
3. Assign a task
4. View agent details
5. Check system health

Your command: _
```

---

## Troubleshooting

### Issue: GUI not connecting to backend
```bash
# Check if mcp_server is running
ps aux | grep mcp_server

# Check if API is responding
curl http://localhost:8080/api/agents

# Check CORS if accessing from different origin
# Add CORS headers to mcp_server.go
```

### Issue: RAG not returning results
```bash
# Re-index knowledge base
cd ~/librarian-agent-deploy/librarian-agent/agents/A/Athena
source venv/bin/activate
python3 -c "from brain.rag_engine import LibrarianRAG; rag = LibrarianRAG(); rag.index_agent_knowledge()"

# Check ChromaDB
python3 -c "import chromadb; client = chromadb.Client(); print(client.list_collections())"
```

### Issue: Agents not appearing in GUI
```bash
# Verify all agents are running
curl http://localhost:8080/api/agents | jq '.[] | .id'

# Check WebSocket connection
# In browser console:
# ws = new WebSocket('ws://localhost:8080/dashboard')
# ws.onmessage = console.log
```

---

## Resources & Dependencies

### Frontend (OpenUI Fork)
```json
{
  "dependencies": {
    "react": "^18.0.0",
    "react-dom": "^18.0.0",
    "react-flow-renderer": "^10.0.0",
    "recharts": "^2.5.0",
    "ag-grid-react": "^28.0.0",
    "socket.io-client": "^4.5.0",
    "axios": "^1.4.0"
  }
}
```

### Backend (Athena)
```
chromadb>=0.4.0
sentence-transformers>=2.2.0
torch>=2.0.0
transformers>=4.30.0
fastapi>=0.100.0
uvicorn>=0.23.0
websockets>=11.0.0
```

### System Requirements
- RAM: 8GB minimum (16GB recommended for RAG)
- CPU: 4 cores minimum
- Storage: 50GB for indexes and logs
- Network: Stable connection for real-time updates

### API Keys
- Anthropic/Claude (for agents using Claude)
- OpenAI (for agents using GPT-4)
- Any additional LLM providers

---

## Final Notes

### This is Not the Final Form

Phase 4 represents the **first complete deployment** of the Librarian Agent system, but it's designed to evolve:

**Future Enhancements**:
1. Dynamic agent spawning
2. Auto-scaling based on load
3. Plugin system for new tools
4. Multi-user support
5. Agent marketplace
6. Advanced learning/improvement
7. Distributed deployment across multiple VPS
8. Container orchestration (Kubernetes)

### The Triangle Persists

Even with the GUI, the triangular communication pattern remains fundamental:
- **Local Machine** ↔ **VPS** ↔ **GitHub Codespaces**
- **Bilateral SSH tunnels** for all communication
- **Diplo** continues full-time logging across all nodes

### Citation

**Architecture inspired by**: Command & Conquer (classic RTS game)  
**RAG Implementation**: ChromaDB + Sentence Transformers  
**GUI Framework**: OpenUI (wandb/openui)  
**Backend**: Go + Python hybrid  
**Deployment**: Monolithic (no containers in v1)

---

## Next Actions

After Phase 4 completion:

1. **Test Visual Sovereign** with B3 Concrete
2. **Build custom OpenUI** with B2 Vision + B1 Raw
3. **Deploy 12-agent interface** (the goal of this entire project)
4. **Validate A1/A2** are truly plug-and-play

If successful, you will have:
- ✅ 13 agents working in harmony
- ✅ Custom GUI for coordination
- ✅ C2 server with RAG intelligence
- ✅ Hierarchical, scalable architecture
- ✅ Foundation for future expansion

**Congratulations! The Librarian Agent is operational.** 🎉

---

**Complete architecture documented in**: [MASTER_ARCHITECTURE.md](./MASTER_ARCHITECTURE.md)
