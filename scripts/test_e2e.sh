#!/bin/bash
# End-to-end test script for 4-box cluster architecture

set -e

echo "🧪 Librarian Agent Cluster E2E Test"
echo "===================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test results
TESTS_PASSED=0
TESTS_FAILED=0

# Helper functions
test_endpoint() {
    local name=$1
    local url=$2
    local method=${3:-GET}
    
    echo -n "Testing $name... "
    
    if curl -s -f -X $method $url > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC}"
        ((TESTS_PASSED++))
        return 0
    else
        echo -e "${RED}✗${NC}"
        ((TESTS_FAILED++))
        return 1
    fi
}

test_json_endpoint() {
    local name=$1
    local url=$2
    local data=$3
    
    echo -n "Testing $name... "
    
    response=$(curl -s -X POST $url \
        -H "Content-Type: application/json" \
        -d "$data")
    
    if echo "$response" | jq -e '.success' > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC}"
        ((TESTS_PASSED++))
        echo "  Response: $response" | jq -C '.' | head -5
        return 0
    else
        echo -e "${RED}✗${NC}"
        ((TESTS_FAILED++))
        echo "  Response: $response"
        return 1
    fi
}

# =============================================================================
# BOX 1 TESTS (D-Agents - Orchestration)
# =============================================================================

echo "📦 Box 1: D-Agents (Orchestration)"
echo "-----------------------------------"

# Check if kirktower_bin is running
if pgrep -f kirktower_bin > /dev/null; then
    echo -e "${GREEN}✓${NC} kirktower_bin is running"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗${NC} kirktower_bin not running"
    ((TESTS_FAILED++))
    echo "  Start with: cd go && go run *.go"
fi

# Test health endpoint
test_endpoint "Box 1 health" "http://localhost:8080/health"

# Test hardware monitoring
test_endpoint "Hardware monitor" "http://localhost:8080/api/hardware"

# Test queue status
test_endpoint "Queue status" "http://localhost:8080/api/queue/list"

# Submit test request to queue
echo ""
echo "Testing queue submission..."
test_json_endpoint "Queue submit (D1 Puckfairy)" \
    "http://localhost:8080/api/queue/submit" \
    '{
        "agent": "D1_Puckfairy",
        "task": "Test routing task",
        "llm_model": "rnj-1:8b",
        "priority": 5,
        "required_vram_mb": 0
    }'

echo ""

# =============================================================================
# BOX 2 TESTS (B-C Agents - Vision/Voice/Browser)
# =============================================================================

echo "📦 Box 2: B-C Agents (AWS g5.xlarge)"
echo "-------------------------------------"

# Check if MCP wrappers are running
if curl -s http://localhost:8083/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Vision MCP running (port 8083)"
    ((TESTS_PASSED++))
else
    echo -e "${YELLOW}⚠${NC}  Vision MCP not running"
    echo "  Start with: cd box3 && ./start_mcps.sh"
fi

if curl -s http://localhost:8084/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Voice MCP running (port 8084)"
    ((TESTS_PASSED++))
else
    echo -e "${YELLOW}⚠${NC}  Voice MCP not running"
fi

if curl -s http://localhost:8085/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Browser MCP running (port 8085)"
    ((TESTS_PASSED++))
else
    echo -e "${YELLOW}⚠${NC}  Browser MCP not running"
fi

# Test vision screening (if running)
if curl -s http://localhost:8083/health > /dev/null 2>&1; then
    echo ""
    echo "Testing vision endpoints..."
    
    # Note: This requires CLIP model to be loaded
    # test_json_endpoint "Vision screen" \
    #     "http://localhost:8083/vision/screen" \
    #     '{...}'
    
    echo -e "${YELLOW}⚠${NC}  Vision tests skipped (requires model load)"
fi

echo ""

# =============================================================================
# BOX 3 TESTS (Clash - GitHub Codespace)
# =============================================================================

echo "📦 Box 3: Clash (GitHub Codespace)"
echo "----------------------------------"

if curl -s http://localhost:8086/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Clash MCP running (port 8086)"
    ((TESTS_PASSED++))
    
    # Test code generation
    echo "Testing code generation..."
    test_json_endpoint "Clash generate" \
        "http://localhost:8086/clash/generate" \
        '{
            "prompt": "Create a hello world function",
            "language": "python",
            "temperature": 0.3
        }'
else
    echo -e "${YELLOW}⚠${NC}  Clash MCP not running"
    echo "  Setup: cd clash && bash setup_clash.sh"
fi

echo ""

# =============================================================================
# BOX 4 TESTS (A-Agents - Google Cloud)
# =============================================================================

echo "📦 Box 4: A-Agents (Google Cloud)"
echo "---------------------------------"

# Check if Box 4 URL is configured
BOX4_URL=${BOX4_URL:-"http://box4.internal:11434"}

if curl -s -m 5 "$BOX4_URL/api/tags" > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Box 4 Ollama accessible"
    ((TESTS_PASSED++))
    
    # Check if models are loaded
    models=$(curl -s "$BOX4_URL/api/tags" | jq -r '.models[].name')
    echo "  Available models:"
    echo "$models" | while read model; do
        echo "    - $model"
    done
else
    echo -e "${YELLOW}⚠${NC}  Box 4 not accessible (expected for dev environment)"
    echo "  This is normal if Google Cloud instance not yet deployed"
fi

echo ""

# =============================================================================
# INTEGRATION TESTS
# =============================================================================

echo "🔗 Integration Tests"
echo "--------------------"

# Test MCP proxy routing
echo "Testing MCP proxy routing..."

# Route D1 (should stay local)
echo -n "  D1_Puckfairy routing... "
if curl -s "http://localhost:8080/api/queue/submit" \
    -H "Content-Type: application/json" \
    -d '{"agent": "D1_Puckfairy", "task": "test", "llm_model": "rnj-1:8b"}' | \
    jq -e '.success' > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗${NC}"
    ((TESTS_FAILED++))
fi

# Test Ollama connectivity (Box 1)
echo ""
echo "Testing Ollama (Box 1)..."
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Ollama running on Box 1"
    ((TESTS_PASSED++))
    
    # Check models
    echo "  Installed models:"
    curl -s http://localhost:11434/api/tags | jq -r '.models[].name' | while read model; do
        echo "    - $model"
    done
else
    echo -e "${RED}✗${NC} Ollama not running"
    ((TESTS_FAILED++))
    echo "  Start with: ollama serve"
fi

echo ""

# =============================================================================
# SUMMARY
# =============================================================================

echo "===================================="
echo "📊 Test Summary"
echo "===================================="
echo ""
echo "  Tests Passed: ${GREEN}$TESTS_PASSED${NC}"
echo "  Tests Failed: ${RED}$TESTS_FAILED${NC}"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✨ All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}❌ Some tests failed${NC}"
    echo ""
    echo "Common issues:"
    echo "  - Ollama not running: ollama serve"
    echo "  - kirktower_bin not running: cd go && go run *.go"
    echo "  - Box 3 MCP not running: cd box3 && ./start_mcps.sh"
    echo "  - Clash not running: cd clash && bash setup_clash.sh"
    echo "  - Box 4 not deployed yet (expected in dev)"
    exit 1
fi
