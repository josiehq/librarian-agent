# Changelog

All notable changes to the Librarian Agent project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] - 2025-12-17

### 🎉 Initial Release: 4-Box Cluster Architecture

Complete implementation of distributed multi-agent system with hardware-aware orchestration, vision/voice capabilities, and code generation services.

---

### Added

#### **Core Infrastructure**

- **Hardware Monitoring (Waria)**
  - Real-time CPU/RAM/GPU detection via `/proc` and `nvidia-smi`
  - 5-second polling interval with automatic GPU selection
  - `go/kernel/hardware.go`: HardwareMonitor with FindAvailableGPU()
  - HTTP endpoint: `GET /api/hardware`

- **Agent Queueing System (Diplo)**
  - 4-worker concurrent processing with priority queue
  - GPU-aware task assignment and lifecycle management (INIT→USE→CLEANUP)
  - Ollama LLM integration in `executeAgent()` function
  - `go/kernel/queue.go`: AgentQueue with Submit(), GetStatus(), GetAllRequests()
  - HTTP endpoints: `POST /api/queue/submit`, `GET /api/queue/status`, `GET /api/queue/list`

- **MCP Proxy Layer**
  - Inter-box HTTP routing for 4-node cluster communication
  - Agent-to-box mapping with automatic fallback logic
  - Box 4 auto-start capability for on-demand A-agents
  - `go/kernel/mcp_proxy.go`: MCPProxy with RouteByAgent(), ProxyRequest()
  - Environment-based configuration via `BOX1_URL`, `BOX2_URL`, etc.

#### **Box 2: Vision/Voice/Browser MCP Wrappers**

- **Vision MCP** (`box3/vision_mcp.py`) - Port 8083
  - CLIP-ViT-B/32 for fast image screening (50-100 images/sec on GPU)
  - NVIDIA nemotron-ocr-v1 for detailed OCR analysis
  - Endpoints: `/vision/screen`, `/vision/ocr`, `/vision/analyze`, `/vision/upload`
  - Automatic CLIP model loading on startup

- **Voice MCP** (`box3/voice_mcp.py`) - Port 8084
  - OpenAI whisper-large-v3 for audio transcription
  - Voice command routing with intent parsing
  - Endpoints: `/voice/transcribe`, `/voice/upload`, `/voice/command`, `/voice/realtime`
  - Auto-detect language support

- **Browser Automation MCP** (`box3/browser_mcp.py`) - Port 8085
  - Olmo-3-7B-Think for Playwright script generation
  - Amazon listing creation automation
  - Endpoints: `/browser/automate`, `/browser/execute`, `/browser/amazon_listing`, `/browser/scrape`
  - Singleton browser instance management

- **Startup Script** (`box3/start_mcps.sh`)
  - One-command setup for all Box 2 services
  - Automatic health checks and dependency validation
  - Process ID tracking for easy shutdown

#### **Box 3: Clash Code Generation Service**

- **Clash MCP** (`clash/setup_clash.sh`)
  - REAP-25B integration for code generation, refactoring, debugging
  - Endpoints: `/clash/generate`, `/clash/refactor`, `/clash/explain`, `/clash/debug`
  - Automatic Ollama + code-server installation

- **VSCode Integration** (`clash/.devcontainer.json`)
  - GitHub Codespace auto-configuration
  - Continue extension with Ollama backend
  - Tab autocomplete powered by REAP-25B
  - One-click development environment setup

#### **Documentation**

- **Architecture Documentation**
  - `docs/NEW_CLUSTER_ARCHITECTURE.md`: Complete 4-box topology and agent mapping
  - `docs/BC_MINIMUM_AWS.md`: Instance sizing for B-C server (g5.xlarge analysis)
  - `docs/ABC_MINIMUM_INSTANCE.md`: VRAM calculations for merged A-B-C scenarios
  - `docs/FINAL_CLUSTER_CONFIG.md`: Definitive deployment specifications
  - `docs/MERGED_BC_BOX.md`: Analysis of B+C consolidation options

- **Deployment Guide** (`docs/DEPLOYMENT_GUIDE.md`)
  - Step-by-step setup for all 4 boxes
  - AWS, GCP, and GitHub Codespace instructions
  - Environment variable configuration
  - Systemd service setup for production
  - Cost breakdown by usage scenario

- **Testing** (`scripts/test_e2e.sh`)
  - Automated end-to-end test suite
  - Health checks for all services
  - Queue submission and Ollama integration tests
  - Cross-box routing validation

#### **Agent-to-Box Mapping**

- **Box 1 (D-Agents - Orchestration)**
  - D1 Puckfairy: rnj-1:8b (routing/delegation)
  - D2 Diplo: nemotron-cascade:8b (queue management)
  - Deployment: GitHub Codespace 4-core OR AWS t3a.xlarge

- **Box 2 (B-C Agents - AWS g5.xlarge)**
  - B1 Concrete Vision: Tools-based (nemotron-ocr + whisper + Olmo-3-7B)
  - C1 Bash: Olmo-3-7B-Think (shell automation)
  - Deployment: AWS EC2 g5.xlarge (1x A10G 24GB)
  - VRAM Usage: 15GB / 24GB (63%)

- **Box 3 (Clash - GitHub Codespace)**
  - C2 Clash: REAP-25B (code generation)
  - Deployment: GitHub Codespace 4-core

- **Box 4 (A-Agents - Google Cloud)**
  - A1 Josie: Qwen3-Next-80B-A3B (advanced reasoning)
  - A2 Roark: Qwen3-Next-80B + Cogito-109B (dual model!)
  - C3 Gunash: Cogito-109B (shell command generation)
  - Deployment: GCP with A100-80GB

---

### Changed

- **Routing Logic Updated** (`go/kernel/mcp_proxy.go`)
  - Removed old 3-box mapping (B1/B2/B3/B4 separate agents)
  - Unified B-agents into single B1 Concrete with specialized tools
  - A-agents moved to Google Cloud (Box 4)
  - C-agents split: Clash (Box 3), Bash (Box 2), Gunash (Box 4)

- **Vision Model Switched**
  - Changed from `deepseek-ocr` to `nemotron-ocr-v1` (NVIDIA)
  - Updated all references in vision_mcp.py, README, and scripts
  - Improved OCR accuracy and GPU performance

- **Agent Architecture Simplified**
  - B-agents consolidated from 4 separate LLM agents to single B1 with tools
  - Reduces model loading overhead and VRAM requirements
  - Enables faster task execution via specialized services

---

### Infrastructure

#### **Technology Stack**

- **Backend**: Go 1.22+ (Kirktower orchestration server)
- **LLM Runtime**: Ollama (local model serving)
- **MCP Services**: Python 3.12 + FastAPI + Uvicorn
- **Browser Automation**: Playwright + Chromium
- **Vision**: PyTorch + Transformers (CLIP + OCR)
- **Voice**: Whisper (via Ollama)

#### **Hardware Requirements**

| Box | Instance Type | GPU | VRAM | RAM |
|-----|--------------|-----|------|-----|
| Box 1 | Codespace/t3a.xlarge | None | - | 16GB |
| Box 2 | g5.xlarge | 1x A10G | 24GB | 16GB |
| Box 3 | Codespace 4-core | None | - | 16GB |
| Box 4 | GCP A100-80GB | 1x A100 | 80GB | 30GB+ |

#### **Model Sizes**

- **Box 1**: 10GB RAM (2x 8B models, Q4 quantized)
- **Box 2**: 15GB VRAM (nemotron-ocr 8GB + whisper 3GB + Olmo 4GB)
- **Box 3**: 13GB RAM (REAP-25B Q4)
- **Box 4**: 80GB VRAM (Qwen3-80B 45GB + Cogito-109B 35GB)

---

### Performance

- **CLIP Screening**: 50-100 images/sec (GPU) | 5-10 images/sec (CPU)
- **OCR Analysis**: 5-10 sec/image (GPU) | 20-30 sec/image (CPU)
- **Voice Transcription**: 1x real-time (GPU) | 0.5x real-time (CPU)
- **Code Generation**: 15-25 tokens/sec (REAP-25B on Codespace CPU)
- **D-Agent Routing**: 5-8 sec latency (8B models on CPU)
- **Queue Throughput**: 4 concurrent workers with dynamic GPU assignment

---

### API Endpoints

#### **Box 1 (Kirktower) - Port 8080**
```
GET  /health                  - Health check
GET  /api/hardware            - System resource status
POST /api/queue/submit        - Submit agent task
GET  /api/queue/status?id=X   - Get task status
GET  /api/queue/list          - List all tasks
```

#### **Box 2 (Vision/Voice/Browser)**
```
# Vision (Port 8083)
POST /vision/screen           - Fast CLIP screening
POST /vision/ocr              - Detailed OCR analysis
POST /vision/analyze          - Full pipeline
POST /vision/upload           - Direct upload

# Voice (Port 8084)
POST /voice/transcribe        - Audio to text
POST /voice/command           - Voice command routing
POST /voice/upload            - Direct upload
POST /voice/realtime          - Streaming transcription

# Browser (Port 8085)
POST /browser/automate        - Generate + execute Playwright
POST /browser/execute         - Execute script
POST /browser/amazon_listing  - Create Amazon listing
POST /browser/scrape          - Simple scraping
POST /browser/close           - Close browser
```

#### **Box 3 (Clash) - Port 8086**
```
POST /clash/generate          - Generate code
POST /clash/refactor          - Refactor code
POST /clash/explain           - Explain code
POST /clash/debug             - Debug + fix code
```

---

### Dependencies

#### **Go Modules** (`go.mod`)
- Go standard library only (no external deps for core)

#### **Python Requirements** (`box3/requirements.txt`)
- fastapi==0.115.0
- uvicorn[standard]==0.32.0
- torch==2.5.1
- transformers==4.46.0
- playwright==1.48.0
- pillow==11.0.0
- numpy==2.1.3
- requests==2.32.3

#### **System Dependencies**
- Ollama (LLM runtime)
- NVIDIA drivers 535+ (for GPU boxes)
- chromium (Playwright browser)

---

### Testing

Run comprehensive test suite:
```bash
./scripts/test_e2e.sh
```

Tests include:
- ✅ Kirktower health checks
- ✅ Hardware monitoring endpoints
- ✅ Agent queue submission and status
- ✅ Ollama integration (Box 1)
- ✅ Vision/Voice/Browser MCP health checks
- ✅ Clash code generation endpoint
- ✅ Cross-box routing validation

---

### Security

- **MCP Authentication**: Shared secret token via `MCP_SHARED_SECRET` environment variable
- **Cross-Box Communication**: HTTP with Bearer token authentication
- **AWS Security Groups**: Restrict ports 8080-8086 to internal VPC only
- **GitHub Codespace**: Private by default, port forwarding requires auth
- **Google Cloud**: Firewall rules limit access to Ollama port 11434

---

### Known Issues

- Box 4 auto-start requires AWS EC2 API integration (currently stubbed)
- Real-time voice transcription uses chunked polling (WebSocket version pending)
- Model swapping on g4dn.xlarge causes 10-15s delays (use g5.xlarge instead)
- CLIP model loading takes ~5 seconds on first request

---

### Breaking Changes

⚠️ **Agent routing completely redesigned**:
- Old agent names (B1_Raw, B2_Vision, B3_Concrete, B4_Kirktower) no longer valid
- New unified B1_Concrete agent handles all vision/voice/browser tasks
- A-agents moved from Box 4 to Google Cloud
- C-agents split across 3 boxes (C1→Box2, C2→Box3, C3→Box4)

**Migration**: Update all agent references in calling code to new mapping in `docs/NEW_CLUSTER_ARCHITECTURE.md`

---

### Upgrade Guide

**From previous architecture**:

1. Update environment variables:
   ```bash
   BOX2_URL=http://box2.internal:8083  # Was port 8082
   BOX3_URL=<clash-codespace-url>      # New Clash box
   BOX4_URL=<gcp-instance-url>         # A-agents to Google Cloud
   ```

2. Deploy Box 2 MCP wrappers:
   ```bash
   cd box3 && ./start_mcps.sh
   ```

3. Deploy Clash Codespace:
   ```bash
   cd clash && bash setup_clash.sh
   ```

4. Rebuild Kirktower:
   ```bash
   cd go && go build -o kirktower_bin *.go
   ```

---

### Roadmap

#### **Planned for v1.1.0**
- [ ] WebSocket support for real-time voice transcription
- [ ] AWS EC2 API integration for Box 4 auto-start/stop
- [ ] Prometheus metrics export from Kirktower
- [ ] Grafana dashboard for cluster monitoring
- [ ] Terraform scripts for automated AWS deployment
- [ ] Docker Compose for local development stack

#### **Planned for v1.2.0**
- [ ] Phase 2 supplier harvesting workflow implementation
- [ ] Visual Sovereign integration (MCP port 8087)
- [ ] Figma MCP proxy (port 8086)
- [ ] CLIP-based product screening pipeline
- [ ] Amazon Seller Central automation

#### **Future Considerations**
- [ ] Kubernetes deployment for production scale
- [ ] Load balancing across multiple Box 2 instances
- [ ] Model caching layer (Redis/Memcached)
- [ ] A/B testing framework for model selection
- [ ] Cost tracking and optimization dashboard

---

### Contributors

- Initial architecture and implementation: December 2025

---

### License

[Insert license here]

---

## Links

- **Repository**: https://github.com/josiehq/librarian-agent
- **Documentation**: `/docs/`
- **Issues**: https://github.com/josiehq/librarian-agent/issues
