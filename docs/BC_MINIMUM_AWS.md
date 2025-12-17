# B-C Server (Without A-Agents): Minimum AWS Instance

## Architecture Split

**New setup**: A-agents separated to Google Cloud, B-C on smallest AWS EC2

### Box Distribution
- **Box 1 (D-agents)**: Flexible (Codespace/local/AWS)
- **Box 2 (B-C agents)**: AWS EC2 - **WHAT WE'RE CALCULATING**
- **Box 3 (Clash)**: GitHub Codespace 4-core
- **Google Cloud Dev**: A-agents (Qwen3-80B + Cogito-109B)

---

## Box 2 (B-C AWS) Models Only

### B-Agent Tools
```
nemotron-ocr-v1 (NVIDIA)
- Purpose: Vision/OCR for product images
- VRAM: 8 GB

whisper-large-v3 (OpenAI)
- Purpose: Voice transcription
- VRAM: 3 GB

Olmo-3-7B-Think Q4 (AllenAI)
- Purpose: Browser automation (Playwright script generation)
- VRAM: 4 GB
```

### C-Agent Models
```
Olmo-3-7B-Think Q4 (already counted above)
- Purpose: C1 Bash shell automation
- Shared with B1 browser automation

C2 Clash: REAP-25B → Separate Codespace ✅
C3 Gunash: Cogito-109B → Google Cloud with A-agents ✅
```

---

## Total VRAM for B-C Box

```
nemotron-ocr-v1:     8 GB
whisper-large-v3:    3 GB
Olmo-3-7B-Think Q4:  4 GB
─────────────────────────
Total:              15 GB
```

**With overhead**: ~17 GB safely

---

## AWS Instance Options

### **Option 1: g5.xlarge** ✅ **RECOMMENDED**
- **GPU**: 1x NVIDIA A10G (**24 GB VRAM**)
- **vCPU**: 4
- **RAM**: 16 GB
- **Network**: 10 Gbps
- **Cost**:
  - On-demand: $1.006/hr
  - **24/7**: $1.006 × 24 × 30 = **$723/month**
  - **12 hrs/day**: $1.006 × 12 × 30 = **$362/month**
  - **8 hrs/day**: $1.006 × 8 × 30 = **$241/month**

**Fits**: 
- ✅ 15 GB models / 24 GB VRAM = 63% utilization
- ✅ 9 GB headroom for concurrent operations
- ✅ Can run all 3 models simultaneously

**Verdict**: **Perfect fit** - smallest GPU instance, plenty of room

---

### **Option 2: g5.2xlarge** (Overkill)
- **GPU**: 1x NVIDIA A10G (**24 GB VRAM**)
- **vCPU**: 8
- **RAM**: 32 GB
- **Cost**: $1.212/hr = **$873/month** (24/7)

**Problem**: Same GPU as g5.xlarge, just more CPU/RAM
- ❌ Paying extra for CPU you don't need
- ✅ VRAM same as g5.xlarge (24 GB)

**Verdict**: ❌ **Unnecessary** - g5.xlarge has same GPU

---

### **Option 3: g4dn.xlarge** (Older GPU)
- **GPU**: 1x NVIDIA T4 (**16 GB VRAM**)
- **vCPU**: 4
- **RAM**: 16 GB
- **Cost**: $0.526/hr = **$379/month** (24/7)

**Fits**:
- ✅ 15 GB / 16 GB = 94% utilization
- ⚠️ Only 1 GB headroom (tight!)
- ⚠️ Older/slower GPU than A10G

**Verdict**: ⚠️ **Possible but tight** - saves $344/mo vs g5.xlarge 24/7

---

### **Option 4: p3.2xlarge** (Expensive)
- **GPU**: 1x NVIDIA V100 (16 GB)
- **Cost**: $3.06/hr = **$2,203/month** (24/7)

**Problem**: 
- ❌ **3x more expensive** than g5.xlarge
- ❌ Same VRAM as g4dn.xlarge but way pricier

**Verdict**: ❌ **Terrible value**

---

### **Option 5: CPU-only (t3a.xlarge)** - NOPE
- **No GPU**: Would need CPU inference
- **Problem**: Vision/voice models need GPU
  - nemotron-ocr: ~50x slower on CPU
  - whisper-large-v3: ~10x slower on CPU
  - Olmo-3-7B: ~20x slower on CPU

**Verdict**: ❌ **Not viable** - B-agents need GPU for real-time

---

## Recommendation

### **g5.xlarge is the smallest viable option** ✅

**Why?**
1. **Perfect VRAM fit**: 15 GB needed, 24 GB available (63% usage)
2. **Cost-effective**: $723/mo (24/7) or $241/mo (8hr/day)
3. **Modern GPU**: A10G is 2-3x faster than T4
4. **Headroom**: 9 GB spare for concurrent operations

**Alternative if budget is tight**:
- **g4dn.xlarge** ($379/mo 24/7): Saves $344/mo but:
  - Only 1 GB VRAM spare (94% usage)
  - Older/slower T4 GPU
  - Risk of OOM if models grow

---

## Final 4-Box Architecture

### **Box 1: D-Agents (Orchestration)**
- Instance: Flexible (Codespace/local/t3a.xlarge)
- Models: rnj-1:8b + nemotron-cascade:8b
- Cost: **$0-$108/month**

### **Box 2: B-C Agents (Vision/Voice/Browser)** ⭐
- Instance: **AWS g5.xlarge** (1x A10G, 24 GB VRAM)
- Models: nemotron-ocr + whisper-large-v3 + Olmo-3-7B
- Cost: **$241/month** (8hr/day) or **$723/month** (24/7)

### **Box 3: Clash (Code Generation)**
- Instance: GitHub Codespace 4-core
- Model: REAP-25B
- Cost: **$0-$87/month**

### **Google Cloud: A-Agents (Big Brain)**
- Instance: GCP with GPU (Vertex AI or Cloud Workstation)
- Models: Qwen3-Next-80B + Cogito-109B
- Cost: Variable (check GCP pricing)

---

## Usage-Based Cost Scenarios

### **Scenario 1: Development (8 hrs/day)**
```
Box 1 (Codespace):    $87/mo
Box 2 (g5.xlarge):   $241/mo (8hr/day)
Box 3 (Codespace):     $0/mo (free tier)
Google Cloud A-agents: TBD
──────────────────────────────
Total AWS:           $241/mo
Total w/ Codespace:  $328/mo
```

### **Scenario 2: Production (24/7)**
```
Box 1 (t3a.xlarge):  $108/mo
Box 2 (g5.xlarge):   $723/mo (24/7)
Box 3 (Codespace):    $87/mo
Google Cloud A-agents: TBD
──────────────────────────────
Total AWS:           $831/mo
Total w/ Codespace:  $918/mo
```

### **Scenario 3: Hybrid (Box 2 only 12hr/day)**
```
Box 1 (Codespace):    $87/mo
Box 2 (g5.xlarge):   $362/mo (12hr/day)
Box 3 (free tier):     $0/mo
Google Cloud A-agents: TBD
──────────────────────────────
Total:               $449/mo (+ GCP)
```

---

## GCP A-Agents Estimate

For Qwen3-80B (45 GB) + Cogito-109B (35 GB):

### **Option 1: GCP Vertex AI Workbench**
- Instance: n1-standard-8 + 1x A100 (80 GB)
- Cost: ~$3.67/hr = ~$440/mo (4hr/day)
- Fits both models with 80 GB VRAM

### **Option 2: GCP Cloud Workstation**
- Similar pricing to Vertex AI
- Better dev experience

### **Option 3: Google Colab Pro+ ($50/mo)**
- Access to A100 GPUs
- Limited hours (unclear quota)
- Cheapest if it works!

**Estimated GCP Cost**: $50-$440/month depending on usage

---

## Grand Total Cost

### **Development Setup (8hr/day)**
```
AWS g5.xlarge (Box 2):      $241/mo
Codespace Box 1+3:           $87/mo
GCP A-agents (Colab Pro+):   $50/mo
────────────────────────────────────
Total:                      $378/mo
```

### **Production Setup (24/7 Box 2, 4hr/day GCP)**
```
AWS g5.xlarge (Box 2):      $723/mo
AWS t3a.xlarge (Box 1):     $108/mo
Codespace (Box 3):           $87/mo
GCP A-agents (4hr/day):     $440/mo
────────────────────────────────────
Total:                    $1,358/mo
```

---

## Answer to Your Question

**Smallest AWS EC2 for B-C server (without Cogito+Qwen3)**: 

## **g5.xlarge** ✅

**Specs**:
- 1x A10G GPU (24 GB VRAM)
- 4 vCPU, 16 GB RAM
- Fits: nemotron-ocr (8GB) + whisper-large-v3 (3GB) + Olmo-3-7B (4GB)
- Usage: 15 GB / 24 GB (63%)

**Cost**:
- 24/7: **$723/month**
- 8 hrs/day: **$241/month**

**Can't go smaller without**: CPU-only (50x slower) or insufficient VRAM

---

## Next Steps

1. ✅ Calculate smallest AWS for B-C
2. ⏳ Set up GCP instance for A-agents (Qwen3+Cogito)
3. ⏳ Update routing in Box 1 to forward A-agent tasks to GCP
4. ⏳ Test B-C server on g5.xlarge
5. ⏳ Deploy and verify all cross-box communication
