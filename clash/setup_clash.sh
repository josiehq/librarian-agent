#!/bin/bash
# Clash Codespace Setup Script
# Sets up REAP-25B code generation environment with VSCode integration

set -e

echo "🚀 Setting up Clash Code Generation Environment"
echo "=============================================="

# Install Ollama
if ! command -v ollama &> /dev/null; then
    echo "Installing Ollama..."
    curl -fsSL https://ollama.com/install.sh | sh
fi

# Start Ollama in background
echo "Starting Ollama server..."
ollama serve &
OLLAMA_PID=$!
sleep 3

# Pull REAP-25B model
echo "Pulling REAP-25B model (this may take a while)..."
ollama pull qwen3-coder-reap-25b-a3b:q4_k_m

# Install code-server
if ! command -v code-server &> /dev/null; then
    echo "Installing code-server..."
    curl -fsSL https://code-server.dev/install.sh | sh
fi

# Install Python dependencies
echo "Installing Python dependencies..."
pip install fastapi uvicorn[standard] pydantic requests

# Create Clash MCP wrapper
cat > /tmp/clash_mcp.py << 'EOF'
#!/usr/bin/env python3
"""
Clash MCP Wrapper - Code Generation Service
Runs on GitHub Codespace with REAP-25B
"""

import logging
from typing import Optional

import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Clash Code Generator", version="1.0.0")

OLLAMA_HOST = "http://localhost:11434"
REAP_MODEL = "qwen3-coder-reap-25b-a3b:q4_k_m"


class CodeGenerationRequest(BaseModel):
    """Code generation request"""
    prompt: str
    language: Optional[str] = "python"
    context: Optional[str] = None
    temperature: float = 0.3


class CodeRefactorRequest(BaseModel):
    """Code refactoring request"""
    code: str
    instructions: str
    language: Optional[str] = "python"


@app.get("/health")
async def health_check():
    """Health check"""
    return {"status": "healthy", "model": REAP_MODEL}


@app.post("/clash/generate")
async def generate_code(request: CodeGenerationRequest):
    """
    Generate code from natural language
    
    Use case: "Create a function that sorts a list of dictionaries by key"
    """
    try:
        # Build prompt
        prompt = f"""You are an expert {request.language} programmer. Generate clean, efficient, well-documented code.

Task: {request.prompt}

"""
        if request.context:
            prompt += f"Context:\n{request.context}\n\n"
        
        prompt += f"Generate only the {request.language} code, no explanations:\n\n"
        
        # Call Ollama
        response = requests.post(
            f"{OLLAMA_HOST}/api/generate",
            json={
                "model": REAP_MODEL,
                "prompt": prompt,
                "stream": False,
                "temperature": request.temperature
            },
            timeout=120
        )
        response.raise_for_status()
        
        result = response.json()
        code = result.get("response", "")
        
        return {
            "success": True,
            "code": code,
            "language": request.language,
            "model": REAP_MODEL
        }
    
    except Exception as e:
        logger.error(f"Generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/clash/refactor")
async def refactor_code(request: CodeRefactorRequest):
    """
    Refactor existing code
    
    Use case: "Add error handling" or "Optimize for speed"
    """
    try:
        prompt = f"""Refactor this {request.language} code according to the instructions.

Original code:
```{request.language}
{request.code}
```

Instructions: {request.instructions}

Provide the refactored code:
"""
        
        response = requests.post(
            f"{OLLAMA_HOST}/api/generate",
            json={
                "model": REAP_MODEL,
                "prompt": prompt,
                "stream": False,
                "temperature": 0.2
            },
            timeout=120
        )
        response.raise_for_status()
        
        result = response.json()
        refactored = result.get("response", "")
        
        return {
            "success": True,
            "original": request.code,
            "refactored": refactored,
            "language": request.language
        }
    
    except Exception as e:
        logger.error(f"Refactor error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/clash/explain")
async def explain_code(code: str, language: str = "python"):
    """Explain what code does"""
    try:
        prompt = f"""Explain what this {language} code does in simple terms:

```{language}
{code}
```

Explanation:
"""
        
        response = requests.post(
            f"{OLLAMA_HOST}/api/generate",
            json={
                "model": REAP_MODEL,
                "prompt": prompt,
                "stream": False,
                "temperature": 0.3
            },
            timeout=60
        )
        response.raise_for_status()
        
        result = response.json()
        explanation = result.get("response", "")
        
        return {
            "success": True,
            "code": code,
            "explanation": explanation
        }
    
    except Exception as e:
        logger.error(f"Explain error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/clash/debug")
async def debug_code(code: str, error: str, language: str = "python"):
    """Debug code and suggest fixes"""
    try:
        prompt = f"""Debug this {language} code that's producing an error:

Code:
```{language}
{code}
```

Error: {error}

Provide:
1. Explanation of the issue
2. Fixed code

Response:
"""
        
        response = requests.post(
            f"{OLLAMA_HOST}/api/generate",
            json={
                "model": REAP_MODEL,
                "prompt": prompt,
                "stream": False,
                "temperature": 0.3
            },
            timeout=120
        )
        response.raise_for_status()
        
        result = response.json()
        solution = result.get("response", "")
        
        return {
            "success": True,
            "original_code": code,
            "error": error,
            "solution": solution
        }
    
    except Exception as e:
        logger.error(f"Debug error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Clash MCP Wrapper on port 8086")
    uvicorn.run(app, host="0.0.0.0", port=8086)
EOF

mv /tmp/clash_mcp.py ~/clash_mcp.py
chmod +x ~/clash_mcp.py

# Start Clash MCP in background
echo "Starting Clash MCP wrapper..."
python3 ~/clash_mcp.py &
CLASH_PID=$!
sleep 3

# Create Continue config for VSCode integration
mkdir -p ~/.continue
cat > ~/.continue/config.json << 'EOF'
{
  "models": [
    {
      "title": "Clash (REAP-25B)",
      "provider": "ollama",
      "model": "qwen3-coder-reap-25b-a3b:q4_k_m",
      "apiBase": "http://localhost:11434"
    }
  ],
  "tabAutocompleteModel": {
    "title": "Clash Autocomplete",
    "provider": "ollama",
    "model": "qwen3-coder-reap-25b-a3b:q4_k_m",
    "apiBase": "http://localhost:11434"
  },
  "embeddingsProvider": {
    "provider": "ollama",
    "model": "nomic-embed-text",
    "apiBase": "http://localhost:11434"
  }
}
EOF

echo ""
echo "=============================================="
echo "✅ Clash Environment Ready!"
echo ""
echo "Services:"
echo "  Ollama:      http://localhost:11434"
echo "  Clash MCP:   http://localhost:8086"
echo ""
echo "PIDs:"
echo "  Ollama: $OLLAMA_PID"
echo "  Clash:  $CLASH_PID"
echo ""
echo "Test Clash:"
echo '  curl -X POST http://localhost:8086/clash/generate \'
echo '    -H "Content-Type: application/json" \'
echo '    -d "{\"prompt\": \"Create a hello world function\", \"language\": \"python\"}"'
echo ""
echo "VSCode Extension:"
echo "  Install 'Continue' extension"
echo "  Config auto-loaded from ~/.continue/config.json"
echo ""
echo "Stop with: kill $OLLAMA_PID $CLASH_PID"
