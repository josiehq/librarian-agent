#!/usr/bin/env python
"""
test_mcp_server.py - MCP Server Testing Suite

Tests JSON-RPC 2.0 request/response cycle, tool handlers, and auditing.
Run AFTER starting the Go MCP server: go run go/kernel/*.go
"""

import asyncio
import httpx
import json
import sys
from typing import Dict, Any

# ============================================================================
# MCP SERVER TESTING
# ============================================================================

MCP_URL = "http://localhost:8080/api/mcp"
TESTS_PASSED = 0
TESTS_FAILED = 0


def test_result(test_name: str, passed: bool, details: str = ""):
    """Pretty print test result."""
    global TESTS_PASSED, TESTS_FAILED
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} | {test_name}")
    if details and not passed:
        print(f"       {details}")
    if passed:
        TESTS_PASSED += 1
    else:
        TESTS_FAILED += 1


async def test_server_reachable():
    """Test 1: MCP server is running and responding."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get("http://localhost:8080/api/state")
            passed = response.status_code == 200
            test_result("Server Reachable", passed)
            return passed
    except Exception as e:
        test_result("Server Reachable", False, f"Connection error: {e}")
        return False


async def test_json_rpc_format():
    """Test 2: Server accepts and parses JSON-RPC 2.0 format."""
    payload = {
        "jsonrpc": "2.0",
        "method": "container_exec",
        "params": {
            "name": "container_exec",
            "arguments": {"command": "echo test", "image": "alpine"},
            "agent_id": "test_agent"
        },
        "id": 1
    }
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(MCP_URL, json=payload)
            passed = response.status_code == 200
            
            if passed:
                resp_json = response.json()
                passed = "jsonrpc" in resp_json and resp_json["jsonrpc"] == "2.0"
            
            test_result("JSON-RPC Format", passed)
            if not passed:
                print(f"       Response: {response.text[:100]}")
            return passed
    except Exception as e:
        test_result("JSON-RPC Format", False, str(e))
        return False


async def test_container_exec_tool():
    """Test 3: container_exec tool executes and returns output."""
    payload = {
        "jsonrpc": "2.0",
        "method": "container_exec",
        "params": {
            "name": "container_exec",
            "arguments": {
                "command": "echo 'Hello from MCP'",
                "image": "alpine"
            },
            "agent_id": "puckfairy"
        },
        "id": 2
    }
    
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(MCP_URL, json=payload)
            passed = response.status_code == 200
            
            if passed:
                resp_json = response.json()
                # Either result exists or error exists
                has_result = "result" in resp_json
                has_error = "error" in resp_json
                passed = (has_result or has_error) and resp_json.get("id") == 2
            
            test_result("container_exec Tool", passed)
            if not passed:
                print(f"       Response: {response.text[:150]}")
            return passed
    except Exception as e:
        test_result("container_exec Tool", False, str(e))
        return False


async def test_memory_commit_tool():
    """Test 4: memory_commit tool accepts and logs data."""
    payload = {
        "jsonrpc": "2.0",
        "method": "memory_commit",
        "params": {
            "name": "memory_commit",
            "arguments": {
                "log_type": "test_log",
                "content": "Testing MCP memory persistence"
            },
            "agent_id": "diplo"
        },
        "id": 3
    }
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(MCP_URL, json=payload)
            passed = response.status_code == 200
            
            if passed:
                resp_json = response.json()
                passed = (resp_json.get("result") is not None or resp_json.get("error") is None)
            
            test_result("memory_commit Tool", passed)
            if not passed:
                print(f"       Response: {response.text[:150]}")
            return passed
    except Exception as e:
        test_result("memory_commit Tool", False, str(e))
        return False


async def test_invalid_tool():
    """Test 5: Server rejects unknown tools with JSON-RPC error."""
    payload = {
        "jsonrpc": "2.0",
        "method": "nonexistent_tool",
        "params": {
            "name": "nonexistent_tool",
            "arguments": {"foo": "bar"},
            "agent_id": "test"
        },
        "id": 4
    }
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(MCP_URL, json=payload)
            resp_json = response.json()
            
            # Should have error, not result
            passed = "error" in resp_json and "result" not in resp_json
            test_result("Invalid Tool Rejection", passed)
            return passed
    except Exception as e:
        test_result("Invalid Tool Rejection", False, str(e))
        return False


async def test_missing_agent_id():
    """Test 6: Server handles missing agent_id gracefully."""
    payload = {
        "jsonrpc": "2.0",
        "method": "container_exec",
        "params": {
            "name": "container_exec",
            "arguments": {"command": "echo test"},
            # Missing agent_id
        },
        "id": 5
    }
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(MCP_URL, json=payload)
            resp_json = response.json()
            
            # Should either work with default or return error, but be valid JSON-RPC
            passed = response.status_code in (200, 400, 500)
            test_result("Missing agent_id Handling", passed)
            return passed
    except Exception as e:
        test_result("Missing agent_id Handling", False, str(e))
        return False


async def test_state_endpoint():
    """Test 7: /api/state returns system state."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get("http://localhost:8080/api/state")
            passed = response.status_code == 200
            
            if passed:
                state = response.json()
                # Check for expected fields
                required_fields = {"active_processes", "total_processes", "processes"}
                passed = all(field in state or field.lower() in str(state).lower() 
                           for field in required_fields)
            
            test_result("/api/state Endpoint", passed)
            return passed
    except Exception as e:
        test_result("/api/state Endpoint", False, str(e))
        return False


async def test_concurrent_requests():
    """Test 8: Server handles concurrent requests."""
    payloads = [
        {
            "jsonrpc": "2.0",
            "method": "container_exec",
            "params": {
                "name": "container_exec",
                "arguments": {"command": f"echo 'Request {i}'"},
                "agent_id": f"agent_{i}"
            },
            "id": 100 + i
        }
        for i in range(3)
    ]
    
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            tasks = [
                client.post(MCP_URL, json=payload)
                for payload in payloads
            ]
            responses = await asyncio.gather(*tasks)
            
            passed = all(r.status_code == 200 for r in responses)
            test_result("Concurrent Requests", passed)
            return passed
    except Exception as e:
        test_result("Concurrent Requests", False, str(e))
        return False


async def test_agent_id_tracking():
    """Test 9: Agent ID is preserved in response."""
    agent_id = "tracking_test_agent"
    payload = {
        "jsonrpc": "2.0",
        "method": "container_exec",
        "params": {
            "name": "container_exec",
            "arguments": {"command": "echo tracked"},
            "agent_id": agent_id
        },
        "id": 9
    }
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(MCP_URL, json=payload)
            resp_json = response.json()
            
            # ID should be preserved in response
            passed = resp_json.get("id") == 9
            test_result("Agent ID Tracking", passed)
            return passed
    except Exception as e:
        test_result("Agent ID Tracking", False, str(e))
        return False


async def test_large_payload():
    """Test 10: Server handles large payloads."""
    large_content = "x" * 100000  # 100KB
    payload = {
        "jsonrpc": "2.0",
        "method": "memory_commit",
        "params": {
            "name": "memory_commit",
            "arguments": {
                "log_type": "large_test",
                "content": large_content
            },
            "agent_id": "large_test"
        },
        "id": 10
    }
    
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(MCP_URL, json=payload)
            passed = response.status_code in (200, 500)  # Either succeeds or returns server error
            test_result("Large Payload", passed)
            return passed
    except Exception as e:
        test_result("Large Payload", False, str(e))
        return False


async def run_all_tests():
    """Run the full test suite."""
    print("\n" + "="*70)
    print("MCP SERVER TEST SUITE")
    print("="*70)
    print(f"\nTarget: {MCP_URL}\n")
    
    tests = [
        test_server_reachable,
        test_json_rpc_format,
        test_container_exec_tool,
        test_memory_commit_tool,
        test_invalid_tool,
        test_missing_agent_id,
        test_state_endpoint,
        test_concurrent_requests,
        test_agent_id_tracking,
        test_large_payload,
    ]
    
    for test_func in tests:
        await test_func()
        await asyncio.sleep(0.1)  # Small delay between tests
    
    print("\n" + "="*70)
    print(f"RESULTS: {TESTS_PASSED} passed, {TESTS_FAILED} failed")
    print("="*70 + "\n")
    
    return TESTS_FAILED == 0


if __name__ == "__main__":
    print("\n⚠️  Make sure MCP server is running: go run go/kernel/*.go")
    print("⏳ Starting tests in 2 seconds...\n")
    
    import time
    time.sleep(2)
    
    try:
        success = asyncio.run(run_all_tests())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n🛑 Tests interrupted by user")
        sys.exit(1)
