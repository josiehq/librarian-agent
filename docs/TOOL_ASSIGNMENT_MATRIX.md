# MCP Tool Assignment Matrix

**Updated:** December 17, 2024  
**Total Tools:** 16 (3 original + 13 MCP integrations)  
**Server Status:** ✅ Built & Ready

## Tool Ownership by Agent

### D-Class (Foundation Layer)

#### D1 Puckfairy - The Trickster Executioner
- `terminal_exec` - Direct shell command execution
- `nvim_lsp` - Neovim LSP for code editing (→ transfers to C1 Bash in Phase 3)
- `openhands_execute` - OpenHands execution layer
- **Persona:** Chaotic, impulsive, execution-focused
- **Skills:** execute_command, manage_files, run_scripts

#### D2 Diplo - The Mediator Librarian
- `memory_commit` - Memory/knowledge persistence
- `github_api` - GitHub repository management (→ transfers to C2 Gunash in Phase 3)
- `narnia_execute` - Narnia VPS/SSH operations (→ transfers to C2 Gunash in Phase 3)
- `openhands_execute` - OpenHands execution layer
- **Persona:** Diplomatic, patient, knowledge-focused
- **Skills:** read_files, analyze_logs, search_codebase

#### D3 Waria - The Sentinel Auditor
- `fabric_execute` - Fabric reasoning patterns/analysis
- `openhands_execute` - OpenHands execution layer
- **Persona:** Vigilant, pattern-obsessed, audit-focused
- **Skills:** analyze_patterns, measure_complexity, track_changes

---

### B-Class (Builder Layer)

#### B1 Raw - The Web Archaeologist
- `browser_navigate` - Browser automation/navigation
- `web_crawl` - Web content extraction
- **Persona:** Curious, relentless, information gatherer
- **Skills:** N/A (no OpenHands)

#### B2 Vision - The Design Oracle
- `figma_api` - Figma design file access
- **Persona:** Visual thinker, UX-obsessed, design-focused
- **Skills:** N/A (no OpenHands)
- **Note:** Uses Figma API, NOT Visual Sovereign (Visual Sovereign is TBD testing framework)

#### B3 Concrete - The Material Provisioner
- `amazon_api` - Amazon/e-commerce integration
- **Persona:** Practical, resource-focused, provisioner
- **Skills:** N/A (no OpenHands)

#### B4 Kirktower - The Air Traffic Controller
- `agno_orchestrate` - Process orchestration (Kirktower's DNA)
- **Persona:** Commanding, strategic, orchestration-focused
- **Skills:** N/A (uses agno, not OpenHands)
- **Note:** Agno is Kirktower's CORE DNA - process lifecycle management

---

### C-Class (Control Layer)

#### C1 Bash - The Script Specialist
- `container_exec` - Docker/container execution
- `openhands_execute` - OpenHands execution layer
- **Phase 3 Transfer:** + `nvim_lsp` (from D1 Puckfairy)
- **Persona:** Pragmatic, automation-focused, script writer
- **Skills:** write_scripts, create_automation, build_tools

#### C2 Gunash - The Git Guardian
- `container_exec` - Docker/container execution
- `openhands_execute` - OpenHands execution layer
- **Phase 3 Transfer:** + `github_api` + `narnia_execute` (from D2 Diplo)
- **Persona:** Meticulous, git-obsessed, guardian of repositories
- **Skills:** analyze_dependencies, analyze_structure, forecast_impact
- **Note:** Manages git on Narnia VPS, commands C3 Clash for codespace analysis

#### C3 Clash - The Codespaces Crawler
- `container_exec` - Docker/container execution
- `openhands_execute` - OpenHands execution layer
- `vscode_mcp` - VSCode workspace/codespace analysis
- **Persona:** Eager, literal, detail-obsessed, anxious to please Gunash
- **Skills:** write_code, write_tests, refactor_code, format_code
- **Hierarchy:** Subordinate to C2 Gunash, crawls codespaces on command

---

### A-Class (Command Layer)

#### A1 Roark - The Architect
- **No tools** (testing phase only)
- **Persona:** Visionary, architect, big-picture thinker
- **Skills:** N/A (MetaGPT orchestration)

#### A2 Josie - The Mediator
- **No tools** (testing phase only)
- **Persona:** Diplomatic, consensus-builder, mediator
- **Skills:** N/A (MetaGPT orchestration)
- **Authority:** Consensus veto power (alongside Gunash, Vision, Diplo)

#### A3 Athena - The Knowledge Oracle
- **No tools** (internal RAG system with ChromaDB)
- **Persona:** Scholarly, knowledge-focused, librarian
- **Skills:** N/A (LlamaIndex RAG)

---

## Tool Transfer Schedule

### Phase 3: Tool Ownership Transfers

**From D1 Puckfairy → To C1 Bash:**
- `nvim_lsp` (Neovim LSP access)
- **Rationale:** Bash needs code editing for script creation

**From D2 Diplo → To C2 Gunash:**
- `github_api` (GitHub repository management)
- `narnia_execute` (Narnia VPS/SSH operations)
- **Rationale:** Gunash is git guardian, manages repos on Narnia VPS

---

## Tool Categories

### Core Infrastructure (2)
- `agno_orchestrate` - Kirktower's process orchestration DNA
- `openhands_execute` - C/D agents' execution layer DNA

### Original Nucleus Tools (3)
- `container_exec` - Docker/sandbox execution (C1, C2, C3)
- `memory_commit` - Knowledge persistence (D2)
- `fs_write_guarded` - File system operations (UNUSED?)

### External MCP Integrations (11)
- `fabric_execute` - Fabric reasoning patterns (D3)
- `nvim_lsp` - Neovim LSP (D1 → C1)
- `github_api` - GitHub repos (D2 → C2)
- `terminal_exec` - Shell commands (D1)
- `figma_api` - Figma designs (B2)
- `browser_navigate` - Browser automation (B1)
- `web_crawl` - Web extraction (B1)
- `amazon_api` - E-commerce (B3)
- `narnia_execute` - VPS/SSH (D2 → C2) [STUB]
- `vscode_mcp` - VSCode workspaces (C3)
- `visual_sovereign` - Testing framework [STUB]

---

## OpenHands Agent Count

**Total:** 6 agents (all C/D class)
- D1 Puckfairy
- D2 Diplo
- D3 Waria
- C1 Bash
- C2 Gunash
- C3 Clash

---

## Quiz Results: Tool Assignment Corrections

1. ✅ **B2 Vision:** Figma API (NOT Visual Sovereign)
2. ✅ **C3 Clash:** VSCode MCP (NOT C2 Gunash)
3. ✅ **C2 Gunash:** github_api + narnia (git management on Narnia VPS)
4. ✅ **D3 Waria:** Fabric (reasoning patterns)
5. ✅ **Hierarchy:** Clash → Gunash (Clash subordinate, follows orders)

---

## Authorization Matrix Location

**File:** `/workspaces/librarian-agent/go/kernel/mcp_tools.go`  
**Lines:** 533-555 (AgentToolPermissions map)  
**Transfer Logic:** Lines 580-591 (transferToolOwnership function)

## Build Status

✅ **Binary:** `/workspaces/librarian-agent/go/kernel/mcp_server_v2`  
✅ **Size:** 9.2MB  
✅ **Compiled:** December 17, 2024 03:23 UTC  
✅ **Tools Registered:** 16 total

---

**Next:** Phase 1 brain implementation (start with D1 Puckfairy)
