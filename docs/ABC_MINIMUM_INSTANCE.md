# Minimum AWS Instance for A-B-C Server

## VRAM Requirements Analysis

### Models on A-B-C Box

#### **A-Agents (Big Brain)**
```
Qwen3-Next-80B-A3B-Thinking (Q4_K_M)
- Base: 80B parameters
- Q4 quantized: ~40-45 GB VRAM
- Used by: A1 Josie, A2 Roark

Cogito-v2-109B-MoE (Q4_K_M)
- Base: 109B parameters (MoE architecture)
- Active parameters: ~25-30B per forward pass
- Q4 quantized: ~30-35 GB VRAM (MoE efficient!)
- Used by: A2 Roark, C3 Gunash
```

#### **B-Agent Tools**
```
nemotron-ocr-v1
- Vision OCR model (NVIDIA)
- VRAM: ~8 GB

whisper-large-v3
- Audio transcription
- VRAM: ~3 GB

Olmo-3-7B-Think (Q4_K_M)
- Browser automation (shared with C1)
- Q4 quantized: ~4 GB
```

#### **C-Agents (Code)**
```
Olmo-3-7B-Think (Q4_K_M)
- Already counted above
- Used by: C1 Bash + B1 browser automation
```

---

## Total VRAM Budget

### **Peak Load (All Models Loaded)**
```
Qwen3-Next-80B Q4:     45 GB
Cogito-109B MoE Q4:    35 GB
nemotron-ocr-v1:        8 GB
whisper-large-v3:       3 GB
Olmo-3-7B-Think Q4:     4 GB
───────────────────────────
Total:                 95 GB
```

### **Typical Load (NUM_PARALLEL=3)**
```
Slot 1: Qwen3-80B      45 GB
Slot 2: Olmo-3-7B       4 GB
Slot 3: whisper         3 GB
───────────────────────────
Concurrent:            52 GB

(Cogito and nemotron-ocr loaded on-demand)
```

---

## AWS Instance Options

### **Option 1: g5.12xlarge** ✅ **RECOMMENDED**
- **GPUs**: 4x NVIDIA A10G (96 GB VRAM total)
- **vCPU**: 48
- **RAM**: 192 GB
- **Network**: 10 Gbps
- **Cost**: 
  - On-demand: $5.67/hr
  - 4 hrs/day: **$680/month**
  - 24/7: $4,100/month

**Fits**:
- ✅ All 5 models loaded simultaneously
- ✅ 95 GB / 96 GB = 99% utilization (perfect!)
- ✅ No model swapping delays
- ✅ Can run 3 models concurrently with headroom

**Verdict**: **Best option** - fits everything, fast, no compromises

---

### **Option 2: g5.8xlarge** (24 GB VRAM)
- **GPUs**: 1x NVIDIA A10G (24 GB VRAM)
- **vCPU**: 32
- **RAM**: 128 GB
- **Cost**: $1.006/hr = **$121/month** (4hr/day)

**Problem**: 
- ❌ Cannot fit Qwen3-80B (needs 45 GB)
- ❌ Cannot fit Cogito-109B (needs 35 GB)
- ⚠️ Could fit smaller models only

**Workarounds**:
1. **Aggressive quantization** (Q3_K_M):
   - Qwen3-80B Q3: ~30 GB (might fit)
   - Cogito-109B Q3: ~23 GB (fits!)
   - Quality loss: ~15-20%

2. **Model swapping**:
   - Load/unload between tasks
   - Swap time: 10-15 seconds per model
   - Terrible UX

**Verdict**: ❌ **Too small** - need 45GB for Qwen3-80B

---

### **Option 3: p3.2xlarge** (16 GB VRAM)
- **GPU**: 1x NVIDIA V100 (16 GB)
- **Cost**: $3.06/hr = **$367/month** (4hr/day)

**Problem**:
- ❌ Cannot fit any of the large models
- ❌ More expensive than g5.8xlarge with less VRAM

**Verdict**: ❌ **Completely inadequate**

---

### **Option 4: g5.48xlarge** (192 GB VRAM)
- **GPUs**: 8x NVIDIA A10G (192 GB VRAM total)
- **Cost**: $16.29/hr = **$1,955/month** (4hr/day)

**Advantage**:
- ✅ 2x the VRAM needed
- ✅ Could run 6 models concurrently

**Problem**:
- ❌ **3x more expensive** than g5.12xlarge
- ❌ Overkill - wasting 97 GB VRAM

**Verdict**: ❌ **Unnecessary** - g5.12xlarge is perfect

---

### **Option 5: GCP A100 40GB**
- **GPU**: 1x NVIDIA A100 (40 GB HBM2)
- **Cost**: ~$3.67/hr = **$440/month** (4hr/day)

**Problem**:
- ❌ Cannot fit Qwen3-80B (45 GB)
- ⚠️ Could fit with Q3 quantization (30 GB)

**Verdict**: ⚠️ **Possible but not ideal**

---

### **Option 6: GCP A100 80GB**
- **GPU**: 1x NVIDIA A100 (80 GB HBM2e)
- **Cost**: ~$4.50/hr = **$540/month** (4hr/day)

**Advantage**:
- ✅ Fits Qwen3-80B (45 GB) + others
- ✅ Faster than A10G
- ❌ Still tight on VRAM (80 GB vs 95 GB needed)

**Verdict**: ⚠️ **Possible** but g5.12xlarge better value

---

## Recommendation

### **g5.12xlarge** is the perfect fit ✅

**Why?**
1. **Exact VRAM match**: 96 GB available, 95 GB needed
2. **Cost-effective**: $680/month for 4hr/day
3. **No compromises**: All models fit without quantization loss
4. **Headroom**: 1 GB spare for system overhead
5. **Multi-model**: Run 3 models concurrently

**Alternative strategies if cost is a concern**:
- **Option A**: Use g5.8xlarge + aggressive Q3 quantization ($121/mo, -15% quality)
- **Option B**: Split A-agents and B-agents again (2 boxes, complexity++)
- **Option C**: Keep g5.12xlarge but reduce usage to 2hr/day ($340/mo)

---

## Final Architecture Summary

### **3-Box Cluster**

**Box 1**: D-agents (Orchestration)
- Instance: Codespace 4-core OR t3a.xlarge
- Cost: **$87/month** (8hr/day)

**Box 2**: A-B-C Merged (Big Brain + Vision + Code)
- Instance: **g5.12xlarge** (4x A10G, 96 GB VRAM)
- Models: Qwen3-80B, Cogito-109B, nemotron-ocr, whisper, Olmo-7B
- Cost: **$680/month** (4hr/day)

**Box 3**: Clash (Code Generation)
- Instance: Codespace 4-core
- Model: REAP-25B
- Cost: **$87/month** (8hr/day) OR **$0** (free tier)

**Total Cost**: $854/month (optimized with Codespace free tier: $767/mo)

---

## Deployment Checklist

- [x] Document new architecture
- [x] Calculate VRAM requirements
- [x] Select g5.12xlarge for Box 2
- [x] Update vision_mcp.py to use nemotron-ocr
- [x] Create Clash Codespace setup
- [ ] Test Qwen3-Next-80B on g5.12xlarge
- [ ] Test Cogito-109B MoE efficiency
- [ ] Verify all 5 models fit in 96 GB
- [ ] Test NUM_PARALLEL=3 concurrency
- [ ] Deploy and benchmark
