# 4-Node Cluster Architecture

**Date**: December 17, 2025  
**Status**: 🏗️ **DESIGN PHASE**

---

## Overview

The Librarian Agent system is distributed across **4 specialized nodes** for optimal cost/performance:

```
┌─────────────────────────────────────────────────────────────────┐
│                    CLUSTER TOPOLOGY                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐    ┌──────────────┐    ┌─────────────────┐  │
│  │   BOX 1      │───▶│   BOX 2      │    │    BOX 4        │  │
│  │  D-Agents    │    │   Clash      │◀───│  Big Brain      │  │
│  │ (Orchestr.)  │    │ (Codespace)  │    │ (A-series+C2)   │  │
│  └──────────────┘    └──────────────┘    └─────────────────┘  │
│         │                                          ▲            │
│         │                                          │            │
│         ▼                                          │            │
│  ┌──────────────────────────────────────┐         │            │
│  │        BOX 3                         │─────────┘            │
│  │  B-Agents + Bash + Whisper           │                      │
│  │  (Vision, STT, Code Execution)       │                      │
│  └──────────────────────────────────────┘                      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Box 1: Orchestration & Control Plane

### 🎯 Purpose
Always-on coordination hub. Handles task orchestration, hardware monitoring, agent queueing, and MCP routing.

### 🤖 Agents
- **D1 Puckfairy** - Task dispatch & coordination
- **D2 Diplo** - Channel management & inter-agent communication
- **D3 Waria** - Resource monitoring & meta-cognitive hygiene

### 🔧 Services
- **Kirktower MCP Server** (port 8080)
  - Hardware monitor API
  - Agent queue system
  - MCP tool routing
- **Narnia CLI** (Git operations)
- **PostgreSQL** (state persistence)
- **Redis** (session cache)

### 💻 AWS Instance Recommendation

**Option 1: t3.large** (Cost-optimized, always-on)
- **vCPUs**: 2
- **Memory**: 8 GB
- **Network**: Up to 5 Gbps
- **Cost**: ~$60/month (24/7)
- **Use Case**: Development/staging

**Option 2: c6i.xlarge** (Production, compute-optimized)
- **vCPUs**: 4
- **Memory**: 8 GB
- **Network**: Up to 12.5 Gbps
- **Cost**: ~$123/month (24/7)
- **Use Case**: Production with high concurrency

### 📊 Resource Profile
```yaml
CPU: 10-30% average (spikes to 80% during queue processing)
Memory: 2-4 GB average
Disk: 50 GB SSD (logs + state)
Network: 100 MB/s average (bursts to 500 MB/s)
```

### 🔌 Exposed Endpoints
- `http://box1.internal:8080/mcp` - MCP JSON-RPC
- `http://box1.internal:8080/api/queue/*` - Agent queue
- `http://box1.internal:8080/api/system/health` - Hardware monitoring

---

## Box 2: Clash Codespace (Isolated)

### 🎯 Purpose
Sandboxed code execution environment. Isolated for security (untrusted code generation, GitHub Codespaces integration).

### 🤖 Agents
- **C3 Clash** - GitHub Codespace operations, code sandbox execution

### 🔧 Services
- **GitHub CLI** (`gh`)
- **Docker** (for codespace containers)
- **MCP Wrapper** (port 8082) - Proxies requests to Box 1

### 💻 AWS Instance Recommendation

**Option 1: c6i.2xlarge** (Compute-optimized)
- **vCPUs**: 8
- **Memory**: 16 GB
- **Storage**: 200 GB EBS (gp3)
- **Network**: Up to 12.5 Gbps
- **Cost**: ~$246/month (24/7) OR ~$0.34/hour (on-demand)
- **Use Case**: On-demand for heavy code generation

**Option 2: c7i.2xlarge** (Latest gen, better performance)
- **vCPUs**: 8
- **Memory**: 16 GB
- **Cost**: ~$283/month OR ~$0.39/hour
- **Use Case**: Production with SLA requirements

### 📊 Resource Profile
```yaml
CPU: 5-15% idle, 90-100% during code generation
Memory: 4-8 GB average (Docker containers)
Disk: 100 GB average (codespace clones)
Network: 50 MB/s average (git operations)
```

### 🔒 Security Considerations
- **Isolated VPC** or separate AWS account
- **No direct internet access** (proxy through Box 1)
- **Ephemeral storage** (auto-wipe after tasks)
- **IAM role-based** GitHub access only

### 🔌 Exposed Endpoints
- `http://box2.internal:8082/mcp/clash` - Clash MCP proxy
- `http://box2.internal:8082/codespace/*` - Codespace operations

---

## Box 3: Vision & Audio Workers

### 🎯 Purpose
Mid-tier GPU workload box. Handles product vision, supplier crawling, voice control, and basic code execution.

### 🤖 Agents
- **B1 Raw** - Browser automation & scraping (Qwen3-VL:32b)
- **B2 Vision** - Design analysis (Qwen3-VL:32b)
- **B3 Concrete** - Supplier product analysis (Nemotron-3-Nano:1.7b + CLIP)
- **B4 Kirktower** - Voice control (Whisper-large-v3)
- **C1 Bash** - Shell command generation (REAP-25B-A3B)

### 🔧 Services
- **Ollama** (LLM runtime)
  - Models loaded: `qwen3-vl:32b`, `nemotron-3-nano:1.7b`, `whisper-large-v3`, `reap-25b-a3b`
- **PARAH (Visual Sovereign)** - CLIP embeddings + Playwright scraping
- **MCP Wrappers**:
  - Port 8083: Vision MCP (CLIP + Qwen3-VL)
  - Port 8084: Whisper STT
  - Port 8085: Amazon MCP
  - Port 8086: Figma MCP
  - Port 8087: Browser MCP
- **ChromeDriver** (for Playwright/Selenium)

### 💻 AWS Instance Recommendation

**Option 1: g5.2xlarge** (Single A10G GPU - RECOMMENDED)
- **GPU**: 1x NVIDIA A10G (24 GB VRAM)
- **vCPUs**: 8
- **Memory**: 32 GB
- **Storage**: 450 GB NVMe SSD
- **Network**: Up to 10 Gbps
- **Cost**: ~$1.21/hour (~$875/month 24/7)
- **Use Case**: Production, balanced cost/performance

**Option 2: g5.xlarge** (Budget option)
- **GPU**: 1x NVIDIA A10G (24 GB VRAM)
- **vCPUs**: 4
- **Memory**: 16 GB
- **Cost**: ~$1.01/hour (~$730/month 24/7)
- **Use Case**: Development, single-agent workloads

**Option 3: g5.4xlarge** (High concurrency)
- **GPU**: 1x NVIDIA A10G (24 GB VRAM)
- **vCPUs**: 16
- **Memory**: 64 GB
- **Cost**: ~$1.62/hour (~$1,170/month 24/7)
- **Use Case**: Production, multiple concurrent vision tasks

### 📊 Resource Profile
```yaml
CPU: 20-40% average (browser automation peaks at 80%)
Memory: 16-24 GB average (Qwen3-VL loaded)
GPU VRAM: 12-18 GB average (Qwen3-VL + Whisper)
Disk: 200 GB average (model cache + browser profiles)
Network: 200 MB/s average (video streaming, image downloads)
```

### 🧠 Model Loading Strategy
```python
# Models loaded on-demand via queue system
# VRAM budget: 24 GB total

qwen3_vl_32b = 12 GB       # Vision tasks (B1, B2)
whisper_large_v3 = 4 GB    # Voice control (B4)
nemotron_nano = 768 MB     # Concrete lightweight (B3)
reap_25b = 10 GB           # Bash code gen (C1)

# Strategy: Load/unload via INIT→USE→CLEANUP lifecycle
# Max concurrent: 2 models (e.g., Qwen3-VL + Whisper = 16 GB)
```

### 🔌 Exposed Endpoints
- `http://box3.internal:8083/vision` - Vision MCP (CLIP + Qwen3-VL)
- `http://box3.internal:8084/stt` - Whisper STT
- `http://box3.internal:8085/amazon` - Amazon MCP proxy
- `http://box3.internal:8086/figma` - Figma MCP proxy
- `http://box3.internal:8087/browser` - Browser automation

---

## Box 4: Big Brain (On-Demand)

### 🎯 Purpose
High-end GPU for complex reasoning, deliberation chains, and advanced vision. **Only turned on when needed** to save costs.

### 🤖 Agents
- **A1 Roark** - Multi-stage reasoning (Qwen3:32b → Cogito:70b → Qwen3:32b)
- **A2 Josie** - Code review & refactoring (Nemotron-3:22b)
- **C2 Gunash** - Git operations & changelog generation (Command-R:32b)
- **Vision Server** - Complex vision fallback (Qwen3-VL:32b + GroundingDINO)

### 🔧 Services
- **Ollama** (LLM runtime)
  - Models loaded: `qwen3:32b`, `cogito:70b`, `nemotron-3:22b`, `command-r:32b`, `qwen3-vl:32b`
- **MCP Wrappers**:
  - Port 8090: Roark deliberation chain
  - Port 8091: Josie code review
  - Port 8092: Gunash git ops
  - Port 8093: Vision fallback (complex reasoning)

### 💻 AWS Instance Recommendation

**Option 1: g5.12xlarge** (4x A10G - RECOMMENDED)
- **GPU**: 4x NVIDIA A10G (96 GB total VRAM)
- **vCPUs**: 48
- **Memory**: 192 GB
- **Storage**: 3.8 TB NVMe SSD
- **Network**: 40 Gbps
- **Cost**: ~$5.67/hour (~$4,100/month 24/7)
- **On-Demand Use**: ~$45 for 8-hour workday
- **Use Case**: Production, complex reasoning chains

**Option 2: p4d.24xlarge** (8x A100 - MAXIMUM POWER)
- **GPU**: 8x NVIDIA A100 (320 GB total VRAM)
- **vCPUs**: 96
- **Memory**: 1.1 TB
- **Network**: 400 Gbps EFA
- **Cost**: ~$32.77/hour (~$23,700/month 24/7)
- **On-Demand Use**: ~$260 for 8-hour workday
- **Use Case**: Critical production, research-grade reasoning

**Option 3: g5.8xlarge** (Budget big brain)
- **GPU**: 1x NVIDIA A10G (24 GB VRAM)
- **vCPUs**: 32
- **Memory**: 128 GB
- **Cost**: ~$2.45/hour (~$1,770/month 24/7)
- **Use Case**: Development, single-agent reasoning

### 📊 Resource Profile
```yaml
CPU: 10-20% idle, 60-90% during reasoning chains
Memory: 32-64 GB average (large context windows)
GPU VRAM: 40-70 GB average (Cogito:70b + Qwen3-VL)
Disk: 500 GB average (model cache)
Network: 500 MB/s average (model transfers from Box 3)
```

### 🧠 Model Loading Strategy
```python
# VRAM budget: 96 GB total (g5.12xlarge with 4x A10G)

# A1 Roark deliberation chain
qwen3_32b = 12 GB          # GPU 0: Fast reasoning
cogito_70b = 28 GB         # GPU 1+2: Deep deliberation
qwen3_32b_copy = 12 GB     # GPU 0: Synthesis (shared)

# A2 Josie
nemotron_3_22b = 8 GB      # GPU 3: Code review

# C2 Gunash
command_r_32b = 12 GB      # GPU 3: Git operations

# Vision fallback
qwen3_vl_32b = 12 GB       # GPU 3: Complex vision (on-demand)

# Total: ~84 GB used, 12 GB free for overhead
```

### 💰 Cost Optimization Strategy

**On-Demand Pattern** (Recommended):
```bash
# Turn on only when needed
aws ec2 start-instances --instance-ids i-box4

# Auto-shutdown after 2 hours of idle
# Estimated monthly cost: ~$500 (4 hours/day, 5 days/week)
```

**Spot Instances** (70% savings):
```bash
# Use spot instances for non-critical work
# Cost: ~$1.70/hour (vs $5.67)
# Risk: Can be interrupted (save state frequently)
```

### 🔌 Exposed Endpoints
- `http://box4.internal:8090/roark` - Roark deliberation chain
- `http://box4.internal:8091/josie` - Josie code review
- `http://box4.internal:8092/gunash` - Gunash git operations
- `http://box4.internal:8093/vision/complex` - Vision fallback

---

## Inter-Box MCP Communication

### 🌐 Network Topology

```
┌─────────────────────────────────────────────────────────────┐
│                    AWS VPC (10.0.0.0/16)                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  [Public Subnet 10.0.1.0/24]                                │
│     ├─ NAT Gateway                                          │
│     └─ Load Balancer (user-facing)                          │
│                                                             │
│  [Private Subnet 10.0.10.0/24]                              │
│     ├─ Box 1 (10.0.10.10) - D-agents                        │
│     ├─ Box 3 (10.0.10.30) - B-agents + C1                   │
│     └─ RDS PostgreSQL (10.0.10.5)                           │
│                                                             │
│  [Isolated Subnet 10.0.20.0/24]                             │
│     └─ Box 2 (10.0.20.20) - Clash (no direct internet)     │
│                                                             │
│  [On-Demand Subnet 10.0.30.0/24]                            │
│     └─ Box 4 (10.0.30.40) - A-agents + C2 (when running)   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 📡 MCP Wrapper Design

**Box 1 → Box 3** (Vision requests):
```python
# Box 1: kirktower.go delegates vision tasks
def delegate_vision_task(agent, task):
    response = requests.post(
        "http://box3.internal:8083/vision",
        json={
            "agent": agent,
            "task": task,
            "model": "qwen3-vl:32b",
            "priority": 7
        }
    )
    return response.json()
```

**Box 1 → Box 4** (Big brain requests):
```python
# Box 1: Check if Box 4 is online before routing
def delegate_reasoning_task(agent, task):
    # 1. Check if Box 4 is online
    try:
        health = requests.get("http://box4.internal:8090/health", timeout=2)
        if health.status_code != 200:
            return {"error": "Box 4 offline"}
    except:
        # Auto-start Box 4 if needed
        start_box4()
        wait_for_boot(timeout=120)
    
    # 2. Submit reasoning task
    response = requests.post(
        "http://box4.internal:8090/roark",
        json={"task": task, "chain": "full"}
    )
    return response.json()
```

**Box 3 → Box 4** (Vision fallback):
```python
# Box 3: CLIP fails, escalate to Box 4
def vision_fallback(image_url, question):
    # 1. Try local CLIP first (fast, cheap)
    clip_result = local_clip_inference(image_url)
    if clip_result["confidence"] > 0.85:
        return clip_result
    
    # 2. Escalate to Box 4 (slow, expensive)
    response = requests.post(
        "http://box4.internal:8093/vision/complex",
        json={
            "image_url": image_url,
            "question": question,
            "model": "qwen3-vl:32b",
            "mode": "detailed"
        }
    )
    return response.json()
```

### 🔐 Security & Authentication

**Inter-Box Authentication**:
```bash
# Each box has a shared secret for internal MCP calls
export MCP_SHARED_SECRET="<32-byte-random-key>"

# Box 1 generates signed tokens
curl -X POST http://box3.internal:8083/vision \
  -H "Authorization: Bearer <JWT-signed-by-box1>" \
  -d '{"task": "..."}'
```

**Firewall Rules** (AWS Security Groups):
```hcl
# Box 1 (Orchestrator)
ingress {
  from_port   = 8080
  to_port     = 8080
  protocol    = "tcp"
  cidr_blocks = ["10.0.0.0/16"]  # Internal VPC only
}

# Box 3 (Vision)
ingress {
  from_port   = 8083
  to_port     = 8087
  protocol    = "tcp"
  cidr_blocks = ["10.0.10.10/32"]  # Only from Box 1
}

# Box 4 (Big Brain)
ingress {
  from_port   = 8090
  to_port     = 8093
  protocol    = "tcp"
  cidr_blocks = ["10.0.10.10/32", "10.0.10.30/32"]  # Box 1 + Box 3
}
```

---

## Cost Analysis

### Monthly Estimates (24/7 Operation)

| Box | Instance | Monthly Cost | Annual Cost |
|-----|----------|--------------|-------------|
| **Box 1** | c6i.xlarge | $123 | $1,476 |
| **Box 2** | c6i.2xlarge (on-demand 4hr/day) | $103 | $1,236 |
| **Box 3** | g5.2xlarge | $875 | $10,500 |
| **Box 4** | g5.12xlarge (on-demand 4hr/day) | $680 | $8,160 |
| **Storage** | EBS + S3 | $100 | $1,200 |
| **Network** | Data transfer | $50 | $600 |
| **Total** | | **$1,931/month** | **$23,172/year** |

### Optimized Pattern (Recommended)

| Scenario | Box 1 | Box 2 | Box 3 | Box 4 | Monthly Total |
|----------|-------|-------|-------|-------|---------------|
| **Development** | t3.large (24/7) | Spot (2hr/day) | g5.xlarge (24/7) | Off | **$850** |
| **Production** | c6i.xlarge (24/7) | c6i.2xlarge (4hr/day) | g5.2xlarge (24/7) | g5.12xlarge (4hr/day) | **$1,931** |
| **Peak Load** | c6i.xlarge (24/7) | c6i.2xlarge (8hr/day) | g5.4xlarge (24/7) | g5.12xlarge (8hr/day) | **$2,850** |

### Spot Instance Savings

```yaml
Box 2 (Clash): 
  On-Demand: $0.34/hour
  Spot: ~$0.10/hour (70% savings)
  Interruption Risk: Low (non-critical code generation)

Box 4 (Big Brain):
  On-Demand: $5.67/hour
  Spot: ~$1.70/hour (70% savings)
  Interruption Risk: Medium (save reasoning state every 5 min)

Monthly Savings with Spot: ~$600-800/month
```

---

## Deployment Strategy

### Phase 1: Single Box (Current State)
```bash
# Everything on Box 1 (development)
./kirktower_bin  # All agents + models on local machine
```

### Phase 2: Two-Box Split
```bash
# Box 1: D-agents + orchestration
# Box 3: B-agents + vision models
# Deploy: Box 1 → Box 3 → test inter-box MCP
```

### Phase 3: Three-Box with Clash
```bash
# Add Box 2: Clash isolation
# Deploy: Box 1 → Box 3 → Box 2 → test codespace workflows
```

### Phase 4: Four-Box Full Cluster
```bash
# Add Box 4: Big brain (on-demand)
# Deploy: Box 1 → Box 3 → Box 2 → Box 4 (manual start)
# Configure auto-start/stop for Box 4
```

---

## Auto-Scaling Strategy

### Box 3 Auto-Scaling (Vision workers)
```hcl
# Auto Scaling Group for Box 3
min_instances = 1
max_instances = 3
target_cpu_utilization = 70%

# Scale up: When queue depth > 10 requests
# Scale down: When queue empty for 10 minutes
```

### Box 4 Auto-Start/Stop
```python
# Lambda function triggered by queue depth
def check_queue_and_start_box4():
    queue = get_queue_status()
    
    # Start Box 4 if high-priority reasoning task pending
    if queue["high_priority_count"] > 0:
        start_box4()
    
    # Stop Box 4 if idle for 2 hours
    if box4_idle_time() > 7200:
        stop_box4()
```

---

## Next Steps

1. **Create MCP wrapper templates** for inter-box communication
2. **Write deployment scripts** (Terraform + Ansible)
3. **Test Box 1 → Box 3 vision delegation** (local first)
4. **Implement Box 4 auto-start logic** (queue-based)
5. **Set up monitoring** (CloudWatch metrics + Grafana)
6. **Configure cost alerts** (AWS Budgets)

---

## Files to Create

- `go/kernel/mcp_proxy.go` - Inter-box MCP wrapper
- `deploy/terraform/box1.tf` - Box 1 infrastructure
- `deploy/terraform/box2.tf` - Box 2 infrastructure
- `deploy/terraform/box3.tf` - Box 3 infrastructure
- `deploy/terraform/box4.tf` - Box 4 infrastructure
- `scripts/start_box4.sh` - Auto-start Box 4 script
- `scripts/stop_box4.sh` - Auto-stop Box 4 script
- `deploy/ansible/playbook.yml` - Configuration management

---

**Status**: Architecture designed, ready for implementation feedback and refinement.
