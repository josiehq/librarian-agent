# Merged B+C Box Analysis

## Current Setup (Separate)

**Box 2 (B-agents):**
- Instance: g5.xlarge (1x A10G 24GB)
- Model: REAP-25B-A3B (15 GB VRAM)
- Cost: $123/month (4 hrs/day on-demand)
- Usage: Mid-tier reasoning for complex B-agent tasks

**Box 4 (C-agents):**
- Instance: g5.12xlarge (4x A10G 96GB)
- Models: Qwen3:32b (16GB) + Cogito:70b (35GB) + Nemotron-3:22b (11GB) + Command-R:32b (16GB)
- Cost: $680/month (4 hrs/day on-demand)
- Usage: Code generation, review, refactoring

**Total: 2 boxes, $803/month**

---

## Merged B+C Requirements

### VRAM Budget
```
B-agent: REAP-25B         15 GB
C-agents:
  Qwen3:32b              16 GB
  Cogito:70b             35 GB (on-demand)
  Nemotron-3:22b         11 GB
  Command-R:32b          16 GB
────────────────────────────────
Max concurrent (2 slots): 31 GB
Peak (with Cogito):       50 GB
Absolute minimum:         35 GB (for Cogito alone)
```

### Queueing Strategy
With NUM_PARALLEL=2:
- **Slot 1**: REAP-25B (15GB) OR Qwen3 (16GB) OR Cogito (35GB)
- **Slot 2**: Nemotron-3 (11GB) OR Command-R (16GB)

**Typical load**: 15GB + 16GB = 31GB
**Peak load**: Cogito (35GB) alone when needed

---

## AWS Instance Options

### Option 1: Keep g5.12xlarge (Current Box 4)
- **GPUs**: 4x A10G (96 GB VRAM total)
- **Fits**: Everything easily
- **Cost**: $5.67/hr = $680/month (4hrs/day)
- **Savings**: -$123/month (eliminate Box 2)
- **New total**: **$680/month** (vs $803 current)

✅ **Simplest - just move REAP-25B to Box 4**

---

### Option 2: Downsize to g5.8xlarge
- **GPUs**: 1x A10G (24 GB VRAM)
- **Problem**: Can't fit Cogito:70b (needs 35GB)
- **Solution**: Drop Cogito, use only Qwen3 + REAP-25B
- **Cost**: $1.006/hr × 4hrs × 30 = **$121/month**
- **Savings**: **-$682/month** ❌ **LOSES Cogito!**

⚠️ **Too small for full model set**

---

### Option 3: Use g5.2xlarge with quantization
- **GPUs**: 1x A10G (24 GB VRAM)
- **Strategy**: Quantize all models to Q4_K_M
  - REAP-25B Q4: ~8 GB
  - Qwen3:32b Q4: ~8 GB
  - Cogito:70b Q4: ~18 GB (still won't fit with others)
  - Nemotron-3:22b Q4: ~5.5 GB
  - Command-R:32b Q4: ~8 GB
- **Cost**: $0.753/hr × 4hrs × 30 = **$90/month**
- **Tradeoff**: Quality loss from quantization

⚠️ **Possible but quality degraded**

---

### Option 4: Use p3.2xlarge (V100 16GB) with heavy quantization
- **GPU**: 1x V100 (16 GB VRAM)
- **Strategy**: Aggressive Q4 quantization + 1 model at a time
- **Cost**: $3.06/hr × 4hrs × 30 = **$367/month**
- **Problem**: V100 is more expensive AND has less VRAM than A10G

❌ **Worse in every way**

---

## Recommended Configuration

### **Best Option: Merge to g5.12xlarge** ✅

**Hardware**:
- Instance: g5.12xlarge
- GPUs: 4x A10G (96 GB VRAM)
- vCPU: 48
- RAM: 192 GB

**Models**:
```bash
# B-agent mid-tier reasoning
REAP-25B-A3B:     15 GB

# C-agent code generation
Qwen3:32b:        16 GB
Cogito:70b:       35 GB (on-demand for hard tasks)
Nemotron-3:22b:   11 GB
Command-R:32b:    16 GB
```

**Ollama Config**:
```bash
NUM_PARALLEL=3              # Run 3 models simultaneously
OLLAMA_MAX_LOADED_MODELS=5  # Keep all 5 models in VRAM
```

**Cost**:
- On-demand (4 hrs/day): **$680/month**
- 24/7 if needed: $4,100/month

**Savings**:
- Old: Box 2 ($123) + Box 4 ($680) = $803/month
- New: Single box $680/month
- **Save: $123/month** (15% reduction)

---

## New Cluster Architecture

### **3-Box Setup** (Down from 4)

**Box 1 (D-agents + orchestration)**
- Instance: t3a.xlarge (CPU only)
- Models: rnj-1:8b + nemotron-cascade:8b
- Cost: **$108/month**

**Box 2 (B+C agents - MERGED)** ← **New unified box**
- Instance: g5.12xlarge (4x A10G 96GB)
- Models: REAP-25B + Qwen3:32b + Cogito:70b + Nemotron-3:22b + Command-R:32b
- Cost: **$680/month** (4hrs/day)

**Box 3 (Vision/Voice/Browser)**
- Instance: g5.xlarge (1x A10G 24GB)
- Models: deepseek-ocr + whisper-large-v3 + Olmo-3-7B-Think + CLIP
- Cost: **$730/month** (24/7)

**Total: $1,518/month** (vs $1,641 with 4 boxes)
**Savings: $123/month** (7.5% reduction)

---

## Comparison Table

| Config | Boxes | Monthly Cost | Savings | Tradeoffs |
|--------|-------|--------------|---------|-----------|
| **Current (4-box)** | 4 | $1,641 | - | Baseline |
| **Merged to g5.12xlarge** | 3 | **$1,518** | **-$123** | ✅ Simpler, full capability |
| Merged to g5.8xlarge | 3 | $959 | -$682 | ❌ Lose Cogito:70b |
| Merged to g5.2xlarge (Q4) | 3 | $928 | -$713 | ⚠️ Quality loss |

---

## Recommendation

**Go with 3-box merged setup** ✅

**Pros**:
- Simpler architecture (3 boxes instead of 4)
- $123/month savings
- All models available
- No quality loss
- Easier deployment/management

**Cons**:
- Slightly higher risk (B+C on same box)
- If Box 2 goes down, lose both B and C agents

**Deployment**:
Just add REAP-25B to current Box 4, eliminate old Box 2 entirely.
