package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"os/exec"
	"strings"
	"sync"
)

// NOTE: This file depends on the 'TowerControl' struct (defined in kirktower.go)
// and the main structures (ProcessState, WariaState) defined in types.go.

// =============================================================================
// 1. MCP PROTOCOL DEFINITIONS (JSON-RPC 2.0)
// =============================================================================

// MCPRequest represents a standard JSON-RPC 2.0 request from an Agent/Model
type MCPRequest struct {
	JSONRPC string          `json:"jsonrpc"`
	Method  string          `json:"method"`      // The tool name (e.g., "container_exec") OR "call_tool" for routing
	Params  json.RawMessage `json:"params"`      // Can be: [args_map, agent_id] OR {name, arguments, agent_id}
	ID      interface{}     `json:"id"`
}

// MCPResponse represents a standard JSON-RPC 2.0 response back to the Agent
type MCPResponse struct {
	JSONRPC string      `json:"jsonrpc"`
	Result  interface{} `json:"result,omitempty"`
	Error   *MCPError   `json:"error,omitempty"`
	ID      interface{} `json:"id"`
}

// MCPError defines the error structure for JSON-RPC
type MCPError struct {
	Code    int    `json:"code"`
	Message string `json:"message"`
	Data    interface{} `json:"data,omitempty"`
}

// =============================================================================
// 2. MCP SERVER CORE
// =============================================================================

// ToolHandler function signature: takes arguments map and the calling Agent ID
type ToolHandler func(args map[string]interface{}, agentID string) (interface{}, error)

// MCPServer hosts the tools and enforces rules
type MCPServer struct {
	tower *TowerControl // Critical reference to Kirktower's main state/auditing system
	tools map[string]ToolHandler
	mu    sync.RWMutex
}

// NewMCPServer initializes the server and registers the core tools
func NewMCPServer(tc *TowerControl) *MCPServer {
	s := &MCPServer{
		tower: tc,
		tools: make(map[string]ToolHandler),
	}
	s.registerTools()
	return s
}

// registerTools maps the Python-facing tool name to the internal Go function
func (s *MCPServer) registerTools() {
	s.tools["container_exec"] = s.tool_ContainerExec
	s.tools["memory_commit"] = s.tool_MemoryCommit
	s.tools["fs_write_guarded"] = s.tool_FSWriteGuarded
}

// =============================================================================
// 3. HARDENED TOOL IMPLEMENTATIONS (AUDITED KERNELS)
// =============================================================================

// tool_ContainerExec is the audited wrapper for code execution (Docker/Sandbox)
func (s *MCPServer) tool_ContainerExec(args map[string]interface{}, agentID string) (interface{}, error) {
	// Expected args: "command" string, "image" string (optional)
	command, ok := args["command"].(string)
	if !ok {
		return nil, fmt.Errorf("argument 'command' is missing or not a string")
	}
	
	image, _ := args["image"].(string)
	if image == "" {
		image = "alpine/git:latest" // Default safe execution image
	}
	
	log.Printf("[MCP AUDIT: %s] Executing command: %s", agentID, command)

	// --- Execution Logic (Docker Sim) ---
	// WARNING: In production, this command must run against a hardened container environment.
	// We run 'sh -c' to execute the command string provided by the agent.
	dockerCmd := exec.Command("docker", "run", "--rm", 
		"-v", fmt.Sprintf("%s:/workspace", "/path/to/josiedesk"), // Volume mount for persistence
		"-w", "/workspace", 
		image, "sh", "-c", command)

	out, err := dockerCmd.CombinedOutput()
	outputStr := string(out)

	// --- Waria Post-Audit ---
	// Update Waria state based on the action/output
	tokenChange := len(outputStr) / 4 // Heuristic token cost
	s.tower.WariaUpdate(agentID, fmt.Sprintf("EXEC: %s | OUT: %s", command, outputStr[:min(len(outputStr), 100)]), tokenChange)

	if err != nil {
		return outputStr, fmt.Errorf("container execution failed: %v | Output: %s", err, outputStr)
	}
	
	return outputStr, nil
}

// tool_MemoryCommit is the critical function for agent memory/state management
func (s *MCPServer) tool_MemoryCommit(args map[string]interface{}, agentID string) (interface{}, error) {
	// Expected args: "log_type" string, "content" string
	logType, ok := args["log_type"].(string)
	content, ok2 := args["content"].(string)
	
	if !ok || !ok2 {
		return nil, fmt.Errorf("missing or invalid arguments for memory_commit (log_type, content)")
	}

	// --- Waria Audit ---
	log.Printf("[MCP AUDIT: %s] Memory Commit Type: %s", agentID, logType)
	s.tower.WariaUpdate(agentID, fmt.Sprintf("MEM_COMMIT: %s", logType), 5) 

	// NOTE: In the full system, this would make an internal RPC to Diplo (D2)
	
	return fmt.Sprintf("Log of type '%s' committed to Diplo by %s. Content length: %d", logType, agentID, len(content)), nil
}

// tool_FSWriteGuarded provides a safe write operation (part of Irreversibility Gatekeeper)
func (s *MCPServer) tool_FSWriteGuarded(args map[string]interface{}, agentID string) (interface{}, error) {
	// Expected args: "path" string, "content" string, "force_override" bool
	path, okPath := args["path"].(string)
	content, okContent := args["content"].(string)
	force, _ := args["force_override"].(bool)
	
	if !okPath || !okContent {
		return nil, fmt.Errorf("missing or invalid arguments for fs_write_guarded (path, content)")
	}

	// 1. Guarded Check (Irreversibility check)
	// Placeholder: A real check would prevent overwrites without explicit force flag.
	if !force {
		// e.g., if fileExists(path) { return nil, error("File exists. Use 'force_override: true'.") }
	}
	
	// 2. Execution Logic (Shell command for file write, must be quoted for safety)
	// We use `exec.Command` with a shell interpreter to handle the redirection.
	command := fmt.Sprintf("echo %s > %s", quote(content), path) 
	err := exec.Command("sh", "-c", command).Run()

	if err != nil {
		return nil, fmt.Errorf("guarded file write failed: %v", err)
	}
	
	// --- Waria Audit ---
	log.Printf("[MCP AUDIT: %s] Guarded Write to: %s (Force: %t)", agentID, path, force)
	s.tower.WariaUpdate(agentID, fmt.Sprintf("FS_WRITE: %s", path), 1)

	return fmt.Sprintf("Wrote %d bytes to %s. Force: %t", len(content), path, force), nil
}


// =============================================================================
// 4. HTTP HANDLER (implements http.Handler)
// =============================================================================

// ServeHTTP is the main entry point for the JSON-RPC server endpoint (e.g., /api/mcp)
func (s *MCPServer) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method Not Allowed. Must use POST.", http.StatusMethodNotAllowed)
		return
	}
	
	var req MCPRequest
	
	// Read and decode the request body (JSON-RPC)
	body, err := io.ReadAll(r.Body)
	if err != nil || json.Unmarshal(body, &req) != nil {
		s.sendError(w, nil, -32700, "Parse Error: Invalid JSON or empty body", nil)
		return
	}
	
	if req.Method == "" {
		s.sendError(w, req.ID, -32600, "Invalid Request: 'method' field is required", nil)
		return
	}

	// 2. Argument and Agent ID Extraction (CRITICAL for auditing)
	// Support TWO call formats:
	// Format 1: {name, arguments, agent_id} for Python hybrid calls
	// Format 2: [args_map, agent_id_string] for direct tool calls
	
	var toolName string
	var argsMap map[string]interface{}
	var agentID string
	
	// First, try to parse as object (Python format)
	var paramsObj map[string]interface{}
	if err := json.Unmarshal(req.Params, &paramsObj); err == nil {
		if name, ok := paramsObj["name"].(string); ok {
			// Python format detected
			toolName = name
			if args, ok := paramsObj["arguments"].(map[string]interface{}); ok {
				argsMap = args
			} else {
				argsMap = make(map[string]interface{})
			}
			if id, ok := paramsObj["agent_id"].(string); ok {
				agentID = id
			} else {
				agentID = "unknown_agent"
			}
		}
	}
	
	// If object parsing failed, try array format (Go format)
	if toolName == "" {
		var rawArgs []interface{}
		if err := json.Unmarshal(req.Params, &rawArgs); err != nil || len(rawArgs) < 2 {
			s.sendError(w, req.ID, -32602, "Invalid params: expected {name, arguments, agent_id} or [args_map, agent_id_string]", nil)
			return
		}
		
		argsMap, _ = rawArgs[0].(map[string]interface{})
		agentID, _ = rawArgs[1].(string)
	}
	
	// Use request Method if toolName wasn't extracted from params
	if toolName == "" {
		toolName = req.Method
	}
	
	if argsMap == nil || agentID == "" {
		s.sendError(w, req.ID, -32602, "Invalid params: missing required fields (arguments map or agent_id)", nil)
		return
	}
	
	// 3. Tool Lookup
	s.mu.RLock()
	handler, exists := s.tools[toolName]
	s.mu.RUnlock()

	if !exists {
		s.sendError(w, req.ID, -32601, fmt.Sprintf("Method Not Found: tool '%s' is not registered.", toolName), nil)
		return
	}

	// 4. Execute the Handler
	result, execErr := handler(argsMap, agentID)

	// 5. Send Response
	if execErr != nil {
		s.sendError(w, req.ID, -32000, "Tool Execution Error", map[string]string{"details": execErr.Error()})
	} else {
		s.sendResult(w, req.ID, result)
	}
}

// =============================================================================
// 5. UTILITY FUNCTIONS
// =============================================================================

// Helper function placeholder for quoting shell arguments to prevent injection
func quote(s string) string {
	// Replaces single quotes with '\''
	s = strings.ReplaceAll(s, "'", `'\''`)
	return "'" + s + "'"
}

// sendResult constructs and sends a successful JSON-RPC response
func (s *MCPServer) sendResult(w http.ResponseWriter, id interface{}, result interface{}) {
	resp := MCPResponse{
		JSONRPC: "2.0",
		Result:  result,
		ID:      id,
	}
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(resp)
}

// sendError constructs and sends a JSON-RPC error response
func (s *MCPServer) sendError(w http.ResponseWriter, id interface{}, code int, message string, data interface{}) {
	resp := MCPResponse{
		JSONRPC: "2.0",
		Error: &MCPError{
			Code:    code,
			Message: message,
			Data:    data,
		},
		ID: id,
	}
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusInternalServerError) // Use 500 for application errors
	json.NewEncoder(w).Encode(resp)
}

func min(a, b int) int {
	if a < b {
		return a
	}
	return b
}