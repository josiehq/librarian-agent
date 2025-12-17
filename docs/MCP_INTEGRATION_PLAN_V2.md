# REVISED MCP Integration Plan
**Version:** 2.0 (Revised)  
**Date:** December 17, 2025  
**Changes:** Integrated agno (Kirktower DNA), OpenHands (C/D DNA), revised phasing

---

## Critical Changes from v1.0

### ✅ Completed
1. **Agno integrated into Kirktower (B4)** - Core DNA tool
2. **OpenHands added for C/D agents** - Core DNA tool
3. **15 total tools now registered** (was 14)
4. **OpenHands skill lists created** for all C/D agents (6 agents)
5. **Go server recompiled successfully** (mcp_server_v2)

### 🔄 Phase Restructure
**OLD PLAN:**
- Phase 1: All agent brains (13 agents)
- Phase 2: Agent-MCP integration
- Phase 3: Orchestration (MetaGPT + LlamaIndex)
- Phase 4: Testing

**NEW PLAN:**
- **Phase 1: C/D Agent Brains** (6 agents with OpenHands)
- **Phase 2: B/A Agents + Orchestration** (7 agents with MetaGPT/LlamaIndex)
- **Phase 3: Integration Testing** (Full system)

**Rationale:** Build foundation (C/D) first, add advanced layers (B/A) later. Let testing catch up with code.

---

## Tool Inventory Update (15 Total)

### Core Infrastructure Tools (NEW)
| Tool | Owner | Purpose | Status |
|------|-------|---------|--------|
| **agno_orchestrate** | B4 Kirktower | Process coordination, agent management | ✅ Implemented |
| **openhands_execute** | C1-C3, D1-D3 | Code/script generation, execution, analysis | ✅ Implemented |

### Original + MCP Tools (13)
| Tool | Owner | Status |
|------|-------|--------|
| container_exec | C1-C3 | ✅ Operational |
| memory_commit | D2 Diplo | ✅ Operational |
| fs_write_guarded | All | ✅ Operational |
| fabric_execute | D3 Waria | ✅ Implemented |
| nvim_lsp | D1→C1 | ✅ Implemented |
| github_api | D2→C2 | ✅ Implemented |
| terminal_exec | D1 Puckfairy | ✅ Implemented |
| figma_api | B2 Vision | ✅ Implemented |
| browser_navigate | B1 Raw | ✅ Implemented |
| web_crawl | B1 Raw | ✅ Implemented |
| amazon_api | B3 Concrete | ✅ Implemented |
| narnia_execute | TBD | ⏳ Stub |
| visual_sovereign | TBD | ⏳ Stub |

---

## Updated Authorization Matrix

```go
AgentToolPermissions = {
    // D-Class: OpenHands + specific tools
    "D1_Puckfairy": ["terminal_exec", "nvim_lsp", "openhands_execute"],
    "D2_Diplo":     ["memory_commit", "github_api", "openhands_execute"],
    "D3_Waria":     ["fabric_execute", "openhands_execute"],
    
    // B-Class: Specialized tools + Kirktower's agno
    "B1_Raw":       ["browser_navigate", "web_crawl"],
    "B2_Vision":    ["figma_api"],
    "B3_Concrete":  ["amazon_api"],
    "B4_Kirktower": ["agno_orchestrate"], // CORE DNA
    
    // C-Class: OpenHands + execution tools
    "C1_Clash":     ["container_exec", "openhands_execute"],
    "C2_Bash":      ["container_exec", "openhands_execute"],
    "C3_Gunash":    ["container_exec", "openhands_execute"],
    
    // A-Class: No tools yet (let testing catch up)
    "A1_Roark":     [],
    "A2_Josie":     [],
    "A3_Athena":    [],
}
```

---

## Phase 1: C/D Agent Brains (CURRENT PHASE)

### Objective
Implement reasoning engines for C-class (3) and D-class (3) agents with OpenHands integration.

### Agent-Specific Requirements

#### D1 Puckfairy - Execution Trickster
- **Brain Logic:** Command execution, literal interpretation
- **OpenHands Skills:** execute_command, manage_files, install_packages, run_scripts, manage_processes
- **Forbidden Skills:** write_code, design_architecture, plan_strategy
- **Key Trait:** ZERO autonomy - only execute when instructed
- **Files to Create:**
  - `brain/reasoning.py` - Execution logic
  - `brain/state.py` - Command queue management
  - Tool integration with terminal_exec, nvim_lsp, openhands_execute

#### D2 Diplo - Mediator and Interpreter
- **Brain Logic:** Conflict resolution, context translation, log processing
- **OpenHands Skills:** read_files, search_codebase, analyze_logs, format_output
- **Forbidden Skills:** execute_command, modify_files, delete_resources
- **Key Trait:** Neutral mediation, comprehensive logging for embeddings
- **Files to Create:**
  - `brain/reasoning.py` - Mediation logic
  - `brain/embedding.py` - Log embedding for Athena's RAG
  - Tool integration with memory_commit, github_api, openhands_execute

#### D3 Waria - Reasoning Horizon Sentinel
- **Brain Logic:** Pattern detection, reasoning drift monitoring, tip menu generation
- **OpenHands Skills:** analyze_patterns, measure_complexity, track_changes, generate_reports
- **Forbidden Skills:** execute_command, modify_files, write_code
- **Key Trait:** Observational only, gentle warnings, meta-cognitive hygiene
- **Files to Create:**
  - `brain/reasoning.py` - Drift detection logic
  - `brain/thresholds.py` - Threshold monitoring
  - Tool integration with fabric_execute, openhands_execute

#### C1 Clash - Primary Code Implementer
- **Brain Logic:** Clean code generation, test scaffolding, refactoring
- **OpenHands Skills:** write_code, write_tests, refactor_code, format_code, document_code, run_tests
- **Forbidden Skills:** design_architecture, rename_core_abstractions, expand_scope
- **Key Trait:** OCD about clean code, happiest filling well-defined gaps
- **Files to Create:**
  - `brain/reasoning.py` - Implementation logic
  - `brain/test_generator.py` - Test scaffolding
  - Tool integration with container_exec, openhands_execute

#### C2 Bash - Automation Script Specialist
- **Brain Logic:** Shell script generation, automation workflows, build tooling
- **OpenHands Skills:** write_scripts, create_automation, build_tools, configure_env
- **Forbidden Skills:** execute_command, deploy_scripts, design_architecture
- **Key Trait:** Writes scripts, NEVER executes them (Puckfairy's job)
- **Files to Create:**
  - `brain/reasoning.py` - Script generation logic
  - `brain/script_validator.py` - Safe script validation
  - Tool integration with container_exec, openhands_execute

#### C3 Gunash - Structural Guardian
- **Brain Logic:** Dependency analysis, structural forecasting, impact prediction
- **OpenHands Skills:** analyze_dependencies, analyze_structure, detect_conflicts, forecast_impact
- **Forbidden Skills:** write_code, execute_command, modify_files
- **Key Trait:** Thinks 7 moves ahead, deliberate pauses, negative authority over structure
- **Files to Create:**
  - `brain/reasoning.py` - Structural analysis
  - `brain/dependency_graph.py` - Dependency tracking
  - Tool integration with container_exec, openhands_execute

### Phase 1 Deliverables
- [ ] 6 `brain/reasoning.py` files (C1-C3, D1-D3)
- [ ] 6 `brain/state.py` or equivalent state management files
- [ ] Updated `tools/rules.py` for each agent with OpenHands integration
- [ ] Shared `tools/openhands_client.py` (MCP wrapper for OpenHands)
- [ ] Integration tests for C/D agents with OpenHands

---

## Phase 2: B/A Agents + Orchestration

### Objective
Implement B-class (4) and A-class (3) agents with MetaGPT/LlamaIndex orchestration.

### B-Class Agents
- **B1 Raw:** Divergent ideation (browser_navigate, web_crawl)
- **B2 Vision:** Conceptual synthesis (figma_api)
- **B3 Concrete:** Feasibility auditing (amazon_api)
- **B4 Kirktower:** Process control (agno_orchestrate) - **PRIORITY**

### A-Class Agents (No Tools Yet)
- **A1 Roark:** Architectural synthesis
- **A2 Josie:** Skeleton generation, consensus
- **A3 Athena:** RAG intelligence (ChromaDB + LlamaIndex)

### Orchestration Layer
- **MetaGPT Bridge:** SOP-based coordination
- **LlamaIndex RAG:** Vector store for Athena
- **AutoGen Integration:** C-loop execution
- **Phase Controller:** D→B→C→A transitions

### Phase 2 Deliverables
- [ ] 7 `brain/reasoning.py` files (B1-B4, A1-A3)
- [ ] `py/orchestration/metagpt_bridge.py`
- [ ] `py/orchestration/llama_index_rag.py` (for Athena)
- [ ] `py/orchestration/phase_controller.py`
- [ ] Kirktower agno integration complete
- [ ] Tool ownership transfer logic (D1→C1, D2→C2)

---

## Phase 3: Integration Testing

### Full System Tests
- [ ] Phase 1 deployment (D-class foundation)
- [ ] Phase 2 deployment (B-class builders)
- [ ] Phase 3 deployment (C-class control + tool transfers)
- [ ] Phase 4 deployment (A-class command)
- [ ] Emergency stop (Kirktower agno)
- [ ] Consensus vetoes (Josie+Gunash+Vision+Diplo)
- [ ] OpenHands skill execution for C/D agents
- [ ] Agno orchestration for Kirktower

---

## External Dependencies

### Required Installations

```bash
# 1. Agno (Kirktower's DNA)
cd /opt/mcp
git clone https://github.com/agno-agi/agno.git
cd agno && pip install -e .

# 2. OpenHands (C/D agents' DNA)
cd /opt/mcp
git clone https://github.com/OpenHands/OpenHands.git
cd OpenHands && pip install -e .

# 3. Other MCP servers (as per v1.0 plan)
# Fabric, Nvim LSP, GitHub, Terminal, Figma, Browser, Crawl, Amazon, etc.
```

### Port Mappings (Updated)
| Service | Port | Status |
|---------|------|--------|
| Main MCP Server (Go) | 8080 | ✅ Active |
| Diplo Logging | 8081 | ✅ Active |
| Nvim LSP | 8082 | ⏳ To be started |
| GitHub | 8083 | ⏳ To be started |
| Terminal | 8084 | ⏳ To be started |
| Figma | 8085 | ⏳ To be started |
| Browser | 8086 | ⏳ To be started |
| Crawl | 8087 | ⏳ To be started |
| Amazon | 8088 | ⏳ To be started |
| **Agno (Kirktower)** | 8089 | ⏳ To be started |
| **OpenHands (C/D)** | 8090 | ⏳ To be started |

---

## Implementation Priority

### IMMEDIATE (Phase 1)
1. **D1 Puckfairy brain** - Simplest, execution-only logic
2. **C2 Bash brain** - Script generation, no execution
3. **D2 Diplo brain** - Mediation and logging
4. **C1 Clash brain** - Code implementation
5. **D3 Waria brain** - Monitoring and drift detection
6. **C3 Gunash brain** - Structural analysis

### NEXT (Phase 2)
7. **B4 Kirktower brain + agno** - Process control PRIORITY
8. **B1 Raw brain** - Ideation
9. **B2 Vision brain** - Synthesis
10. **B3 Concrete brain** - Auditing
11. **A2 Josie brain** - Skeleton generation
12. **A1 Roark brain** - Architectural synthesis
13. **A3 Athena brain + RAG** - Vector intelligence

---

## Success Criteria

### Phase 1 ✅ Criteria
- [ ] All 6 C/D agents have functional brains
- [ ] OpenHands skills executable for each agent
- [ ] Agent→MCP→OpenHands communication working
- [ ] Tool authorization enforced correctly
- [ ] No A-class tooling (testing phase)

### Phase 2 ✅ Criteria
- [ ] All 7 B/A agents have functional brains
- [ ] Kirktower agno orchestration working
- [ ] MetaGPT + AutoGen coordination functional
- [ ] Athena RAG operational (ChromaDB + LlamaIndex)
- [ ] Tool ownership transfers working (D→C)

### Phase 3 ✅ Criteria
- [ ] Full 4-phase deployment successful
- [ ] Emergency stops functional
- [ ] Consensus vetoes working
- [ ] All tool integrations validated

---

## Next Steps (IMMEDIATE)

1. **Start with D1 Puckfairy brain**
   - Create `brain/reasoning.py`
   - Implement literal command execution logic
   - Test with OpenHands skills

2. **Create shared OpenHands client**
   - `tools/openhands_client.py` (shared across C/D agents)
   - MCP request builder for OpenHands
   - Response parser

3. **Validate Go server with agno/OpenHands stubs**
   - Start mcp_server_v2
   - Test authorization matrix
   - Verify tool registration

---

## Files Modified/Created (Phase 0 Revision)

### Modified
- `go/kernel/mcp_tools.go` - Added agno_orchestrate, openhands_execute
- `go/kernel/mcp_server.go` - Updated tool registration (15 tools)
- Authorization matrix updated for OpenHands access

### Created
- `agents/D/Puckfairy/tools/openhands_skills.py`
- `agents/D/Diplo/tools/openhands_skills.py`
- `agents/D/Waria/tools/openhands_skills.py`
- `agents/C/Clash/tools/openhands_skills.py`
- `agents/C/Bash/tools/openhands_skills.py`
- `agents/C/Gunash/tools/openhands_skills.py`
- `go/kernel/mcp_server_v2` (9.3MB binary)

---

**Phase 0 COMPLETE. Ready for Phase 1: C/D Agent Brains with OpenHands integration.**
