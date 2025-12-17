#!/bin/bash
# MCP Inter-Box Communication Test Script
# Tests connectivity between all 4 boxes

set -e

echo "🧪 Testing 4-Node Cluster MCP Communication"
echo "=========================================="

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Box addresses (update with actual IPs in production)
BOX1_ADDR="${BOX1_ADDR:-http://localhost:8080}"
BOX2_ADDR="${BOX2_ADDR:-http://localhost:8082}"
BOX3_ADDR="${BOX3_ADDR:-http://localhost:8083}"
BOX4_ADDR="${BOX4_ADDR:-http://localhost:8090}"

# Test function
test_endpoint() {
    local name=$1
    local url=$2
    local expected_status=${3:-200}
    
    echo -n "Testing $name... "
    
    status=$(curl -s -o /dev/null -w "%{http_code}" "$url" || echo "000")
    
    if [ "$status" == "$expected_status" ]; then
        echo -e "${GREEN}✓ OK${NC} (HTTP $status)"
        return 0
    else
        echo -e "${RED}✗ FAIL${NC} (HTTP $status, expected $expected_status)"
        return 1
    fi
}

# Test Box 1 (Orchestrator)
echo ""
echo "📦 Box 1: D-Agents (Orchestrator)"
test_endpoint "Box 1 Health" "$BOX1_ADDR/health"
test_endpoint "Box 1 MCP" "$BOX1_ADDR/mcp" "200"
test_endpoint "Box 1 Hardware Monitor" "$BOX1_ADDR/api/system/health"
test_endpoint "Box 1 Queue Status" "$BOX1_ADDR/api/queue/list"

# Test Box 3 (Vision Workers)
echo ""
echo "📦 Box 3: B-Agents + C1 Bash (Vision Workers)"
test_endpoint "Box 3 Vision MCP" "$BOX3_ADDR/vision" "404"  # Will return 404 until implemented
test_endpoint "Box 3 Whisper STT" "$BOX3_ADDR:8084/stt" "404"
test_endpoint "Box 3 Amazon MCP" "$BOX3_ADDR:8085/amazon" "404"
test_endpoint "Box 3 Figma MCP" "$BOX3_ADDR:8086/figma" "404"
test_endpoint "Box 3 Browser MCP" "$BOX3_ADDR:8087/browser" "404"

# Test Box 2 (Clash)
echo ""
echo "📦 Box 2: C3 Clash (Codespace)"
test_endpoint "Box 2 MCP Proxy" "$BOX2_ADDR/mcp/clash" "404"
test_endpoint "Box 2 Codespace API" "$BOX2_ADDR/codespace/status" "404"

# Test Box 4 (Big Brain - may be offline)
echo ""
echo "📦 Box 4: A-Agents + C2 Gunash (Big Brain - On-Demand)"
echo -e "${YELLOW}Note: Box 4 may be offline to save costs${NC}"
if test_endpoint "Box 4 Roark Deliberation" "$BOX4_ADDR/roark" "404" 2>/dev/null; then
    test_endpoint "Box 4 Josie Code Review" "$BOX4_ADDR:8091/josie" "404"
    test_endpoint "Box 4 Gunash Git Ops" "$BOX4_ADDR:8092/gunash" "404"
    test_endpoint "Box 4 Vision Fallback" "$BOX4_ADDR:8093/vision/complex" "404"
else
    echo -e "${YELLOW}Box 4 appears to be offline (expected for cost savings)${NC}"
fi

# Summary
echo ""
echo "=========================================="
echo "✅ Basic connectivity test complete"
echo ""
echo "Next steps:"
echo "1. Implement MCP wrapper endpoints on each box"
echo "2. Test Box 1 → Box 3 vision delegation"
echo "3. Test Box 1 → Box 4 auto-start logic"
echo "4. Test Box 3 → Box 4 vision fallback"
echo ""
