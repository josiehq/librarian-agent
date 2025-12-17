"""
D3 Waria - MCP Communication Rules
Build & Infrastructure

This module defines how Waria communicates with the MCP server
and what tools/capabilities it has access to.
"""

AGENT_INFO = {
    "agent_id": "D3-Waria",
    "class": "D",
    "rank": "D3",
    "role": "Build & Infrastructure",
    "phase": 1
}

# MCP Server Configuration
MCP_CONFIG = {
    "server_url": "http://localhost:8080/mcp",
    "protocol": "JSON-RPC 2.0",
    "timeout": 30,
    "retry_attempts": 3,
    "retry_delay": 1.0
}

# Tools available to this agent
AVAILABLE_TOOLS = {
    "fabric_mcp": {
        "name": "fabric_mcp",
        "agent": "D3-Waria"
    },
    "build_tools": {
        "name": "build_tools",
        "agent": "D3-Waria"
    },
}

# Communication patterns
COMMUNICATION_RULES = {
    "coordinate_with": {
        "D1-Puckfairy": {
            "relationship": "peer",
            "pattern": "coordinate"
        },
        "D2-Diplo": {
            "relationship": "peer",
            "pattern": "coordinate"
        },
    },
    "logging": {
        "log_to": "D2-Diplo",
        "log_level": "info",
        "include": ["tool_usage", "decisions", "errors"],
        "async": True
    }
}

# Request/Response format
def build_mcp_request(method, params, request_id=None):
    """
    Build a JSON-RPC 2.0 compliant request for the MCP server.
    
    Args:
        method: Tool name
        params: Dictionary of parameters
        request_id: Optional request ID
        
    Returns:
        Dictionary formatted as JSON-RPC 2.0 request
    """
    import time
    
    return {
        "jsonrpc": "2.0",
        "method": "call_tool",
        "params": {
            "name": method,
            "arguments": params,
            "agent_id": AGENT_INFO["agent_id"]
        },
        "id": request_id or int(time.time() * 1000)
    }


def parse_mcp_response(response):
    """
    Parse JSON-RPC 2.0 response from MCP server.
    
    Args:
        response: Dictionary from MCP server
        
    Returns:
        Result data or raises exception on error
    """
    if "error" in response and response["error"]:
        error = response["error"]
        raise MCPError(
            code=error.get("code", -1),
            message=error.get("message", "Unknown error"),
            data=error.get("data")
        )
    
    return response.get("result")


class MCPError(Exception):
    """Custom exception for MCP errors"""
    def __init__(self, code, message, data=None):
        self.code = code
        self.message = message
        self.data = data
        super().__init__(f"MCP Error {code}: {message}")


# Phase-specific behavior
PHASE_BEHAVIORS = {
    1: {
        "tools": ['fabric_mcp', 'build_tools'],
        "subordinates": [],
        "responsibilities": [
            "Infrastructure building and Fabric MCP integration"
        ]
    }
}


# Usage example
if __name__ == "__main__":
    import json
    request = build_mcp_request(
        method="fabric_mcp",
        params={"action": "test"}
    )
    print("Sample MCP Request:")
    print(json.dumps(request, indent=2))
