# Agent LLM Model Assignments — librarian-agent

**Last Updated:** 2025-12-17  
**Purpose:** Definitive model configuration for all agents in the swarm

---

## 🔍 Vision Models (Shared B-Class + A-Class)

### Primary Vision: Qwen3-VL:32b (Ollama)
**Source:** https://ollama.com/library/qwen3-vl:32b  
**Used by:** All B-class agents (B1/B2/B3/B4) + A1 Roark + A2 Josie  
**Purpose:** General multimodal vision (images, light video understanding)  
**Activation:** On-demand only (init → query → cleanup to save memory)

### Fallback Vision: CLIP (PARAH)
**Source:** Already deployed in Visual Sovereign (port 8001)  
**Used by:** B-class agents for fast product image matching  
**Purpose:** Image embeddings, similarity search  
**Activation:** Always-on service, low memory footprint

### Vision MCP Wrapper
**Port:** 8093  
**Strategy:** 
1. Try CLIP first (fast, <1sec)
2. If complex reasoning needed → spawn Qwen3-VL:32b
3. Return result, cleanup Qwen3-VL instance

---

## 🅱️ B-Class Agent Models

### B1 Raw — Browser Intelligence Agent
**Browser Control Model:**
- **Primary:** browser-use/bu-30b-a3b-preview  
  https://huggingface.co/browser-use/bu-30b-a3b-preview
- **Purpose:** Human-like browser navigation, DOM understanding

**Text Generation Model:**
- **Primary:** CohereLabs/c4ai-command-r-08-2024  
  https://huggingface.co/CohereLabs/c4ai-command-r-08-2024
- **Purpose:** General reasoning, scraping logic

**Vision:** Qwen3-VL:32b (shared, on-demand)

**Question:** Which is better for browser control — current Playwright/Selenium or browser-use model?

---

### B2 Vision — Frontend/GUI Design Agent
**Image-to-Text:**
- **Primary:** Qwen3-VL-8B-NSFW-Caption-V4.5  
  https://huggingface.co/thesby/Qwen3-VL-8B-NSFW-Caption-V4.5
- **Purpose:** Generate prompts from Figma mockups/screenshots

**Text-to-Text:**
- **Primary:** Llama-3-15b-Instruct_NSFW_ORPO  
  https://huggingface.co/athirdpath/Llama-3-15b-Instruct_NSFW_ORPO
- **Purpose:** Component code generation, design refinement

**Text-to-Image:**
- **Primary:** openjourney  
  https://huggingface.co/prompthero/openjourney
- **Purpose:** Generate UI mockups from descriptions

**Vision:** Qwen3-VL:32b (shared, on-demand)

---

### B3 Concrete — Visual Sovereign & Amazon Agent
**Primary Model:**
- **Model:** Nemotron-3-Nano-30B-A3B-GGUF  
  https://huggingface.co/unsloth/Nemotron-3-Nano-30B-A3B-GGUF
- **Purpose:** Product analysis, ASIN matching logic

**Vision:** 
- CLIP (PARAH, always-on) for product matching
- Qwen3-VL:32b (shared, on-demand) for complex reasoning

**Note:** Same model as A3 Athena

---

### B4 Kirktower — Orchestration Core + Voice Control
**Speech-to-Text (STT):**
- **Model:** Whisper-large-v3  
  https://huggingface.co/openai/whisper-large-v3
- **Purpose:** Voice control easter egg (hands-free Josiedesk commands)
- **Priority:** Audio > Video (we have Fabric for video later)

**Text Generation:** TBD (likely shares with orchestration logic)

---

## 🇩 D-Class Agent Models

### D1 Puckfairy — Terminal Execution Agent
**Primary Model:**
- **Model:** rnj-1:8b (Ollama)  
  https://ollama.com/library/rnj-1:8b
- **Purpose:** Shell command generation, terminal reasoning

---

### D2 Diplo — Memory & Queue Management Agent
**Primary Model:**
- **Model:** Olmo-3-7B-Think  
  https://huggingface.co/allenai/Olmo-3-7B-Think
- **Purpose:** Lightweight reasoning for queue/cache operations

**Critical Role:** Go concurrency queueing with D3 Waria (MUST be optimized to best-in-class)

---

### D3 Waria — Meta-Cognitive & Resource Monitor
**Primary Model:**
- **Model:** Nemotron-Cascade-8B  
  https://huggingface.co/nvidia/Nemotron-Cascade-8B
- **Purpose:** Resource monitoring, threshold detection

**Critical Requirements:**
- **MUST** always know hardware specs (CPU/GPU/RAM/VRAM)
- **MUST** handle agent queueing with D2 Diplo
- Go concurrency optimization critical
- Lifecycle management (init → tool → cleanup)

---

## 🇨 C-Class Agent Models

### C1 Bash & C3 Clash — Code Execution Agents
**Primary Model (SHARED):**
- **Model:** Qwen3-Coder-REAP-25B-A3B  
  https://huggingface.co/cerebras/Qwen3-Coder-REAP-25B-A3B
- **Purpose:** Code generation, debugging

**Note:** User question — Qwen3-Coder:30b (Ollama) vs REAP-25B-A3B?  
**Decision:** Use same model for both C1 and C3 (REAP-25B-A3B chosen)

---

### C2 Gunash — Git Management Agent
**Primary Model:**
- **Model:** Qwen3-Next-80B-A3B-Thinking-GGUF  
  https://huggingface.co/Qwen/Qwen3-Next-80B-A3B-Thinking-GGUF
- **Purpose:** Complex git orchestration, reasoning

**Note:** Same model as A1 Roark and A2 Josie

---

## 🅰️ A-Class Agent Models

### A1 Roark — Strategic Planning Agent
**Primary Model:**
- **Model:** Qwen3-Next-80B-A3B-Thinking-GGUF  
  https://huggingface.co/Qwen/Qwen3-Next-80B-A3B-Thinking-GGUF
- **Purpose:** High-level reasoning, strategic planning

**Deep Thinking Model:**
- **Model:** Cogito:70b (Ollama)  
  https://ollama.com/library/cogito:70b
- **Purpose:** Internal reasoning only (not exposed to user)

**Vision:** Qwen3-VL:32b (shared, on-demand)

**Special Architecture:**
```
User Input → Qwen3 → Cogito:70b (deep thinking) → Qwen3 (in-character response)
```

---

### A2 Josie — Executive Agent
**Primary Model:**
- **Model:** Qwen3-Next-80B-A3B-Thinking-GGUF  
  https://huggingface.co/Qwen/Qwen3-Next-80B-A3B-Thinking-GGUF
- **Purpose:** Executive decision-making

**Vision:** Qwen3-VL:32b (shared, on-demand)

**Note:** Container operations via delegation to D3/C3, no direct tools

---

### A3 Athena — Knowledge & RAG Agent
**Primary Model:**
- **Model:** Nemotron-3-Nano-30B-A3B-GGUF  
  https://huggingface.co/unsloth/Nemotron-3-Nano-30B-A3B-GGUF
- **Purpose:** RAG operations, knowledge base management

**Note:** Same model as B3 Concrete

---

## 🏗️ Architecture Principles

### Memory Optimization
**Tool Lifecycle:**
```
1. Initialize model (load into memory)
2. Execute query
3. Cleanup/unload model
```

**Responsibility:** Waria + Diplo handle all queueing/lifecycle via Go concurrency

---

### Vision Strategy
**Decision Tree:**
```
Query arrives
  ↓
Is it a product image? → YES → Use CLIP (PARAH, fast)
  ↓ NO
Complex reasoning needed? → YES → Spawn Qwen3-VL:32b
  ↓ NO
Use text-only model
```

---

### Resource Monitoring (Waria's Job)
**Required Knowledge:**
- CPU cores, utilization
- GPU model, VRAM available
- System RAM, swap usage
- Disk I/O, network bandwidth
- Model memory footprint per agent

**Phase 1 Requirement:** Waria MUST detect all hardware specs on startup

---

## 📋 Implementation Priority

### Phase 1 (Current)
1. ✅ Document model assignments (this file)
2. ⏳ Implement Waria hardware detection
3. ⏳ Implement Diplo+Waria Go queueing
4. ⏳ Deploy vision MCP wrapper (port 8093)

### Phase 2 (Build Test)
1. Wire B4 Kirktower Whisper STT (voice control)
2. Configure first agent LLM profile
3. Test Amazon/Visual Sovereign workflow
4. Implement tool lifecycle management

### Future
- Video/screencapture template (deferred)
- Multi-VPS deployment with SSH tunnels
- Fabric integration for video analysis

---

## 🚨 Open Questions

1. **B1 Raw browser control:** Current Playwright/Selenium vs browser-use/bu-30b-a3b-preview — which is better?
2. **C1/C3 model:** Confirmed REAP-25B-A3B for both?
3. **First agent to implement:** Which agent/tool should we configure first?

---

**Next Step:** Pick ONE agent/tool/LLM to implement and check in with user frequently.
