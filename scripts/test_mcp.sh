#!/bin/bash
# MCP Server Test Runner

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                   MCP SERVER TESTING                          ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Check if Go server is already running
echo "1️⃣  Checking if MCP server is running..."
if curl -s http://localhost:8080/api/state > /dev/null 2>&1; then
    echo "✅ MCP server already running on port 8080"
else
    echo "❌ MCP server not running. Starting..."
    cd ../go
    go run kernel/*.go types.go &
    KIRK_PID=$!
    sleep 2
    
    if curl -s http://localhost:8080/api/state > /dev/null 2>&1; then
        echo "✅ MCP server started (PID: $KIRK_PID)"
    else
        echo "❌ Failed to start MCP server"
        kill $KIRK_PID 2>/dev/null || true
        exit 1
    fi
    cd - > /dev/null
fi

echo ""
echo "2️⃣  Running test suite..."
echo ""

cd /workspaces/librarian-agent

# Check if httpx is installed
python -c "import httpx" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "📦 Installing dependencies..."
    pip install httpx > /dev/null 2>&1
fi

# Run tests
python py/tests/test_mcp_server.py

TEST_RESULT=$?

if [ $TEST_RESULT -eq 0 ]; then
    echo ""
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║                  🎉 ALL TESTS PASSED 🎉                       ║"
    echo "║                                                                ║"
    echo "║  You now understand how MCP Server works:                      ║"
    echo "║  - Python agents POST JSON-RPC requests to /api/mcp           ║"
    echo "║  - Server routes to tool handlers (container_exec, etc.)      ║"
    echo "║  - Tools execute with auditing via Waria state manager        ║"
    echo "║  - Response returned as JSON-RPC result                       ║"
    echo "║                                                                ║"
    echo "║  Next: Explore agents/*/tools/ to add custom tools            ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
else
    echo ""
    echo "❌ Some tests failed. Check output above for details."
    echo ""
    echo "Debugging tips:"
    echo "  • Ensure Go server is running: cd go && go run kernel/*.go types.go"
    echo "  • Check if Docker is available (for container_exec tests)"
    echo "  • Verify port 8080 is not in use"
fi

exit $TEST_RESULT
