# MCP Integration Master Plan
**Version:** 1.0  
**Date:** December 17, 2025  
**Status:** Pre-Implementation

---

## Executive Summary

This document outlines the complete integration of 11 MCP tools into the Librarian Agent swarm system. The integration follows a **nucleus-first** approach: Golang MCP server expansion → Agent brain logic → Python orchestration enhancement.

---

## Phase Structure

### **PHASE 0: Golang MCP Server Expansion** ✅ START HERE
**Objective:** Expand `mcp_server.go` from 3 tools to 14 tools  
**Rationale:** Go is the nucleus; all Python agents depend on this

**Current State:**
- 3 tools: `container_exec`, `memory_commit`, `fs_write_guarded`
- Basic JSON-RPC 2.0 handler
- Diplo logging pipeline
- Waria audit hooks

**New Tools to Add:**
1. **fabric_execute** (D3 Waria) - Fabric AI prompts/patterns
2. **nvim_lsp** (D1→C1 transfer) - Neovim LSP operations
3. **github_api** (D2→C2 transfer) - GitHub API operations
4. **terminal_exec** (D1 Puckfairy) - Terminal command execution
5. **figma_api** (B2 Vision) - Figma design operations
6. **browser_navigate** (B1 Raw) - Browser automation
7. **web_crawl** (B1 Raw) - Web scraping
8. **amazon_api** (B3 Concrete) - Amazon services
9. **agentify_orchestrate** (Kirktower B4) - Meta-orchestration
10. **narnia_execute** (To be integrated) - Narnia framework
11. **visual_sovereign** (To be integrated) - Visual Sovereign testing

**Agent-Tool Ownership Matrix:**
```
D1 Puckfairy    → terminal_exec, nvim_lsp (phase 1)
D2 Diplo        → memory_commit, github_api (phase 1)
D3 Waria        → fabric_execute
B1 Raw          → browser_navigate, web_crawl
B2 Vision       → figma_api
B3 Concrete     → amazon_api
B4 Kirktower    → agentify_orchestrate
C1 Bash         → nvim_lsp (phase 3 transfer from D1)
C2 Gunash       → github_api (phase 3 transfer from D2)
C3 Clash        → container_exec
```

**Deliverables:**
- [ ] `go/kernel/mcp_tools.go` - New file with all 11 tool implementations
- [ ] Update `mcp_server.go` `registerTools()` to include all tools
- [ ] Add tool-specific audit hooks for Waria
- [ ] Create `go/kernel/mcp_types.go` for tool request/response types
- [ ] Tool authorization matrix (which agent can call which tool)

---

### **PHASE 1: Agent Brain Logic** 
**Objective:** Create reasoning engines for all 13 agents in their `/brain/` folders

**Current State:**
- All `/brain/` folders are empty
- Persona definitions exist in `/profile/persona.py`
- Generic tool rules exist in `/tools/rules.py`

**Deliverables:**
- [ ] Create `brain/reasoning.py` for each agent with:
  - `think()` - Core reasoning function
  - `plan()` - Task breakdown
  - `reflect()` - Self-evaluation
  - `escalate()` - Hierarchy escalation logic
- [ ] Create `brain/state.py` for agent state management
- [ ] Create `brain/memory.py` for agent-specific memory

**Agent-Specific Brain Requirements:**
- **A1 Roark:** Synthesis logic, architectural critique, 4-question framework
- **A2 Josie:** Skeleton generation, consensus protocol, escalation logic
- **A3 Athena:** RAG query logic, ChromaDB interface, context injection
- **B1 Raw:** Divergent ideation (no filtering)
- **B2 Vision:** Conceptual synthesis, confidence calibration
- **B3 Concrete:** Feasibility auditing, constraint checking
- **B4 Kirktower:** Process monitoring, conflict detection, emergency stops
- **C1 Clash:** Implementation execution, test scaffolding
- **C2 Bash:** Script generation (no execution)
- **C3 Gunash:** Dependency forecasting, structural guards
- **D1 Puckfairy:** Command execution logic, environment management
- **D2 Diplo:** Mediation logic, conflict resolution
- **D3 Waria:** Reasoning horizon monitoring, drift detection

---

### **PHASE 2: Agent-MCP Integration**
**Objective:** Connect agent brains to MCP tools via updated `rules.py`

**Current State:**
- Generic `rules.py` templates with placeholder tool lists
- No actual tool authorization logic

**Deliverables:**
- [ ] Update each agent's `tools/rules.py` with:
  - Authorized MCP tool list (from ownership matrix)
  - Tool-specific parameter builders
  - Response parsers for each tool
  - Error handling for MCP failures
- [ ] Create `tools/mcp_client.py` - Shared MCP client for all agents
- [ ] Tool permission enforcement in Go server

---

### **PHASE 3: Python Orchestration Enhancement**
**Objective:** Integrate MetaGPT + LlamaIndex alongside AutoGen

**Current State:**
- AutoGen scaffolding in `c_loop.py`
- Basic Josie orchestration in `josie.py`
- LlamaIndex in `setup.py` but not implemented

**Deliverables:**
- [ ] Create `py/orchestration/metagpt_bridge.py`:
  - MetaGPT SOP (Standard Operating Procedure) definitions
  - Role-based agent coordination
  - Hierarchical task decomposition
- [ ] Create `py/orchestration/llama_index_rag.py`:
  - ChromaDB vector store setup
  - Document indexing pipeline
  - Semantic search for Athena (A3)
- [ ] Update `josie.py` to coordinate AutoGen + MetaGPT
- [ ] Create `py/orchestration/phase_controller.py`:
  - Phase transitions (D→B→C→A)
  - Tool ownership transfers
  - Checkpoint validation

---

### **PHASE 4: Integration Testing & Validation**
**Objective:** End-to-end testing of all components

**Deliverables:**
- [ ] Unit tests for each MCP tool
- [ ] Integration tests for agent→MCP communication
- [ ] Phase transition tests
- [ ] Tool ownership transfer tests
- [ ] Consensus protocol tests (Josie + Gunash + Vision + Diplo)
- [ ] Emergency stop tests (Kirktower)

---

## Critical Dependencies

### External MCP Servers
These must be installed/configured:

```bash
# Fabric
cd /opt/mcp && git clone https://github.com/danielmiessler/Fabric.git

# Figma MCP
npm install -g @mohammeduvaiz/figma-mcp-server

# Nvim LSP MCP
npm install -g nvim-lsp-mcp

# Browser MCP
npm install -g @bytedance/browser-mcp

# Crawl MCP
npm install -g @walksoda/crawl-mcp

# Terminal MCP
npm install -g @dillip285/mcp-terminal

# GitHub MCP
npm install -g @github/github-mcp-server

# Amazon MCP
cd /opt/mcp && git clone https://github.com/r123singh/amazon-mcp-server.git

# Agentify MCP
npm install -g @gargoyle92/agentify-mcp
```

### Python Dependencies
Add to `setup.py`:
```python
install_requires=[
    # Existing
    "httpx>=0.24.0",
    "flask>=2.3.0",
    "pyautogen>=0.2.0",
    "llama-index>=0.9.0",
    "llama-index-core>=0.1.0",
    
    # NEW
    "metagpt>=0.7.0",
    "chromadb>=0.4.0",
    "sentence-transformers>=2.2.0",
    "beautifulsoup4>=4.12.0",
    "selenium>=4.15.0",
    "playwright>=1.40.0",
]
```

---

## Tool Implementation Specifications

### 1. fabric_execute
```go
// Executes Fabric AI patterns/prompts
// Owner: D3 Waria
// Args: pattern (string), input (string)
// Returns: Fabric output (string)
```

### 2. nvim_lsp
```go
// Neovim LSP operations (hover, definition, references)
// Owner: D1→C1 (transfers in Phase 3)
// Args: operation (string), file (string), position (line, col)
// Returns: LSP response (json)
```

### 3. github_api
```go
// GitHub API operations (issues, PRs, commits)
// Owner: D2→C2 (transfers in Phase 3)
// Args: operation (string), repo (string), params (map)
// Returns: GitHub API response (json)
```

### 4. terminal_exec
```go
// Direct terminal command execution
// Owner: D1 Puckfairy ONLY
// Args: command (string), cwd (string)
// Returns: stdout + stderr (string)
// Security: Restricted to Puckfairy agent_id
```

### 5. figma_api
```go
// Figma API operations (read designs, export assets)
// Owner: B2 Vision
// Args: operation (string), file_key (string), params (map)
// Returns: Figma data (json)
```

### 6. browser_navigate
```go
// Browser automation via Playwright/Selenium
// Owner: B1 Raw
// Args: url (string), actions ([]action)
// Returns: page_content (html), screenshot (base64)
```

### 7. web_crawl
```go
// Web scraping and crawling
// Owner: B1 Raw
// Args: start_url (string), depth (int), selectors ([]string)
// Returns: crawled_data (json)
```

### 8. amazon_api
```go
// Amazon services (S3, EC2, etc.)
// Owner: B3 Concrete
// Args: service (string), operation (string), params (map)
// Returns: AWS response (json)
```

### 9. agentify_orchestrate
```go
// Meta-orchestration for multi-agent coordination
// Owner: B4 Kirktower
// Args: agents ([]string), task (string), mode (string)
// Returns: orchestration_result (json)
```

### 10-11. narnia_execute, visual_sovereign
```go
// To be specified when loaded
```

---

## Security & Authorization Model

### Agent Authorization Matrix (in Go)
```go
var AgentToolPermissions = map[string][]string{
    "D1_Puckfairy": {"terminal_exec", "nvim_lsp"},
    "D2_Diplo":     {"memory_commit", "github_api"},
    "D3_Waria":     {"fabric_execute"},
    "B1_Raw":       {"browser_navigate", "web_crawl"},
    "B2_Vision":    {"figma_api"},
    "B3_Concrete":  {"amazon_api"},
    "B4_Kirktower": {"agentify_orchestrate"},
    "C1_Bash":      {"nvim_lsp"}, // After Phase 3 transfer
    "C2_Gunash":    {"github_api"}, // After Phase 3 transfer
    "C3_Clash":     {"container_exec"},
}
```

### Permission Check Function
```go
func (s *MCPServer) checkPermission(agentID string, toolName string) bool {
    allowedTools, exists := AgentToolPermissions[agentID]
    if !exists {
        return false // Unknown agent
    }
    for _, tool := range allowedTools {
        if tool == toolName {
            return true
        }
    }
    return false // Tool not authorized for this agent
}
```

---

## Implementation Order (Execution Plan)

### Week 1: Golang Nucleus
1. Create `mcp_tools.go` with all 11 tool stubs
2. Implement authorization matrix
3. Add tools to `registerTools()`
4. Update `ServeHTTP()` to check permissions before execution
5. Test with curl/httpie

### Week 2: Agent Brains
6. Implement D-class brains (Puckfairy, Diplo, Waria)
7. Implement B-class brains (Raw, Vision, Concrete, Kirktower)
8. Implement C-class brains (Bash, Gunash, Clash)
9. Implement A-class brains (Roark, Josie, Athena)

### Week 3: Integration Layer
10. Update all `rules.py` with tool specifications
11. Create shared `mcp_client.py`
12. Implement MetaGPT bridge
13. Implement LlamaIndex RAG for Athena

### Week 4: Testing & Validation
14. Phase 1 deployment test (D-class)
15. Phase 2 deployment test (B-class)
16. Phase 3 deployment test (C-class, tool transfers)
17. Phase 4 deployment test (A-class, GUI)

---

## Success Criteria

- ✅ All 11 MCP tools operational in Go server
- ✅ All 13 agents have functional brain logic
- ✅ Agent→MCP communication working for all tools
- ✅ Tool authorization enforced at Go level
- ✅ MetaGPT + AutoGen + LlamaIndex orchestration functional
- ✅ Phase 1-4 deployment completes without errors
- ✅ Tool ownership transfers (D1→C1, D2→C2) working
- ✅ Emergency stop (Kirktower) functional
- ✅ Consensus vetoes (Josie+Gunash+Vision+Diplo) working

---

## Risk Mitigation

### Risk: MCP tool integration failures
**Mitigation:** Implement each tool with mock/stub first, test in isolation

### Risk: Agent brain logic too complex
**Mitigation:** Start with minimal viable logic, iterate

### Risk: Permission matrix too restrictive
**Mitigation:** Log all denied requests, review and adjust

### Risk: MetaGPT + AutoGen conflicts
**Mitigation:** Keep them in separate orchestration layers, use phase_controller as arbiter

---

## Next Steps

1. **Implement Phase 0** (Golang expansion) - START NOW
2. Create tracking board for all deliverables
3. Set up integration test suite
4. Document all tool APIs
5. Begin Phase 1 after Phase 0 validation
