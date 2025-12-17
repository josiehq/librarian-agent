# NEW Cluster Architecture: 3 Boxes

**Major Change**: Clash (C2) moved to separate GitHub Codespace, A-B-C agents merged on single AWS box

---

## Box 1: D-Agents (Orchestration)
**Instance**: GitHub Codespace 4-core (16 GB RAM) OR AWS t3a.xlarge  
**Cost**: $87/month (8hrs/day) OR $108/month (24/7)

### Models
- `rnj-1:8b` (Q4) → **D1 Puckfairy** (routing/delegation)
- `nemotron-cascade:8b` (Q4) → **D2 Diplo** (queue management)

### Purpose
- Orchestration layer
- Request routing to A-B-C box
- Agent queue management
- Hardware monitoring (Waria)

---

## Box 2: A-B-C Agents (Merged Big Brain + Vision + Code)
**Instance**: g5.12xlarge (4x A10G, 96 GB VRAM)  
**Cost**: $680/month (4hrs/day on-demand)

### Models

#### **A-Agents (Big Brain)**
1. **Qwen3-Next-80B-A3B-Thinking-GGUF** (Q4: ~40-45 GB)
   - **A1 Josie**: Advanced reasoning, complex planning
   - **A2 Roark**: Research, analysis (shares with Josie)

2. **Cogito-v2-109B-MoE** (Q4: ~30-35 GB MoE efficient)
   - **A2 Roark**: Deep thinking (uses BOTH Cogito + Qwen3)
   - **C3 Gunash**: Shell command generation

#### **B-Agents (Vision/Voice/Browser)**
- **Tools-based** (no dedicated LLM, uses vision/voice/browser services)
- **B1 Concrete Vision**: Unified agent with specialized tools
  - Vision: nemotron-ocr-v1 (~8 GB)
  - Voice: whisper-large-v3 (~3 GB)
  - Browser: Olmo-3-7B-Think (~4 GB) - shared with C1

#### **C-Agents (Code)**
3. **Olmo-3-7B-Think** (Q4: ~4 GB)
   - **C1 Bash**: Shell automation, system tasks
   - Used by B1 for browser automation (Playwright generation)

### VRAM Budget
```
Qwen3-Next-80B Q4:     40-45 GB
Cogito-109B MoE Q4:    30-35 GB
nemotron-ocr-v1:       ~8 GB
whisper-large-v3:      ~3 GB
Olmo-3-7B-Think Q4:    ~4 GB
──────────────────────────────
Total (all loaded):    ~90 GB / 96 GB available ✅
Typical (3 active):    ~55 GB
```

### Ollama Config
```bash
NUM_PARALLEL=3              # Run 3 models simultaneously
OLLAMA_MAX_LOADED_MODELS=5  # Keep all in VRAM
```

---

## Box 3: Clash (Code Generation)
**Instance**: GitHub Codespace 4-core (16 GB RAM)  
**Cost**: $87/month (8hrs/day dev) OR $0/month (free tier 60hrs)

### Model
- **Qwen3-Coder-REAP-25B-A3B** (Q4: ~13 GB)
  - **C2 Clash**: Code generation, refactoring, debugging

### Special Setup: VSCode Server Integration
```bash
# Install code-server in Codespace
curl -fsSL https://code-server.dev/install.sh | sh

# Start code-server on port 8080
code-server --bind-addr 0.0.0.0:8080 --auth none

# Ollama on port 11434
ollama serve

# Clash MCP wrapper on port 8086
python3 clash_mcp.py
```

### VSCode Extension Integration
- Install GitHub Copilot alternative using Ollama backend
- Point to `http://localhost:11434` for Clash REAP-25B
- Code completions, refactoring, chat all via Clash

---

## Cost Breakdown

| Box | Instance | Models | Cost/Month |
|-----|----------|--------|------------|
| **Box 1** | Codespace 4-core | rnj-1 + nemotron-cascade | $87 (8hr/day) |
| **Box 2** | g5.12xlarge | Qwen3-80B + Cogito-109B + Vision/Voice/Browser | $680 (4hr/day) |
| **Box 3** | Codespace 4-core | REAP-25B | $87 (8hr/day) |
| **Total** | | | **$854/month** |

**Alternative**: Run Box 1 24/7 on AWS t3a.xlarge = $108/mo (total $895/mo)

---

## Agent-Model Mapping

### A-Agents (Big Brain)
- **A1 Josie** → Qwen3-Next-80B-A3B (advanced reasoning)
- **A2 Roark** → Qwen3-Next-80B-A3B + Cogito-109B (dual model!)

### B-Agents (Vision/Voice)
- **B1 Concrete Vision** → Tool-based:
  - Vision: nemotron-ocr-v1
  - Voice: whisper-large-v3
  - Browser: Olmo-3-7B-Think (shared with C1)

### C-Agents (Code)
- **C1 Bash** → Olmo-3-7B-Think
- **C2 Clash** → REAP-25B (separate Codespace)
- **C3 Gunash** → Cogito-109B

### D-Agents (Orchestration)
- **D1 Puckfairy** → rnj-1:8b
- **D2 Diplo** → nemotron-cascade:8b

---

## Routing Logic

### Box 1 → Box 2 Routing
```go
func RouteToABC(agent string, task Task) {
    switch agent {
    case "A1_Josie", "A2_Roark":
        // Use Qwen3-Next-80B by default
        model := "qwen3-next-80b-a3b"
        
        // Roark can also use Cogito for deep thinking
        if agent == "A2_Roark" && task.RequiresDeepThinking {
            model = "cogito-109b"
        }
        
        ProxyRequest("box2.internal:11434", model, task)
    
    case "B1_Concrete":
        // Route to appropriate tool service
        if task.Type == "vision" {
            ProxyRequest("box2.internal:8083", "vision", task)
        } else if task.Type == "voice" {
            ProxyRequest("box2.internal:8084", "voice", task)
        } else if task.Type == "browser" {
            ProxyRequest("box2.internal:8085", "browser", task)
        }
    
    case "C1_Bash":
        ProxyRequest("box2.internal:11434", "olmo-3-7b-think", task)
    
    case "C3_Gunash":
        ProxyRequest("box2.internal:11434", "cogito-109b", task)
    }
}
```

### Box 1 → Box 3 Routing (Clash)
```go
func RouteToClash(task Task) {
    // Clash runs in separate Codespace
    ProxyRequest("clash-codespace.github.dev:8086", "reap-25b", task)
}
```

---

## Deployment Order

1. **Box 3 (Clash Codespace)**
   - Spin up Codespace
   - Install Ollama + REAP-25B
   - Install code-server
   - Start Clash MCP wrapper
   - Test VSCode integration

2. **Box 1 (D-agents Codespace)**
   - Spin up Codespace
   - Install Ollama + rnj-1 + nemotron-cascade
   - Build kirktower_bin
   - Start MCP server

3. **Box 2 (A-B-C AWS)**
   - Launch g5.12xlarge
   - Install Ollama + all 5 models
   - Start vision/voice/browser MCP wrappers
   - Configure routing from Box 1

---

## Model Download Commands

### Box 1 (D-agents)
```bash
ollama pull rnj-1:8b
ollama pull nemotron-cascade:8b
```

### Box 2 (A-B-C)
```bash
# A-agents
ollama pull qwen3-next-80b-a3b:q4_k_m
ollama pull cogito-109b:q4_k_m

# B-agent tools
ollama pull nemotron-ocr-v1
ollama pull whisper-large-v3

# C-agent
ollama pull olmo-3-7b-think:q4_k_m
```

### Box 3 (Clash)
```bash
ollama pull qwen3-coder-reap-25b-a3b:q4_k_m
```

---

## Minimum AWS Instance for Box 2

### **Recommended: g5.12xlarge** ✅
- **GPUs**: 4x A10G (96 GB VRAM)
- **Fits**: All 5 models comfortably (~90 GB used)
- **Cost**: $5.67/hr × 4hrs × 30 = **$680/month**

### **Alternative: g5.8xlarge** ⚠️
- **GPUs**: 1x A10G (24 GB VRAM)
- **Problem**: Cannot fit Qwen3-80B (45GB) + Cogito-109B (35GB)
- **Solution**: Unload models between tasks (slower)
- **Cost**: $1.006/hr × 4hrs × 30 = **$121/month**
- **Tradeoff**: 10-15 second model swap delays

### **Not Recommended: g5.2xlarge or smaller**
- Too small, constant model swapping
- Poor user experience

---

## VSCode Server Setup (Clash Box)

Create `.devcontainer/devcontainer.json` in Clash Codespace:

```json
{
  "name": "Clash Code Generation",
  "image": "mcr.microsoft.com/devcontainers/base:ubuntu",
  "features": {
    "ghcr.io/devcontainers/features/python:1": {},
    "ghcr.io/devcontainers/features/node:1": {}
  },
  "postCreateCommand": "bash .devcontainer/setup.sh",
  "forwardPorts": [8080, 11434, 8086],
  "customizations": {
    "vscode": {
      "extensions": [
        "continue.continue"
      ],
      "settings": {
        "continue.modelProvider": "ollama",
        "continue.ollamaUrl": "http://localhost:11434",
        "continue.model": "qwen3-coder-reap-25b-a3b"
      }
    }
  }
}
```

---

## Next Steps

1. ✅ Document new architecture
2. ⏳ Update vision_mcp.py to use nemotron-ocr-v1
3. ⏳ Create Clash Codespace setup scripts
4. ⏳ Test Roark dual-model routing (Qwen3 + Cogito)
5. ⏳ Deploy Box 2 on g5.12xlarge
6. ⏳ Test full cross-box communication
