# Waria Hardware Detection & Diplo Queue System

## Overview

This document describes the hardware monitoring and agent queueing systems implemented for **D3 Waria** (resource management) and **D1 Diplo** (task orchestration).

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     KIRKTOWER (Port 8080)                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────┐          ┌────────────────────────┐  │
│  │ HardwareMonitor  │◄─────────┤   AgentQueue           │  │
│  │  (D3 Waria)      │          │   (D1 Diplo + Waria)   │  │
│  ├──────────────────┤          ├────────────────────────┤  │
│  │ • CPU Usage      │          │ • 4 Worker Goroutines  │  │
│  │ • Memory Stats   │          │ • Priority Queue       │  │
│  │ • GPU Detection  │          │ • GPU Assignment       │  │
│  │ • VRAM Tracking  │          │ • Tool Lifecycle Mgmt  │  │
│  └──────────────────┘          └────────────────────────┘  │
│           │                              │                 │
│           │ 5s polling                   │ Submits requests│
│           ▼                              ▼                 │
│  /api/system/health         /api/queue/{submit,status,list}│
└─────────────────────────────────────────────────────────────┘
```

## Components

### 1. Hardware Monitor (D3 Waria)

**File**: `go/kernel/hardware.go`

**Purpose**: Continuously tracks system resources to inform scheduling decisions.

**Features**:
- **CPU Monitoring**: Reads `/proc/stat` to calculate real-time CPU usage
- **Memory Tracking**: Parses `/proc/meminfo` for RAM usage (total, used, available)
- **GPU Detection**: Uses `nvidia-smi` to detect NVIDIA GPUs with:
  - VRAM total/used (MB)
  - GPU utilization (%)
  - Temperature (°C)
  - Availability status (< 90% VRAM = available)
- **Auto-refresh**: 5-second polling interval
- **Thread-safe**: RWMutex protects concurrent access

**API Endpoint**:
```bash
GET /api/system/health
```

**Response Example**:
```json
{
  "cpu_cores": 8,
  "cpu_usage_percent": 45.3,
  "memory_total_mb": 32768,
  "memory_used_mb": 16384,
  "memory_percent": 50.0,
  "gpus": [
    {
      "id": 0,
      "name": "NVIDIA RTX 4090",
      "memory_total_mb": 24576,
      "memory_used_mb": 8192,
      "memory_percent": 33.3,
      "utilization_percent": 65.0,
      "temperature_c": 72,
      "available": true
    }
  ],
  "timestamp": "2025-12-17T10:30:00Z"
}
```

**Usage**:
```go
// Find GPU with at least 8GB free
gpuID, err := hwMonitor.FindAvailableGPU(8192)
if err != nil {
    // Fall back to CPU
}
```

---

### 2. Agent Queue (D1 Diplo + D3 Waria)

**File**: `go/kernel/queue.go`

**Purpose**: Manages LLM agent execution with hardware-aware scheduling and lifecycle management.

**Features**:
- **Concurrent Workers**: 4 goroutines process requests in parallel
- **Priority Queue**: 0-10 priority levels (10 = highest)
- **GPU Assignment**: Waria hardware monitor selects best GPU based on VRAM requirements
- **Tool Lifecycle**:
  1. **INIT**: Load LLM model into GPU memory
  2. **USE**: Execute agent task
  3. **CLEANUP**: Unload model to free VRAM
- **Status Tracking**: queued → running → completed/failed
- **Metrics Integration**: Sends completion data to Waria for meta-cognitive analysis

**API Endpoints**:

#### Submit Request
```bash
POST /api/queue/submit
Content-Type: application/json

{
  "agent": "B3_Concrete",
  "task": "Search AliExpress for leather wallet suppliers",
  "llm_model": "qwen3-vl:32b",
  "priority": 8,
  "required_vram_mb": 12288
}
```

**Response**:
```json
{
  "success": true,
  "request_id": "req-1734435000123"
}
```

#### Check Status
```bash
GET /api/queue/status?id=req-1734435000123
```

**Response**:
```json
{
  "id": "req-1734435000123",
  "agent": "B3_Concrete",
  "task": "Search AliExpress for leather wallet suppliers",
  "llm_model": "qwen3-vl:32b",
  "priority": 8,
  "required_vram_mb": 12288,
  "status": "completed",
  "gpu_assigned": 0,
  "submit_time": "2025-12-17T10:30:00Z",
  "start_time": "2025-12-17T10:30:02Z",
  "end_time": "2025-12-17T10:30:05Z",
  "result": "Agent B3_Concrete completed task: Search AliExpress... (model: qwen3-vl:32b, GPU: 0)"
}
```

#### List All Requests
```bash
GET /api/queue/list
```

**Response**:
```json
{
  "queue_depth": 3,
  "total_requests": 15,
  "requests": [...]
}
```

---

## Integration Example

### Scenario: B3 Concrete needs to analyze supplier images

```python
import requests

# 1. Check hardware availability
health = requests.get("http://localhost:8080/api/system/health").json()
print(f"Available GPUs: {len([g for g in health['gpus'] if g['available']])}")

# 2. Submit agent request
request = {
    "agent": "B3_Concrete",
    "task": "Analyze product images from Sunsky supplier page",
    "llm_model": "qwen3-vl:32b",
    "priority": 8,
    "required_vram_mb": 12288,
    "metadata": {
        "supplier": "Sunsky",
        "category": "leather_goods"
    }
}

response = requests.post(
    "http://localhost:8080/api/queue/submit",
    json=request
).json()

request_id = response["request_id"]
print(f"Request submitted: {request_id}")

# 3. Poll for completion
import time
while True:
    status = requests.get(
        f"http://localhost:8080/api/queue/status?id={request_id}"
    ).json()
    
    if status["status"] in ["completed", "failed"]:
        break
    
    print(f"Status: {status['status']} (GPU: {status['gpu_assigned']})")
    time.sleep(1)

print(f"Result: {status['result']}")
```

---

## Tool Lifecycle Pattern

The queue implements the 3-phase lifecycle from `LLM_MODEL_ASSIGNMENTS.md`:

```
┌─────────────────────────────────────────────────────────┐
│ INIT (Model Load)                                       │
│ • Check GPU availability via Waria hardware monitor     │
│ • Assign best GPU based on free VRAM                    │
│ • Load LLM weights into GPU memory                      │
│ • Duration: ~500ms (simulated, actual varies by model)  │
└─────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│ USE (Task Execution)                                    │
│ • Execute agent task with LLM                           │
│ • Stream responses if needed                            │
│ • Track token count for Waria metrics                   │
│ • Duration: varies by task complexity                   │
└─────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│ CLEANUP (Model Unload)                                  │
│ • Unload LLM from GPU memory                            │
│ • Free VRAM for other agents                            │
│ • Report completion metrics to Waria                    │
│ • Update hardware monitor state                         │
└─────────────────────────────────────────────────────────┘
```

**Why This Matters**:
- **Memory Efficiency**: Heavy models (Qwen3-VL:32b = 12GB) can't all stay loaded
- **Resource Sharing**: Multiple agents compete for 2-4 GPUs
- **Latency Trade-off**: Init/cleanup adds ~1s overhead but enables 10+ agents to share hardware

---

## Agent-Specific VRAM Requirements

From `docs/LLM_MODEL_ASSIGNMENTS.md`:

| Agent | Model | VRAM (MB) | GPU Required? |
|-------|-------|-----------|---------------|
| **A1 Roark** | Qwen3:32b → Cogito:70b → Qwen3:32b | 4096 → 28672 → 4096 | Yes (chain) |
| **A2 Josie** | Nemotron-3:22b | 8192 | Yes |
| **B1 Raw** | Qwen3-VL:32b | 12288 | Yes |
| **B2 Vision** | Qwen3-VL:32b | 12288 | Yes |
| **B3 Concrete** | Nemotron-3-Nano:1.7b | 768 | Optional |
| **B4 Kirktower** | Whisper-large-v3 | 4096 | Yes (STT) |
| **C1 Bash** | REAP-25B-A3B | 10240 | Yes |
| **C2 Gunash** | Command-R:32b | 12288 | Yes |
| **C3 Clash** | REAP-25B-A3B | 10240 | Yes |
| **D1 Puckfairy** | rnj-1:8b | 3072 | Optional |
| **D2 Diplo** | Qwen3-mini:2.8b | 1024 | No (CPU-only) |
| **D3 Waria** | None (system monitor) | 0 | No |

**Queue Strategy**:
- High-priority vision tasks (B1, B2, B3) get GPU 0 or 1
- Code generation (A1, C1-C3) prefers GPU 2 or 3
- D-tier agents run on CPU to preserve GPU resources
- Cogito:70b (A1 deliberation) blocks GPU 2+3 (28GB VRAM)

---

## Next Steps

### ✅ Completed
- [x] Hardware detection with CPU/RAM/GPU monitoring
- [x] Agent queue with 4 concurrent workers
- [x] GPU assignment via Waria monitor
- [x] Tool lifecycle framework (init→use→cleanup)
- [x] HTTP API endpoints for queue and health

### ⏳ Pending
- [ ] Wire Ollama API calls in `executeAgent()` (currently placeholder)
- [ ] Implement priority queue sorting (FIFO currently)
- [ ] Add queue persistence (restart recovery)
- [ ] Create Waria intelligence: auto-adjust thresholds based on hardware
- [ ] Add GPU-specific model routing (e.g., vision → GPU 0, code → GPU 1)
- [ ] Integrate with MCP tools (e.g., `amazon_mcp` calls queue for B3)

---

## Testing

### 1. Start Kirktower
```bash
cd /workspaces/librarian-agent/go
./kirktower_bin
```

### 2. Check Hardware
```bash
curl http://localhost:8080/api/system/health | jq
```

### 3. Submit Test Request
```bash
curl -X POST http://localhost:8080/api/queue/submit \
  -H "Content-Type: application/json" \
  -d '{
    "agent": "B3_Concrete",
    "task": "Test task",
    "llm_model": "qwen3-vl:32b",
    "priority": 5,
    "required_vram_mb": 12288
  }' | jq
```

### 4. Monitor Queue
```bash
curl http://localhost:8080/api/queue/list | jq
```

---

## Files Modified/Created

- ✅ **NEW**: `go/kernel/hardware.go` (297 lines)
- ✅ **NEW**: `go/kernel/queue.go` (355 lines)
- ✅ **MODIFIED**: `go/kernel/kirktower.go` (added hwMonitor + agentQueue)
- ✅ **MODIFIED**: `go/kirktower_bin` (rebuilt binary)

---

## Architecture Notes

**Why Goroutines Instead of Threads?**
- Go's concurrency model is lightweight (thousands of goroutines on 1 OS thread)
- Channels provide safe message passing without mutex hell
- Context cancellation enables graceful shutdown

**Why 4 Workers?**
- Typical dev machine: 2-4 GPUs
- 1 worker per GPU avoids VRAM contention
- CPU tasks (D1, D2) can use any worker since they don't block GPU

**Why 5-Second Hardware Polling?**
- Balance between responsiveness and CPU overhead
- GPU state changes slowly (model loads take seconds)
- Fast enough to react to crashed processes freeing VRAM

---

**Status**: ✅ Phase 1 Complete - Hardware detection and queue foundation ready for Phase 2 LLM integration.
