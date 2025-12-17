# Final 4-Node Cluster Configuration

**Last Updated**: December 17, 2025  
**Status**: Ready for Deployment

---

## Box 1: Orchestration Hub (D-Agents) — CPU ONLY

### Hardware
- **Instance**: AWS t3a.xlarge
- **vCPU**: 4
- **RAM**: 16 GB
- **GPU**: None (CPU inference)
- **Cost**: **$108/month** (24/7)

### Agent & Model Configuration

| Agent | Model | RAM (Q4) | Purpose |
|-------|-------|----------|---------|
| **D1 Puckfairy** | rnj-1:8b-q4_k_m | 4 GB | Task dispatch & user intent parsing |
| **D2 Diplo** | nemotron-cascade:8b-q4_k_m | 4 GB | Dynamic queue optimization & resource allocation |
| **D3 Waria** | None (algorithmic) | 0 | Hardware monitoring, logging, threshold checking |

**Total RAM Usage**: 8 GB models + 2 GB OS/services = **10 GB / 16 GB available** ✅

### Ollama Configuration
```bash
export OLLAMA_NUM_PARALLEL=2          # Load both models simultaneously
export OLLAMA_MAX_LOADED_MODELS=2     # Keep both in memory
export OLLAMA_NUM_THREAD=4            # Use all 4 vCPUs
export OLLAMA_HOST=0.0.0.0:11434
```

### Model Installation
```bash
ollama pull rnj-1:8b-q4_k_m
ollama pull nemotron-cascade:8b-q4_k_m
```

### Performance Estimates
- **Latency**: 5-8 seconds per inference (CPU)
- **Throughput**: ~0.5 requests/sec (4 concurrent workers)
- **Token Speed**: 15-25 tokens/sec per model

---

## Box 2: Isolated Codespace (C3 Clash) — SMALL GPU

### Hardware
- **Instance**: AWS g5.xlarge
- **vCPU**: 4
- **RAM**: 16 GB
- **GPU**: 1x NVIDIA A10G (24 GB VRAM)
- **Cost**: $730/month (24/7) OR **$1.01/hour on-demand**
- **Recommendation**: **On-demand 4 hours/day = $123/month**

### Agent & Model Configuration

| Agent | Model | VRAM | Purpose |
|-------|-------|------|---------|
| **C3 Clash** | REAP-25B-A3B (30B params) | ~15 GB | Code generation, GitHub Codespace operations, sandbox execution |

**Model Link**: [NousResearch/REAP-25B-A3B](https://huggingface.co/NousResearch/REAP-25B-A3B)

**VRAM Usage**: 15 GB / 24 GB available ✅

### Ollama Configuration
```bash
export OLLAMA_NUM_PARALLEL=1
export OLLAMA_MAX_LOADED_MODELS=1
export OLLAMA_NUM_GPU=1
export CUDA_VISIBLE_DEVICES=0
```

### Model Installation
```bash
# Pull quantized version for 24GB GPU
ollama pull nous-research/reap-25b-a3b:q4_k_m
```

### Performance Estimates
- **Latency**: 1-2 seconds per inference (GPU)
- **Throughput**: ~1-2 requests/sec
- **Token Speed**: 40-60 tokens/sec
- **Code Quality**: Production-grade (30B model)

### Security Isolation
- Separate AWS VPC subnet (no direct internet)
- Only accessible from Box 1 (orchestrator)
- Ephemeral storage (auto-wipe after sessions)

---

## Box 3: Vision & Audio Workers (B1 + C1) — MEDIUM GPU

### Hardware
- **Instance**: AWS g5.xlarge
- **vCPU**: 4
- **RAM**: 16 GB
- **GPU**: 1x NVIDIA A10G (24 GB VRAM)
- **Cost**: **$730/month** (24/7)

### Unified B1 Agent Architecture

**Philosophy**: Single agent with multiple specialized tools instead of 4 separate agents.

| Component | Model | VRAM | Purpose |
|-----------|-------|------|---------|
| **Vision (OCR)** | deepseek-ocr | ~8 GB | Product image analysis, text extraction |
| **Vision (Screening)** | CLIP-ViT-B/32 | 150 MB | Fast image relevance filtering (100+ images/sec) |
| **Voice (STT)** | whisper-large-v3 | ~3 GB | Voice control, audio transcription |
| **Browser/Bash** | Olmo-3-7B-Think | ~4 GB | Browser automation (Playwright), shell commands |

**Model Links**:
- [deepseek-ocr on Ollama](https://ollama.com/library/deepseek-ocr)
- [whisper-large-v3 on HuggingFace](https://huggingface.co/openai/whisper-large-v3)
- [Olmo-3-7B-Think on HuggingFace](https://huggingface.co/allenai/Olmo-3-7B-Think)

**Total VRAM**: 8 + 0.15 + 3 + 4 = **~15 GB / 24 GB** ✅

### Agent Roster

| Agent | Models Used | Primary Role |
|-------|-------------|--------------|
| **B1 "Concrete Vision"** | All 4 models | Vision analysis, voice control, browser automation, supplier harvesting |
| **C1 Bash** | Olmo-3-7B-Think (shared) | Shell command generation |

### Services Running

**Port 8083**: Vision MCP Wrapper
```python
# Endpoints:
POST /vision/ocr          # deepseek-ocr
POST /vision/screen       # CLIP fast screening
POST /vision/analyze      # Full analysis with OCR
```

**Port 8084**: Voice MCP Wrapper
```python
POST /voice/transcribe    # whisper-large-v3
POST /voice/command       # Voice → action routing
```

**Port 8085**: Browser Automation MCP
```python
POST /browser/automate    # Olmo-3-7B-Think generates Playwright
POST /browser/execute     # Run automation script
```

**Port 8086**: Figma MCP (proxy)
```python
POST /figma/extract       # Proxy to figma-mcp-server
```

**Port 8087**: Visual Sovereign / Harvester
```python
POST /harvest/suppliers   # PARAH scraping (Sunsky, AliExpress, CJ)
POST /harvest/analyze     # CLIP + OCR analysis pipeline
```

### Ollama Configuration
```bash
export OLLAMA_NUM_PARALLEL=3          # Load deepseek-ocr + whisper + olmo simultaneously
export OLLAMA_MAX_LOADED_MODELS=3
export OLLAMA_NUM_GPU=1
export CUDA_VISIBLE_DEVICES=0
```

### Model Installation
```bash
ollama pull deepseek-ocr
ollama pull whisper-large-v3
ollama pull allenai/olmo-3-7b-think

# CLIP installed via Python
pip install transformers torch
# Will auto-download clip-vit-base-patch32 on first use
```

### Performance Estimates
- **OCR**: 20-30 tokens/sec, ~5 sec per image
- **CLIP Screening**: 50-100 images/sec
- **Whisper**: Real-time (1x speed on GPU)
- **Olmo**: 25-35 tokens/sec for browser scripts

### Phase 2 Workflow: Supplier Harvesting → Amazon Listing

```python
# 1. Visual Sovereign scrapes suppliers
products = harvest_suppliers("leather wallet", ["sunsky", "aliexpress"])
# Returns: 500 products with images

# 2. CLIP fast screening (B1)
relevant = clip_screen(products, threshold=0.7)
# Filters: 500 → 50 products

# 3. OCR detailed analysis (B1, deepseek-ocr)
analyzed = [deepseek_ocr_analyze(p.image) for p in relevant]

# 4. Browser automation (B1, Olmo-3-7B-Think)
for product in analyzed[:10]:
    script = olmo_generate_playwright(f"Create Amazon listing for {product}")
    execute_browser_script(script)
```

---

## Box 4: Big Brain (A-Agents + C2) — LARGE GPU

### Hardware
- **Instance**: AWS g5.12xlarge
- **vCPU**: 48
- **RAM**: 192 GB
- **GPU**: 4x NVIDIA A10G (96 GB total VRAM)
- **Cost**: $5.67/hour = **$4,100/month** (24/7)
- **Recommendation**: **On-demand 4 hours/day = $680/month**

### Agent & Model Configuration

| Agent | Model | VRAM | Purpose |
|-------|-------|------|---------|
| **A1 Roark** | Qwen3:32b → Cogito:70b → Qwen3:32b | 12 + 28 + 12 GB | Multi-stage reasoning chain |
| **A2 Josie** | Nemotron-3:22b | 8 GB | Code review & refactoring |
| **C2 Gunash** | Command-R:32b | 12 GB | Git operations & changelog |
| **Vision Fallback** | Qwen3-VL:32b | 12 GB | Complex vision (from Box 3 escalation) |

**Total VRAM**: ~72 GB / 96 GB available ✅

### Auto-Start/Stop Logic
```python
# Box 1 monitors queue and auto-starts Box 4 when:
# 1. High-priority reasoning task (A1, A2)
# 2. Vision fallback from Box 3 (CLIP confidence < 0.85)
# 3. Complex git operations (C2)

# Auto-stop after 2 hours idle (saves ~$11/hour)
```

---

## Cost Summary

| Box | Instance | Models | $/month (24/7) | $/month (Optimized) |
|-----|----------|--------|----------------|---------------------|
| **Box 1** | t3a.xlarge (CPU) | 2x 8B | $108 | $108 |
| **Box 2** | g5.xlarge (GPU) | 1x 30B | $730 | $123 (4hr/day) |
| **Box 3** | g5.xlarge (GPU) | 4 models (~15GB) | $730 | $730 (always-on) |
| **Box 4** | g5.12xlarge (GPU) | 4 models (~72GB) | $4,100 | $680 (4hr/day) |
| **Total** | | | **$5,668** | **$1,641/month** ✅ |

**Savings**: $4,027/month with on-demand optimization

---

## Deployment Order

### Phase 1: Box 1 (Foundation)
```bash
1. Deploy t3a.xlarge
2. Install Ollama + models (rnj-1:8b, nemotron-cascade:8b)
3. Start Kirktower with hardware monitor + queue
4. Test local agent routing
```

### Phase 2: Box 3 (Vision Workers)
```bash
1. Deploy g5.xlarge
2. Install Ollama + models (deepseek-ocr, whisper, olmo)
3. Deploy MCP wrappers (ports 8083-8087)
4. Test Box 1 → Box 3 delegation
5. Test Visual Sovereign integration
```

### Phase 3: Box 2 (Clash Isolation)
```bash
1. Deploy g5.xlarge (on-demand)
2. Install Ollama + REAP-25B-A3B
3. Configure isolated VPC subnet
4. Test codespace workflows
```

### Phase 4: Box 4 (Big Brain)
```bash
1. Deploy g5.12xlarge (on-demand)
2. Install Ollama + models (qwen3:32b, cogito:70b, etc)
3. Implement auto-start Lambda
4. Test Box 3 → Box 4 vision fallback
5. Configure 2-hour idle shutdown
```

---

## Environment Variables

### Box 1 (Orchestrator)
```bash
export BOX1_URL=http://localhost:8080
export BOX2_URL=http://box2.internal:8082
export BOX2_ENABLED=false  # On-demand
export BOX3_URL=http://box3.internal:8083
export BOX3_ENABLED=true   # Always-on
export BOX4_URL=http://box4.internal:8090
export BOX4_ENABLED=false  # On-demand
export BOX4_AUTO_START=true
export BOX4_IDLE_TIMEOUT=7200  # 2 hours
export MCP_SHARED_SECRET=<32-byte-key>
export AWS_REGION=us-east-1
export BOX4_INSTANCE_ID=i-xxxxx
```

### Box 3 (Vision Workers)
```bash
export OLLAMA_NUM_PARALLEL=3
export OLLAMA_MAX_LOADED_MODELS=3
export OLLAMA_NUM_GPU=1
export PARAH_URL=http://localhost:8001  # Visual Sovereign
export FIGMA_MCP_URL=http://localhost:8086
```

---

## Next Steps

1. ✅ Finalize model selections
2. ⏳ Create Box 3 MCP wrapper stubs (vision, voice, browser)
3. ⏳ Test Box 1 → Box 3 delegation locally
4. ⏳ Wire Ollama into queue `executeAgent()`
5. ⏳ Create Terraform deployment scripts
6. ⏳ Implement Phase 2 supplier harvesting workflow

---

**Status**: Architecture finalized, ready for Box 3 MCP wrapper implementation.
