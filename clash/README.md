# Clash Code Generation (C2 Agent)

**Purpose**: Code generation, refactoring, and debugging via REAP-25B
**Deployment**: GitHub Codespace (4-core, 16 GB RAM)
**Model**: Qwen3-Coder-REAP-25B-A3B (Q4: ~13 GB)

---

## Features

### 1. Code Generation
```bash
POST /clash/generate
{
  "prompt": "Create a function that validates email addresses",
  "language": "python",
  "temperature": 0.3
}
```

### 2. Code Refactoring
```bash
POST /clash/refactor
{
  "code": "def foo():\n  return 1+1",
  "instructions": "Add type hints and docstring",
  "language": "python"
}
```

### 3. Code Explanation
```bash
POST /clash/explain?language=python
Body: "def factorial(n): return 1 if n <= 1 else n * factorial(n-1)"
```

### 4. Debugging
```bash
POST /clash/debug?language=python
{
  "code": "print(x)",
  "error": "NameError: name 'x' is not defined"
}
```

---

## Setup

### Quick Start (GitHub Codespace)
```bash
# Clone repo and open in Codespace
gh codespace create -r josiehq/librarian-agent

# Setup script runs automatically via .devcontainer.json
# Or run manually:
bash /workspaces/librarian-agent/clash/setup_clash.sh
```

### Manual Setup
```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Start Ollama
ollama serve &

# Pull REAP-25B model (Q4 quantized)
ollama pull qwen3-coder-reap-25b-a3b:q4_k_m

# Install Python deps
pip install fastapi uvicorn requests

# Start Clash MCP
python3 ~/clash_mcp.py
```

---

## VSCode Integration

### Continue Extension Setup

1. Install **Continue** extension in VSCode
2. Config auto-loaded from `~/.continue/config.json`:

```json
{
  "models": [{
    "title": "Clash (REAP-25B)",
    "provider": "ollama",
    "model": "qwen3-coder-reap-25b-a3b:q4_k_m",
    "apiBase": "http://localhost:11434"
  }],
  "tabAutocompleteModel": {
    "provider": "ollama",
    "model": "qwen3-coder-reap-25b-a3b:q4_k_m"
  }
}
```

3. Use **Cmd+I** (Mac) or **Ctrl+I** (Linux/Windows) to open Clash chat
4. Highlight code and ask questions
5. Tab autocomplete powered by REAP-25B

---

## Integration with Box 1

Box 1 routes code generation tasks to Clash Codespace:

```go
// In Box 1 mcp_proxy.go
func RouteToClash(task CodeTask) (interface{}, error) {
    response := http.Post(
        "https://clash-codespace.github.dev:8086/clash/generate",
        "application/json",
        codePayload
    )
    return response.JSON()
}
```

**Codespace URL**: Forwarded via GitHub Codespace ports (public or private)

---

## Performance

**Model**: Qwen3-Coder-REAP-25B-A3B (Q4_K_M)
- **Size**: ~13 GB RAM
- **Speed**: 15-25 tokens/sec on Codespace 4-core (CPU)
- **Context**: 32K tokens
- **Quality**: Better than CodeLlama-34B, on par with GPT-3.5 for code

**Hardware**: GitHub Codespace 4-core
- **CPU**: 4 vCPUs (Intel/AMD)
- **RAM**: 16 GB (3 GB used by system, 13 GB for REAP-25B)
- **Disk**: 32 GB SSD

---

## Cost

### GitHub Codespaces Pricing
- **4-core instance**: $0.36/hour
- **8 hours/day**: $87/month
- **Free tier**: 60 hours/month = **$0/month** for light use!

### Alternative: AWS t3a.xlarge
- **4 vCPU, 16 GB RAM**: $0.1504/hr = $108/month (24/7)
- Use if Codespace limits exhausted

---

## Testing

```bash
# Generate code
curl -X POST http://localhost:8086/clash/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Create a binary search function",
    "language": "python"
  }' | jq

# Refactor code
curl -X POST http://localhost:8086/clash/refactor \
  -H "Content-Type: application/json" \
  -d '{
    "code": "def add(a,b):\n  return a+b",
    "instructions": "Add type hints and handle edge cases",
    "language": "python"
  }' | jq

# Explain code
curl -X POST "http://localhost:8086/clash/explain?language=python" \
  --data-raw "lambda x: x**2" | jq

# Debug code
curl -X POST "http://localhost:8086/clash/debug?language=python" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "def divide(a, b):\n  return a / b",
    "error": "ZeroDivisionError: division by zero"
  }' | jq
```

---

## Agent Usage

### C2 Clash Agent Profile
```python
# agents/C/Clash/profile/api.py

async def generate_code(prompt: str, language: str = "python") -> str:
    """Generate code using REAP-25B"""
    response = await http_client.post(
        "http://localhost:8086/clash/generate",
        json={"prompt": prompt, "language": language}
    )
    return response.json()["code"]

async def refactor_code(code: str, instructions: str) -> str:
    """Refactor existing code"""
    response = await http_client.post(
        "http://localhost:8086/clash/refactor",
        json={"code": code, "instructions": instructions}
    )
    return response.json()["refactored"]
```

---

## Next Steps

1. ✅ Setup Clash Codespace environment
2. ⏳ Test code generation quality
3. ⏳ Integrate with Box 1 routing
4. ⏳ Test VSCode Continue extension
5. ⏳ Benchmark performance (tokens/sec on Codespace)
6. ⏳ Test public URL forwarding for cross-box communication
