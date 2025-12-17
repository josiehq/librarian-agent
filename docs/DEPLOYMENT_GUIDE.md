# 4-Box Cluster Deployment Guide

## Architecture Overview

```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│   Box 1     │─────▶│   Box 2     │      │   Box 3     │      │   Box 4     │
│  D-Agents   │      │  B-C Agents │      │   Clash     │      │  A-Agents   │
│             │      │             │      │             │      │             │
│ rnj-1:8b    │      │nemotron-ocr │      │ REAP-25B    │      │ Qwen3-80B   │
│ nemotron-   │      │whisper-v3   │      │             │      │ Cogito-109B │
│ cascade:8b  │      │Olmo-3-7B    │      │             │      │             │
│             │      │             │      │             │      │             │
│ Codespace   │      │ g5.xlarge   │      │ Codespace   │      │GCP A100-80G │
│ or Local    │      │ $241/mo     │      │ $0-87/mo    │      │ $50-440/mo  │
└─────────────┘      └─────────────┘      └─────────────┘      └─────────────┘
```

---

## Box 1: D-Agents (Orchestration)

### **Deployment Options**

#### Option A: GitHub Codespace (Development)
```bash
# 1. Create Codespace from repo
gh codespace create -r josiehq/librarian-agent

# 2. Install Ollama
curl -fsSL https://ollama.com/install.sh | sh
ollama serve &

# 3. Pull models
ollama pull rnj-1:8b
ollama pull nemotron-cascade:8b

# 4. Build and run Kirktower
cd go
go build -o kirktower_bin *.go
./kirktower_bin

# 5. Test
curl http://localhost:8080/health
```



#### Option B: Local Development
```bash
# Same as Codespace, but free!
ollama serve &
cd go && go run *.go
```

#### Option C: AWS t3a.xlarge (Production 24/7)
```bash
# Launch instance
aws ec2 run-instances \
  --image-id ami-0c55b159cbfafe1f0 \
  --instance-type t3a.xlarge \
  --key-name your-key \
  --security-group-ids sg-xxx

# SSH and setup (same as Codespace)
```



---

## Box 2: B-C Agents (AWS g5.xlarge)

### **Deployment: AWS EC2**

#### 1. Launch Instance
```bash
aws ec2 run-instances \
  --image-id ami-0c55b159cbfafe1f0 \
  --instance-type g5.xlarge \
  --key-name your-key \
  --security-group-ids sg-xxx \
  --block-device-mappings '[{"DeviceName":"/dev/sda1","Ebs":{"VolumeSize":100}}]' \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=Box2-BC-Agents}]'
```

#### 2. Install Dependencies
```bash
# SSH into instance
ssh -i your-key.pem ubuntu@<box2-ip>

# Install NVIDIA drivers
sudo apt update
sudo apt install -y nvidia-driver-535
sudo reboot

# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh
ollama serve &

# Install Python
sudo apt install -y python3.12 python3-pip python3-venv
```

#### 3. Pull Models
```bash
# Vision OCR
ollama pull nemotron-ocr-v1

# Voice
ollama pull whisper-large-v3

# Browser automation
ollama pull olmo-3-7b-think:q4_k_m
```

#### 4. Setup MCP Wrappers
```bash
cd /opt
git clone https://github.com/josiehq/librarian-agent.git
cd librarian-agent/box3

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium

# Start services
./start_mcps.sh
```

#### 5. Configure Systemd (Auto-start)
```bash
# Create service file
sudo tee /etc/systemd/system/box2-mcps.service << EOF
[Unit]
Description=Box 2 MCP Wrappers
After=network.target

[Service]
Type=forking
User=ubuntu
WorkingDirectory=/opt/librarian-agent/box3
ExecStart=/opt/librarian-agent/box3/start_mcps.sh
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable box2-mcps
sudo systemctl start box2-mcps
```



---

## Box 3: Clash (GitHub Codespace)

### **Deployment: GitHub Codespace**

#### 1. Create Codespace
```bash
# Create separate Codespace for Clash
gh codespace create -r josiehq/librarian-agent -m basicLinux32gb
```

#### 2. Run Setup Script
```bash
cd /workspaces/librarian-agent/clash
bash setup_clash.sh
```

#### 3. Install VSCode Extension
```bash
# In Codespace VSCode, install Continue extension
# Config auto-loaded from ~/.continue/config.json
```

#### 4. Test
```bash
curl http://localhost:8086/clash/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Create a hello world function", "language": "python"}'
```



---

## Box 4: A-Agents (Google Cloud)

### **Deployment Options**

#### Option A: Google Colab Pro+ (Cheapest)
```bash
# 1. Subscribe to Colab Pro+
# 2. Create notebook with Ollama
!curl -fsSL https://ollama.com/install.sh | sh
!ollama serve &

# 3. Pull models
!ollama pull qwen3-next-80b-a3b:q4_k_m
!ollama pull cogito-109b:q4_k_m

# 4. Expose via ngrok
!pip install pyngrok
from pyngrok import ngrok
ngrok.set_auth_token("YOUR_TOKEN")
public_url = ngrok.connect(11434)
print(f"Ollama URL: {public_url}")

# 5. Set BOX4_URL in Box 1
export BOX4_URL="https://xxx.ngrok.io"
```

#### Option B: GCP Vertex AI Workbench
```bash
# 1. Create workbench instance
gcloud workbench instances create box4-a-agents \
  --location=us-central1-a \
  --machine-type=n1-standard-8 \
  --accelerator-type=NVIDIA_TESLA_A100 \
  --accelerator-core-count=1

# 2. SSH and setup (same as Box 2)
gcloud workbench instances ssh box4-a-agents

# 3. Install Ollama + models
curl -fsSL https://ollama.com/install.sh | sh
ollama serve &
ollama pull qwen3-next-80b-a3b:q4_k_m
ollama pull cogito-109b:q4_k_m
```

**Cost**: ~$440/month (4 hrs/day with A100-80GB)

## Environment Variables

Create `.env` in Box 1:

```bash
# Box 1 (local)
BOX1_URL=http://localhost:8080

# Box 2 (AWS g5.xlarge)
BOX2_URL=http://box2.internal:8083
BOX2_ENABLED=true

# Box 3 (Clash Codespace)
BOX3_URL=https://xxx-xxx.githubpreview.dev:8086
BOX3_ENABLED=true

# Box 4 (Google Cloud)
BOX4_URL=http://box4.internal:11434
BOX4_ENABLED=true

# Authentication
MCP_SHARED_SECRET=your-secret-here

# Ollama config (Box 1)
NUM_PARALLEL=2

# Ollama config (Box 2)
NUM_PARALLEL=3
```

---

## Testing

### Run E2E Tests
```bash
cd /workspaces/librarian-agent
./scripts/test_e2e.sh
```

### Test Individual Boxes

**Box 1 (Orchestration)**:
```bash
curl http://localhost:8080/health
curl http://localhost:8080/api/hardware
curl http://localhost:8080/api/queue/list
```

**Box 2 (Vision/Voice/Browser)**:
```bash
curl http://localhost:8083/health  # Vision
curl http://localhost:8084/health  # Voice
curl http://localhost:8085/health  # Browser
```

**Box 3 (Clash)**:
```bash
curl http://localhost:8086/health
curl -X POST http://localhost:8086/clash/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "test", "language": "python"}'
```

**Box 4 (A-Agents)**:
```bash
curl http://<box4-url>:11434/api/tags
```

---

## Cost Summary

### Development (8 hrs/day)
```
Box 1: Codespace 4-core        $87/mo
Box 2: g5.xlarge (8hr/day)    $241/mo
Box 3: Codespace (free tier)    $0/mo
Box 4: Colab Pro+               $50/mo
─────────────────────────────────────
Total:                        $378/mo
```

### Production (24/7 Box 2, 4hr/day Box 4)
```
Box 1: t3a.xlarge             $108/mo
Box 2: g5.xlarge (24/7)       $723/mo
Box 3: Codespace               $87/mo
Box 4: GCP A100 (4hr/day)     $440/mo
─────────────────────────────────────
Total:                      $1,358/mo
```

---

## Troubleshooting

### Box 1: Kirktower not starting
```bash
# Check Ollama
curl http://localhost:11434/api/tags

# Check Go build
cd go && go build -o kirktower_bin *.go
./kirktower_bin
```

### Box 2: MCP wrappers failing
```bash
# Check Ollama models
ollama list

# Check Python logs
tail -f /tmp/box3_*.log

# Restart services
pkill -f "vision_mcp.py"
cd box3 && ./start_mcps.sh
```

### Box 3: Clash not responding
```bash
# Check Ollama
curl http://localhost:11434/api/tags | grep reap

# Restart Clash
pkill -f clash_mcp.py
python3 ~/clash_mcp.py &
```

### Box 4: A-agents unreachable
```bash
# Check GCP instance running
gcloud compute instances list

# Check firewall
gcloud compute firewall-rules list | grep ollama

# Check Ollama
curl http://<box4-ip>:11434/api/tags
```

---

## Next Steps

1. ✅ Deploy Box 1 (Codespace or local)
2. ✅ Deploy Box 2 (AWS g5.xlarge)
3. ✅ Deploy Box 3 (Clash Codespace)
4. ✅ Deploy Box 4 (Google Cloud)
5. ⏳ Configure cross-box networking
6. ⏳ Test end-to-end workflow
7. ⏳ Set up monitoring (Prometheus/Grafana)
8. ⏳ Production deployment with load balancing
