# Box 3 MCP Wrappers

**Purpose**: FastAPI services providing vision, voice, and browser automation capabilities for B1 agent

---

## Services

### 1. Vision MCP (Port 8083)
**File**: `vision_mcp.py`

**Models**:
- CLIP-ViT-B/32 (150 MB) - Fast image screening
- nemotron-ocr-v1 (8 GB) - Detailed OCR analysis (NVIDIA)

**Endpoints**:
```bash
# Fast CLIP screening (100+ images/sec)
POST /vision/screen
{
  "image_urls": ["url1", "url2", ...],
  "categories": ["leather wallet", "not relevant"],
  "threshold": 0.7
}

# Detailed OCR analysis (5-10 sec per image)
POST /vision/ocr
{
  "image_url": "https://example.com/product.jpg",
  "question": "Extract all text and describe the product"
}

# Full analysis (CLIP + OCR)
POST /vision/analyze
{
  "image_url": "https://example.com/product.jpg",
  "categories": ["wallet", "bag", "other"],
  "ocr_question": "Describe this product in detail"
}

# Upload image directly
POST /vision/upload
FormData: file + question
```

---

### 2. Voice MCP (Port 8084)
**File**: `voice_mcp.py`

**Model**: whisper-large-v3 (3 GB)

**Endpoints**:
```bash
# Transcribe audio to text
POST /voice/transcribe
{
  "audio_url": "https://example.com/audio.wav",
  "language": "en"  # optional, auto-detect if null
}

# Voice command routing
POST /voice/command
{
  "audio_url": "https://example.com/command.wav"
}
# Returns: {"agent": "B1_Concrete", "task_type": "search"}

# Upload audio directly
POST /voice/upload
FormData: file + language (optional)

# Real-time transcription
POST /voice/realtime
FormData: audio chunk
```

---

### 3. Browser Automation MCP (Port 8085)
**File**: `browser_mcp.py`

**Model**: Olmo-3-7B-Think (4 GB)

**Endpoints**:
```bash
# Generate + execute Playwright automation
POST /browser/automate
{
  "task_description": "Navigate to Amazon and search for leather wallets",
  "url": "https://amazon.com",
  "execute": true,
  "headless": true
}

# Execute pre-generated script
POST /browser/execute
{
  "script": "async def automate_task(page): ...",
  "headless": true
}

# Create Amazon listing (Phase 2)
POST /browser/amazon_listing
{
  "product_title": "Leather Wallet...",
  "product_description": "...",
  "price": 29.99,
  "images": ["url1", "url2"],
  "category": "Wallets",
  "keywords": ["leather", "wallet", "bifold"]
}

# Simple scraping
POST /browser/scrape?url=...&selector=...

# Close browser
POST /browser/close
```

---

## Installation

```bash
cd /workspaces/librarian-agent/box3

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Pull Ollama models
ollama pull nemotron-ocr-v1
ollama pull whisper-large-v3
ollama pull olmo-3-7b-think
```

---

## Usage

### Start All Services
```bash
./start_mcps.sh
```

### Start Individual Services
```bash
# Vision
python3 vision_mcp.py

# Voice
python3 voice_mcp.py

# Browser
python3 browser_mcp.py
```

---

## Testing

### Vision Test
```bash
curl -X POST http://localhost:8083/vision/screen \
  -H "Content-Type: application/json" \
  -d '{
    "image_urls": ["https://example.com/wallet.jpg"],
    "categories": ["leather wallet", "not relevant"],
    "threshold": 0.7
  }' | jq
```

### Voice Test
```bash
curl -X POST http://localhost:8084/voice/transcribe \
  -H "Content-Type: application/json" \
  -d '{
    "audio_url": "https://example.com/audio.wav"
  }' | jq
```

### Browser Test
```bash
curl -X POST http://localhost:8085/browser/automate \
  -H "Content-Type: application/json" \
  -d '{
    "task_description": "Go to example.com and extract the page title",
    "execute": true,
    "headless": true
  }' | jq
```

---

## Integration with Box 1

Box 1 routes requests to Box 3 via MCP proxy:

```go
// In Box 1 mcp_proxy.go
func RouteVisionTask(imageURL string) (interface{}, error) {
    response := http.Post(
        "http://box3.internal:8083/vision/analyze",
        "application/json",
        imagePayload
    )
    return response.JSON()
}
```

---

## Performance

| Service | Model | Speed (GPU) | Speed (CPU) |
|---------|-------|-------------|-------------|
| **CLIP Screening** | ViT-B/32 | 50-100 img/s | 5-10 img/s |
| **Nemotron OCR** | nemotron-ocr-v1 | 5-10 sec/img | 20-30 sec/img |
| **Whisper** | large-v3 | 1x real-time | 0.5x real-time |
| **Olmo Browser** | 7B | 25-35 tok/s | 10-15 tok/s |

**GPU**: NVIDIA A10G 24GB (g5.xlarge)  
**VRAM Usage**: ~15 GB / 24 GB available

---

## Next Steps

1. Test locally with Box 1 delegation
2. Deploy to AWS g5.xlarge
3. Integrate with Visual Sovereign (port 8087)
4. Add Figma MCP proxy (port 8086)
5. Test Phase 2 workflow (supplier harvesting → Amazon listing)
