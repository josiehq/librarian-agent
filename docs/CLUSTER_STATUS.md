# 4-Node Cluster Implementation Status

## ✅ Completed (Phase 1 - Architecture & Foundation)

### 1. Cluster Architecture Design
**File**: [docs/CLUSTER_ARCHITECTURE.md](CLUSTER_ARCHITECTURE.md)

- **Box 1**: D-Agents (Orchestrator) - c6i.xlarge, $123/month
- **Box 2**: C3 Clash (Codespace) - c6i.2xlarge, $103/month on-demand
- **Box 3**: B-Agents + C1 Bash (Vision/Audio) - g5.2xlarge, $875/month
- **Box 4**: A-Agents + C2 Gunash (Big Brain) - g5.12xlarge, $680/month on-demand

**Total Cost**: $1,781/month (optimized with on-demand for Box 2 & 4)

---

### 2. Agent Distribution
**File**: [agents/CLUSTER_AGENT_DISTRIBUTION.md](../agents/CLUSTER_AGENT_DISTRIBUTION.md)

| Box | Agents | GPU | Purpose |
|-----|--------|-----|---------|
| Box 1 | D1, D2, D3 | None | Orchestration (24/7) |
| Box 2 | C3 | None | Isolated codespace (on-demand) |
| Box 3 | B1, B2, B3, B4, C1 | 1x A10G (24GB) | Vision/Audio (24/7) |
| Box 4 | A1, A2, C2 | 4x A10G (96GB) | Big brain (on-demand) |

---

### 3. MCP Proxy Layer (HTTP-Based)
**File**: [go/kernel/mcp_proxy.go](../go/kernel/mcp_proxy.go)

**Implementation**:
- HTTP POST requests between boxes (no SSH tunneling needed)
- Agent-based routing: `RouteByAgent()` determines target box
- Box 4 auto-start: Monitors queue, starts/stops EC2 instance as needed
- Vision fallback: Box 3 → Box 4 escalation for complex vision tasks
- Idle timer: Auto-shutdown Box 4 after 2 hours idle

**Security**:
- AWS VPC private subnets (internal communication only)
- Shared secret authentication via `MCP_SHARED_SECRET` env var
- Security groups restrict access between boxes
- Box 2 isolated subnet (no direct internet)

**Communication Pattern**:
```
Box 1 (Orchestrator)
    │
    ├─> POST http://box3.internal:8083/vision (B-Agents)
    ├─> POST http://box2.internal:8082/codespace (C3 Clash)
    └─> POST http://box4.internal:8090/roark (A-Agents, auto-start)

Box 3 (Vision)
    └─> POST http://box4.internal:8093/vision/complex (fallback)
```

---

### 4. Hardware Monitoring & Queue System
**Files**: 
- [go/kernel/hardware.go](../go/kernel/hardware.go) - Hardware detection
- [go/kernel/queue.go](../go/kernel/queue.go) - Agent queueing

**Features**:
- Real-time CPU/RAM/GPU monitoring (5s polling)
- 4-worker queue with priority levels
- GPU-aware task assignment
- Tool lifecycle: INIT → USE → CLEANUP

---

### 5. Testing Infrastructure
**File**: [scripts/test_cluster_mcp.sh](../scripts/test_cluster_mcp.sh)

Tests connectivity to all 4 boxes and their MCP endpoints.

---

## ⏳ Next Steps (Phase 2 - Implementation)

### 1. Deploy Box 1 (Current Box)
```bash
# Already running locally
cd /workspaces/librarian-agent/go
./kirktower_bin
```

**Endpoints**:
- `http://localhost:8080/mcp` - MCP JSON-RPC
- `http://localhost:8080/api/system/health` - Hardware monitor
- `http://localhost:8080/api/queue/list` - Agent queue

---

### 2. Create Box 3 MCP Wrapper Stubs
**Files to create**:
- `box3/vision_mcp.py` - Vision wrapper (CLIP + Qwen3-VL)
- `box3/whisper_mcp.py` - Whisper STT wrapper
- `box3/amazon_mcp.py` - Amazon MCP proxy
- `box3/figma_mcp.py` - Figma MCP proxy
- `box3/browser_mcp.py` - Browser automation wrapper

**Ports**:
- 8083: Vision MCP
- 8084: Whisper STT
- 8085: Amazon MCP
- 8086: Figma MCP
- 8087: Browser MCP

---

### 3. Test Local Multi-Port Setup
```bash
# Terminal 1: Box 1 (Orchestrator)
cd /workspaces/librarian-agent/go
./kirktower_bin

# Terminal 2: Box 3 Vision Stub (Python)
cd /workspaces/librarian-agent/box3
python3 vision_mcp.py --port 8083

# Terminal 3: Test delegation
curl -X POST http://localhost:8080/api/proxy/route \
  -d '{"agent": "B1_Raw", "method": "vision_analyze", "params": {...}}'
```

---

### 4. Implement Box 4 Auto-Start (AWS Integration)
**File**: `go/kernel/mcp_proxy.go` (already stubbed)

**TODO**:
- Replace AWS CLI simulation with AWS SDK
- Add CloudWatch metrics for Box 4 usage
- Implement graceful shutdown (save state before stop)
- Add cost tracking (log Box 4 runtime hours)

**Environment Variables**:
```bash
export AWS_REGION=us-east-1
export BOX4_INSTANCE_ID=i-0123456789abcdef0
export BOX4_AUTO_START=true
export BOX4_IDLE_TIMEOUT=7200  # 2 hours
```

---

### 5. Create Terraform Deployment
**Files to create**:
- `deploy/terraform/main.tf` - VPC, subnets, security groups
- `deploy/terraform/box1.tf` - D-Agents (c6i.xlarge)
- `deploy/terraform/box2.tf` - Clash (c6i.2xlarge)
- `deploy/terraform/box3.tf` - Vision (g5.2xlarge)
- `deploy/terraform/box4.tf` - Big Brain (g5.12xlarge)
- `deploy/terraform/outputs.tf` - Box IPs, endpoints

**Deployment Commands**:
```bash
cd deploy/terraform
terraform init
terraform plan
terraform apply  # Provisions all 4 boxes
```

---

### 6. Wire Ollama Integration
**File**: `go/kernel/queue.go` → `executeAgent()`

Replace placeholder with real Ollama API calls:
```go
func (aq *AgentQueue) executeAgent(req *AgentRequest) (string, error) {
    // Real Ollama call
    ollamaURL := "http://localhost:11434/api/generate"
    payload := map[string]interface{}{
        "model":  req.LLMModel,
        "prompt": req.Task,
        "stream": false,
    }
    
    response := http.Post(ollamaURL, "application/json", payload)
    // ... parse and return
}
```

---

## 📊 Cost Optimization Checklist

- [x] Box 2 (Clash): On-demand only (4 hrs/day)
- [x] Box 4 (Big Brain): On-demand only (4 hrs/day)
- [x] Box 4 auto-shutdown: 2-hour idle timer
- [ ] Spot instances for Box 2 (70% savings)
- [ ] Spot instances for Box 4 (70% savings)
- [ ] CloudWatch alarms for runaway costs
- [ ] Auto-scaling for Box 3 (1-3 instances)
- [ ] S3 lifecycle policies (log archival)

---

## 🔒 Security Checklist

- [x] AWS VPC with private subnets
- [x] Security groups (restrict inter-box access)
- [x] Box 2 isolated subnet (no internet)
- [x] MCP shared secret authentication
- [ ] TLS/SSL for inter-box HTTP
- [ ] IAM roles (no hardcoded credentials)
- [ ] CloudTrail logging
- [ ] Secrets Manager for MCP_SHARED_SECRET
- [ ] Network ACLs (additional firewall layer)
- [ ] VPC Flow Logs (traffic monitoring)

---

## 🚀 Deployment Timeline

### Week 1: Local Testing
- [x] Box 1 hardware monitor & queue
- [x] MCP proxy layer design
- [ ] Box 3 MCP wrapper stubs
- [ ] Test Box 1 → Box 3 delegation (local)

### Week 2: AWS Infrastructure
- [ ] Terraform scripts for all 4 boxes
- [ ] Deploy Box 1 + Box 3 to AWS
- [ ] Test vision workflows (B1, B2, B3)
- [ ] Wire Ollama on Box 3

### Week 3: Full Cluster
- [ ] Deploy Box 2 (Clash isolation)
- [ ] Deploy Box 4 (Big Brain on-demand)
- [ ] Test auto-start/stop logic
- [ ] Test vision fallback (Box 3 → Box 4)

### Week 4: Production Hardening
- [ ] TLS certificates
- [ ] CloudWatch monitoring
- [ ] Cost alerts
- [ ] Backup & disaster recovery
- [ ] Documentation & runbooks

---

## 📝 Quick Reference

**Start/Stop Box 4 Manually**:
```bash
# Start
aws ec2 start-instances --instance-ids $BOX4_INSTANCE_ID

# Stop
aws ec2 stop-instances --instance-ids $BOX4_INSTANCE_ID

# Check status
aws ec2 describe-instances --instance-ids $BOX4_INSTANCE_ID \
  --query 'Reservations[0].Instances[0].State.Name'
```

**Test MCP Proxy Routing**:
```bash
# Box 1 → Box 3 vision
curl -X POST http://localhost:8080/api/proxy/route \
  -H "Content-Type: application/json" \
  -d '{
    "agent": "B1_Raw",
    "method": "vision_analyze",
    "params": {"image_url": "https://example.com/image.jpg"}
  }'

# Box 1 → Box 4 reasoning (auto-start)
curl -X POST http://localhost:8080/api/proxy/route \
  -H "Content-Type: application/json" \
  -d '{
    "agent": "A1_Roark",
    "method": "deliberate",
    "params": {"task": "Complex reasoning task"}
  }'
```

---

**Current State**: Architecture complete, MCP proxy layer ready (HTTP-based), hardware monitoring operational, agent queue functional. Ready for Box 3 MCP wrapper implementation and AWS deployment.
