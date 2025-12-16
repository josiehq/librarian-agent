#!/usr/bin/env bash
# MCP Server Architecture Quick Reference

cat << 'EOF'

╔══════════════════════════════════════════════════════════════════════════════╗
║                    MCP SERVER ARCHITECTURE & DATA FLOW                      ║
╚══════════════════════════════════════════════════════════════════════════════╝

1. WHAT IS THE MCP SERVER?
   └─ Go kernel service at go/kernel/mcp_server.go
      - Runs on http://localhost:8080
      - Implements JSON-RPC 2.0 protocol
      - Routes all agent tool calls
      - Audits every action (via Waria state manager)

2. HOW DOES AN AGENT USE IT?
   
   Python Agent (e.g., Clash in py/orchestration/c_loop.py)
           │
           │ call_mcp_tool("container_exec", agent_id="clash", command="...")
           │
           ▼
   Build JSON-RPC Payload:
   {
     "jsonrpc": "2.0",
     "method": "container_exec",
     "params": {
       "name": "container_exec",
       "arguments": {"command": "...", "image": "..."},
       "agent_id": "clash"
     },
     "id": 1
   }
           │
           │ HTTP POST to http://localhost:8080/api/mcp
           │
           ▼
   MCP Server (go/kernel/mcp_server.go)
   - Parse JSON-RPC request
   - Extract: tool="container_exec", agentID="clash", args={...}
   - Lookup handler: s.tools["container_exec"]
   - Execute: tool_ContainerExec(args, "clash")
   - Audit via Waria: log action, check thresholds
   - Return JSON-RPC response
           │
           │ Response with result or error
           │
           ▼
   Python Agent receives response
   - Uses result to continue execution
   - Updates internal state

3. CURRENT REGISTERED TOOLS (in go/kernel/mcp_server.go)

   ┌─ container_exec ──────────────────────────────────────────┐
   │ Purpose:  Execute shell command in isolated Docker       │
   │ Args:     {command: "str", image: "str (optional)"}      │
   │ Handler:  tool_ContainerExec                             │
   │ Example:  await call_mcp_tool("container_exec",          │
   │             agent_id="puckfairy",                        │
   │             command="python main.py",                    │
   │             image="python:3.10")                         │
   └────────────────────────────────────────────────────────────┘

   ┌─ memory_commit ────────────────────────────────────────────┐
   │ Purpose:  Persist execution logs to Diplo (memory service)│
   │ Args:     {log_type: "str", content: "str"}              │
   │ Handler:  tool_MemoryCommit                              │
   │ Example:  await call_mcp_tool("memory_commit",           │
   │             agent_id="diplo",                            │
   │             log_type="blueprint",                        │
   │             content="Implementation plan...")            │
   └────────────────────────────────────────────────────────────┘

   ┌─ fs_write_guarded ─────────────────────────────────────────┐
   │ Purpose:  Safe file write with overwrite protection       │
   │ Args:     {path: "str", content: "str",                   │
   │            force_override: "bool"}                        │
   │ Handler:  tool_FSWriteGuarded                             │
   │ Example:  await call_mcp_tool("fs_write_guarded",        │
   │             agent_id="clash",                            │
   │             path="main.py",                              │
   │             content="...",                               │
   │             force_override=false)                        │
   └────────────────────────────────────────────────────────────┘

4. WHERE DO agents/*/tools/ FIT IN?

   Current Status: EMPTY DIRECTORIES (placeholders)
   
   Future Role:
   - Store agent-specific custom tools as Python functions
   - Example: agents/C/tools/code_implement.py
   
   Usage Pattern:
   ┌────────────────────────────────────────────────┐
   │ agents/C/tools/code_implement.py               │
   │                                                │
   │ def write_implementation(filepath, code):      │
   │     # Option 1: Direct local execution        │
   │     with open(filepath, 'w') as f:           │
   │         f.write(code)                        │
   │     return "Written locally"                  │
   │                                                │
   │     # Option 2: Call MCP for safety check    │
   │     result = await call_mcp_tool(            │
   │         "fs_write_guarded",                  │
   │         agent_id="clash",                    │
   │         path=filepath,                       │
   │         content=code                         │
   │     )                                         │
   │     return result                            │
   └────────────────────────────────────────────────┘

5. REQUEST/RESPONSE CYCLE (Complete Example)

   AGENT CALL (Python):
   ───────────────────
   await call_mcp_tool(
       "container_exec",
       agent_id="puckfairy",
       command="python test.py",
       image="python:3.10"
   )

   HTTP REQUEST:
   ─────────────
   POST /api/mcp HTTP/1.1
   Host: localhost:8080
   Content-Type: application/json

   {
     "jsonrpc": "2.0",
     "method": "container_exec",
     "params": {
       "name": "container_exec",
       "arguments": {
         "command": "python test.py",
         "image": "python:3.10"
       },
       "agent_id": "puckfairy"
     },
     "id": 1234567890ab
   }

   MCP SERVER PROCESSING:
   ──────────────────────
   1. Parse request → toolName="container_exec", agentID="puckfairy"
   2. Lookup handler → s.tools["container_exec"] found
   3. Execute → tool_ContainerExec({command: ..., image: ...}, "puckfairy")
   4. Audit → WariaUpdate("puckfairy", "EXEC: python test.py | OUT: ...", tokens)
   5. Return result or error

   HTTP RESPONSE:
   ──────────────
   HTTP/1.1 200 OK
   Content-Type: application/json

   {
     "jsonrpc": "2.0",
     "result": "test output...",
     "id": 1234567890ab
   }

   AGENT RECEIVES:
   ───────────────
   result = response.json()["result"]
   print(result)  # "test output..."

6. ADDING A NEW TOOL

   Step 1: Implement handler in go/kernel/mcp_server.go
   ────────────────────────────────────────────────────
   
   func (s *MCPServer) tool_MyNewTool(args map[string]interface{}, agentID string) (interface{}, error) {
       // Extract arguments
       param1, _ := args["param1"].(string)
       param2, _ := args["param2"].(int)
       
       // Execute logic
       result := doSomething(param1, param2)
       
       // Audit action
       s.tower.WariaUpdate(agentID, fmt.Sprintf("MY_NEW_TOOL: %s", result), 3)
       
       // Return result or error
       return result, nil
   }

   Step 2: Register in registerTools()
   ──────────────────────────────────
   
   func (s *MCPServer) registerTools() {
       s.tools["container_exec"] = s.tool_ContainerExec
       s.tools["memory_commit"] = s.tool_MemoryCommit
       s.tools["fs_write_guarded"] = s.tool_FSWriteGuarded
       s.tools["my_new_tool"] = s.tool_MyNewTool  // ← ADD HERE
   }

   Step 3: Use from Python agent
   ─────────────────────────────
   
   result = await call_mcp_tool(
       "my_new_tool",
       agent_id="agent_name",
       param1="value1",
       param2=42
   )

╔══════════════════════════════════════════════════════════════════════════════╗
║                             KEY TAKEAWAYS                                    ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ • MCP Server = Execution & Auditing Kernel (Go, JSON-RPC 2.0)              ║
║ • Agents = Python clients that POST requests to /api/mcp                    ║
║ • Tools = Registered handlers that execute safely & audit via Waria        ║
║ • agents/*/tools/ = Future extension point for agent-specific tools        ║
║                                                                              ║
║ Current Flow: Agent → HTTP POST → MCP Server → Handler → Response → Agent  ║
╚══════════════════════════════════════════════════════════════════════════════╝

EOF
