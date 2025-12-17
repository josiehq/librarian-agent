# Agent Distribution Across 4-Node Cluster

## Box 1: Orchestration Hub (D-Agents)

**Instance**: AWS c6i.xlarge (4 vCPU, 8 GB RAM)  
**Cost**: ~$123/month (24/7)  
**GPU**: None (CPU-only)

| Agent | Model | VRAM | Role |
|-------|-------|------|------|
| **D1 Puckfairy** | rnj-1:8b | 0 MB (CPU) | Task dispatch & coordination |
| **D2 Diplo** | qwen3-mini:2.8b | 0 MB (CPU) | Channel management & routing |
| **D3 Waria** | None (system) | 0 MB | Hardware monitoring & queue management |

**Services**:
- Kirktower MCP Server (port 8080)
- PostgreSQL (state)
- Redis (cache)
- Narnia CLI (git ops)

---

## Box 2: Isolated Codespace (C3 Clash)

**Instance**: AWS c6i.2xlarge (8 vCPU, 16 GB RAM)  
**Cost**: ~$103/month (4 hours/day on-demand)  
**GPU**: None (CPU-only)

| Agent | Model | VRAM | Role |
|-------|-------|------|------|
| **C3 Clash** | REAP-25B-A3B | 0 MB (CPU) | GitHub Codespace operations, sandbox code execution |

**Services**:
- GitHub CLI (`gh`)
- Docker (codespace containers)
- MCP Proxy (port 8082)

**Security**: Isolated subnet, no direct internet access

---

## Box 3: Vision & Audio Workers (B-Agents + C1)

**Instance**: AWS g5.2xlarge (8 vCPU, 32 GB RAM, 1x A10G 24GB)  
**Cost**: ~$875/month (24/7)  
**GPU**: 1x NVIDIA A10G (24 GB VRAM)

| Agent | Model | VRAM | Role |
|-------|-------|------|------|
| **B1 Raw** | Qwen3-VL:32b | 12 GB | Browser automation & supplier scraping |
| **B2 Vision** | Qwen3-VL:32b | 12 GB | Design analysis (Figma integration) |
| **B3 Concrete** | Nemotron-3-Nano:1.7b | 768 MB | Product analysis (Amazon + Visual Sovereign) |
| **B4 Kirktower** | Whisper-large-v3 | 4 GB | Voice control (STT) |
| **C1 Bash** | REAP-25B-A3B | 10 GB | Shell command generation |

**Services**:
- Ollama (LLM runtime)
- PARAH/Visual Sovereign (CLIP embeddings)
- ChromeDriver (Playwright)
- MCP Wrappers:
  - Port 8083: Vision MCP
  - Port 8084: Whisper STT
  - Port 8085: Amazon MCP
  - Port 8086: Figma MCP
  - Port 8087: Browser MCP

**VRAM Budget**: 24 GB total
- Load/unload models via queue lifecycle (INIT→USE→CLEANUP)
- Max 2 models concurrent (e.g., Qwen3-VL + Whisper = 16 GB)

---

## Box 4: Big Brain (A-Agents + C2) **ON-DEMAND**

**Instance**: AWS g5.12xlarge (48 vCPU, 192 GB RAM, 4x A10G 96GB)  
**Cost**: ~$680/month (4 hours/day on-demand)  
**GPU**: 4x NVIDIA A10G (96 GB total VRAM)

| Agent | Model | VRAM | Role |
|-------|-------|------|------|
| **A1 Roark** | Qwen3:32b → Cogito:70b → Qwen3:32b | 12+28+12 GB | Multi-stage reasoning & deliberation chain |
| **A2 Josie** | Nemotron-3:22b | 8 GB | Code review & refactoring |
| **C2 Gunash** | Command-R:32b | 12 GB | Git operations & changelog generation |
| **Vision Server** | Qwen3-VL:32b | 12 GB | Complex vision fallback from Box 3 |

**Services**:
- Ollama (LLM runtime)
- MCP Wrappers:
  - Port 8090: Roark deliberation
  - Port 8091: Josie code review
  - Port 8092: Gunash git ops
  - Port 8093: Vision fallback

**VRAM Budget**: 96 GB total
- GPU 0+1: Roark chain (Qwen3 12GB + Qwen3 12GB = 24 GB)
- GPU 2+3: Cogito 70B deliberation (28 GB × 2 shards = 56 GB)
- GPU 3: Josie (8 GB) + Gunash (12 GB) = 20 GB

**Auto-Start Logic**:
```python
# Box 1 monitors queue and starts Box 4 when:
# 1. High-priority reasoning task (A1, A2)
# 2. Vision fallback needed (Box 3 → Box 4)
# 3. Git operations with changelog (C2)

# Auto-stop after 2 hours idle
```

---

## Summary Table

| Box | Agents | GPU | Monthly Cost | Purpose |
|-----|--------|-----|--------------|---------|
| **Box 1** | D1, D2, D3 | None | $123 | Orchestration (24/7) |
| **Box 2** | C3 | None | $103 | Codespace isolation (on-demand) |
| **Box 3** | B1, B2, B3, B4, C1 | 1x A10G (24GB) | $875 | Vision & audio workers (24/7) |
| **Box 4** | A1, A2, C2, Vision | 4x A10G (96GB) | $680 | Big brain reasoning (on-demand) |
| **Total** | 13 agents | 5 GPUs | **$1,781/month** | Full cluster |

---

## MCP Communication Patterns

### Box 1 → Box 3 (Vision delegation)
```python
# User asks: "Find leather wallets on AliExpress"
# Box 1 (D2 Diplo) routes to Box 3 (B1 Raw)

response = requests.post("http://box3.internal:8083/vision", json={
    "agent": "B1_Raw",
    "task": "Search AliExpress for leather wallets",
    "model": "qwen3-vl:32b",
    "priority": 7
})
```

### Box 3 → Box 4 (Vision fallback)
```python
# Box 3 CLIP fails (low confidence), escalate to Box 4

# 1. Try local CLIP (fast, cheap)
clip_result = local_clip_inference(image_url)
if clip_result["confidence"] < 0.85:
    # 2. Escalate to Box 4 (slow, expensive)
    response = requests.post("http://box4.internal:8093/vision/complex", json={
        "image_url": image_url,
        "question": "Is this a leather wallet?",
        "model": "qwen3-vl:32b"
    })
```

### Box 1 → Box 4 (Auto-start big brain)
```python
# User asks: "Review this complex PR with 50 files changed"
# Box 1 (D1 Puckfairy) checks if Box 4 is online

if not is_box4_online():
    start_box4()  # Sends AWS API call to start instance
    wait_for_boot(timeout=120)  # Wait for Ollama to load

# Route to Josie (A2) for code review
response = requests.post("http://box4.internal:8091/josie", json={
    "task": "Review PR #123",
    "files": pr_files,
    "priority": 9
})
```

### Box 1 → Box 2 (Clash codespace)
```python
# User asks: "Create a new GitHub Codespace for testing"
# Box 1 (D2 Diplo) routes to Box 2 (C3 Clash)

response = requests.post("http://box2.internal:8082/codespace/create", json={
    "repo": "josiehq/librarian-agent",
    "branch": "feature/new-agent",
    "machine_type": "standardLinux32gb"
})
```

---

## Agent Communication Flow

```
User Request
    │
    ▼
┌───────────────────┐
│  Box 1 (D-Agents) │ ◄─── Always-on orchestrator
│  D1 → D2 → D3     │
└───────────────────┘
    │ routes to...
    │
    ├─────────────────────┐───────────────────┐
    ▼                     ▼                   ▼
┌──────────┐      ┌──────────────┐    ┌──────────────┐
│  Box 2   │      │    Box 3     │    │   Box 4      │
│ (C3)     │      │ (B1-B4, C1)  │    │ (A1, A2, C2) │
│ Codespace│      │ Vision+Audio │    │  Big Brain   │
└──────────┘      └──────────────┘    └──────────────┘
                         │                    ▲
                         │ fallback if needed │
                         └────────────────────┘
```

---

**Next Steps**:
1. Implement MCP proxy layer in `go/kernel/mcp_proxy.go`
2. Create Box 4 auto-start Lambda function
3. Test inter-box vision delegation
4. Deploy Terraform infrastructure for all 4 boxes
