package kernel

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"os/exec"
)

// =============================================================================
// MCP TOOL IMPLEMENTATIONS - ALL 11 EXTERNAL TOOLS
// =============================================================================
// Each tool follows the ToolHandler signature: func(args map[string]interface{}, agentID string) (interface{}, error)
// All tools include Waria auditing and Diplo logging hooks

// =============================================================================
// 1. FABRIC EXECUTE (D3 Waria)
// =============================================================================

func (s *MCPServer) tool_FabricExecute(args map[string]interface{}, agentID string) (interface{}, error) {
	pattern, okPattern := args["pattern"].(string)
	input, okInput := args["input"].(string)

	if !okPattern || !okInput {
		return nil, fmt.Errorf("missing required arguments: pattern (string), input (string)")
	}

	log.Printf("[MCP AUDIT: %s] Fabric Execute: pattern=%s", agentID, pattern)

	// Fabric CLI command: fabric --pattern <pattern> <<< "input"
	fabricCmd := exec.Command("fabric", "--pattern", pattern)
	fabricCmd.Stdin = bytes.NewBufferString(input)

	output, err := fabricCmd.CombinedOutput()
	outputStr := string(output)

	// Waria Audit
	s.tower.WariaUpdate(agentID, fmt.Sprintf("FABRIC: %s", pattern), len(outputStr)/4)

	if err != nil {
		return outputStr, fmt.Errorf("fabric execution failed: %v | output: %s", err, outputStr)
	}

	return map[string]interface{}{
		"pattern": pattern,
		"output":  outputStr,
		"status":  "success",
	}, nil
}

// =============================================================================
// 2. NVIM LSP (D1 Puckfairy → C1 Bash)
// =============================================================================

func (s *MCPServer) tool_NvimLSP(args map[string]interface{}, agentID string) (interface{}, error) {
	operation, okOp := args["operation"].(string) // hover, definition, references, etc.
	file, okFile := args["file"].(string)
	line, okLine := args["line"].(float64)
	col, okCol := args["col"].(float64)

	if !okOp || !okFile || !okLine || !okCol {
		return nil, fmt.Errorf("missing required arguments: operation, file, line, col")
	}

	log.Printf("[MCP AUDIT: %s] Nvim LSP: %s at %s:%d:%d", agentID, operation, file, int(line), int(col))

	// Call nvim-lsp-mcp server (assumed running on localhost:8082)
	lspURL := "http://localhost:8082/lsp"
	payload := map[string]interface{}{
		"jsonrpc": "2.0",
		"method":  operation,
		"params": map[string]interface{}{
			"textDocument": map[string]string{"uri": fmt.Sprintf("file://%s", file)},
			"position":     map[string]int{"line": int(line), "character": int(col)},
		},
		"id": 1,
	}

	jsonData, _ := json.Marshal(payload)
	resp, err := http.Post(lspURL, "application/json", bytes.NewBuffer(jsonData))
	if err != nil {
		return nil, fmt.Errorf("nvim-lsp-mcp connection failed: %v", err)
	}
	defer resp.Body.Close()

	body, _ := io.ReadAll(resp.Body)
	var lspResponse map[string]interface{}
	json.Unmarshal(body, &lspResponse)

	// Waria Audit
	s.tower.WariaUpdate(agentID, fmt.Sprintf("LSP: %s", operation), 3)

	return lspResponse, nil
}

// =============================================================================
// 3. GITHUB API (D2 Diplo → C2 Gunash)
// =============================================================================

func (s *MCPServer) tool_GitHubAPI(args map[string]interface{}, agentID string) (interface{}, error) {
	operation, okOp := args["operation"].(string) // issues, pulls, commits, etc.
	repo, okRepo := args["repo"].(string)         // owner/repo
	params, _ := args["params"].(map[string]interface{})

	if !okOp || !okRepo {
		return nil, fmt.Errorf("missing required arguments: operation, repo")
	}

	log.Printf("[MCP AUDIT: %s] GitHub API: %s on %s", agentID, operation, repo)

	// Call github-mcp-server (assumed running on localhost:8083)
	githubURL := "http://localhost:8083/github"
	payload := map[string]interface{}{
		"jsonrpc": "2.0",
		"method":  operation,
		"params": map[string]interface{}{
			"repository": repo,
			"arguments":  params,
		},
		"id": 1,
	}

	jsonData, _ := json.Marshal(payload)
	resp, err := http.Post(githubURL, "application/json", bytes.NewBuffer(jsonData))
	if err != nil {
		return nil, fmt.Errorf("github-mcp connection failed: %v", err)
	}
	defer resp.Body.Close()

	body, _ := io.ReadAll(resp.Body)
	var githubResponse map[string]interface{}
	json.Unmarshal(body, &githubResponse)

	// Waria Audit
	s.tower.WariaUpdate(agentID, fmt.Sprintf("GITHUB: %s", operation), 5)

	return githubResponse, nil
}

// =============================================================================
// 4. TERMINAL EXEC (D1 Puckfairy ONLY)
// =============================================================================

func (s *MCPServer) tool_TerminalExec(args map[string]interface{}, agentID string) (interface{}, error) {
	// SECURITY: Only Puckfairy can call this
	if agentID != "D1_Puckfairy" {
		return nil, fmt.Errorf("SECURITY VIOLATION: terminal_exec restricted to D1_Puckfairy only")
	}

	command, okCmd := args["command"].(string)
	cwd, _ := args["cwd"].(string)
	if cwd == "" {
		cwd = "/workspace"
	}

	if !okCmd {
		return nil, fmt.Errorf("missing required argument: command")
	}

	log.Printf("[MCP AUDIT: %s] Terminal Exec: %s (cwd: %s)", agentID, command, cwd)

	// Call mcp-terminal server (assumed running on localhost:8084)
	terminalURL := "http://localhost:8084/terminal"
	payload := map[string]interface{}{
		"jsonrpc": "2.0",
		"method":  "execute",
		"params": map[string]interface{}{
			"command": command,
			"cwd":     cwd,
		},
		"id": 1,
	}

	jsonData, _ := json.Marshal(payload)
	resp, err := http.Post(terminalURL, "application/json", bytes.NewBuffer(jsonData))
	if err != nil {
		return nil, fmt.Errorf("mcp-terminal connection failed: %v", err)
	}
	defer resp.Body.Close()

	body, _ := io.ReadAll(resp.Body)
	var terminalResponse map[string]interface{}
	json.Unmarshal(body, &terminalResponse)

	// Waria Audit
	s.tower.WariaUpdate(agentID, fmt.Sprintf("TERMINAL: %s", command[:min(len(command), 50)]), 10)

	return terminalResponse, nil
}

// =============================================================================
// 5. FIGMA API (B2 Vision)
// =============================================================================

func (s *MCPServer) tool_FigmaAPI(args map[string]interface{}, agentID string) (interface{}, error) {
	operation, okOp := args["operation"].(string) // get_file, export_image, etc.
	fileKey, okKey := args["file_key"].(string)
	params, _ := args["params"].(map[string]interface{})

	if !okOp || !okKey {
		return nil, fmt.Errorf("missing required arguments: operation, file_key")
	}

	log.Printf("[MCP AUDIT: %s] Figma API: %s on file %s", agentID, operation, fileKey)

	// Call figma-mcp-server (assumed running on localhost:8085)
	figmaURL := "http://localhost:8085/figma"
	payload := map[string]interface{}{
		"jsonrpc": "2.0",
		"method":  operation,
		"params": map[string]interface{}{
			"file_key":  fileKey,
			"arguments": params,
		},
		"id": 1,
	}

	jsonData, _ := json.Marshal(payload)
	resp, err := http.Post(figmaURL, "application/json", bytes.NewBuffer(jsonData))
	if err != nil {
		return nil, fmt.Errorf("figma-mcp connection failed: %v", err)
	}
	defer resp.Body.Close()

	body, _ := io.ReadAll(resp.Body)
	var figmaResponse map[string]interface{}
	json.Unmarshal(body, &figmaResponse)

	// Waria Audit
	s.tower.WariaUpdate(agentID, fmt.Sprintf("FIGMA: %s", operation), 7)

	return figmaResponse, nil
}

// =============================================================================
// 6. BROWSER NAVIGATE (B1 Raw)
// =============================================================================

func (s *MCPServer) tool_BrowserNavigate(args map[string]interface{}, agentID string) (interface{}, error) {
	url, okURL := args["url"].(string)
	actions, _ := args["actions"].([]interface{})

	if !okURL {
		return nil, fmt.Errorf("missing required argument: url")
	}

	log.Printf("[MCP AUDIT: %s] Browser Navigate: %s", agentID, url)

	// Call browser-mcp server (assumed running on localhost:8086)
	browserURL := "http://localhost:8086/browser"
	payload := map[string]interface{}{
		"jsonrpc": "2.0",
		"method":  "navigate",
		"params": map[string]interface{}{
			"url":     url,
			"actions": actions,
		},
		"id": 1,
	}

	jsonData, _ := json.Marshal(payload)
	resp, err := http.Post(browserURL, "application/json", bytes.NewBuffer(jsonData))
	if err != nil {
		return nil, fmt.Errorf("browser-mcp connection failed: %v", err)
	}
	defer resp.Body.Close()

	body, _ := io.ReadAll(resp.Body)
	var browserResponse map[string]interface{}
	json.Unmarshal(body, &browserResponse)

	// Waria Audit
	s.tower.WariaUpdate(agentID, fmt.Sprintf("BROWSER: %s", url), 15)

	return browserResponse, nil
}

// =============================================================================
// 7. WEB CRAWL (B1 Raw)
// =============================================================================

func (s *MCPServer) tool_WebCrawl(args map[string]interface{}, agentID string) (interface{}, error) {
	startURL, okURL := args["start_url"].(string)
	depth, _ := args["depth"].(float64)
	selectors, _ := args["selectors"].([]interface{})

	if !okURL {
		return nil, fmt.Errorf("missing required argument: start_url")
	}
	if depth == 0 {
		depth = 1 // Default depth
	}

	log.Printf("[MCP AUDIT: %s] Web Crawl: %s (depth: %d)", agentID, startURL, int(depth))

	// Call crawl-mcp server (assumed running on localhost:8087)
	crawlURL := "http://localhost:8087/crawl"
	payload := map[string]interface{}{
		"jsonrpc": "2.0",
		"method":  "crawl",
		"params": map[string]interface{}{
			"start_url": startURL,
			"depth":     int(depth),
			"selectors": selectors,
		},
		"id": 1,
	}

	jsonData, _ := json.Marshal(payload)
	resp, err := http.Post(crawlURL, "application/json", bytes.NewBuffer(jsonData))
	if err != nil {
		return nil, fmt.Errorf("crawl-mcp connection failed: %v", err)
	}
	defer resp.Body.Close()

	body, _ := io.ReadAll(resp.Body)
	var crawlResponse map[string]interface{}
	json.Unmarshal(body, &crawlResponse)

	// Waria Audit
	s.tower.WariaUpdate(agentID, fmt.Sprintf("CRAWL: %s", startURL), 20)

	return crawlResponse, nil
}

// =============================================================================
// 8. AMAZON API (B3 Concrete)
// =============================================================================

func (s *MCPServer) tool_AmazonAPI(args map[string]interface{}, agentID string) (interface{}, error) {
	service, okSvc := args["service"].(string)    // s3, ec2, lambda, etc.
	operation, okOp := args["operation"].(string) // list_buckets, describe_instances, etc.
	params, _ := args["params"].(map[string]interface{})

	if !okSvc || !okOp {
		return nil, fmt.Errorf("missing required arguments: service, operation")
	}

	log.Printf("[MCP AUDIT: %s] Amazon API: %s.%s", agentID, service, operation)

	// Call amazon-mcp-server (assumed running on localhost:8088)
	amazonURL := "http://localhost:8088/amazon"
	payload := map[string]interface{}{
		"jsonrpc": "2.0",
		"method":  fmt.Sprintf("%s.%s", service, operation),
		"params":  params,
		"id":      1,
	}

	jsonData, _ := json.Marshal(payload)
	resp, err := http.Post(amazonURL, "application/json", bytes.NewBuffer(jsonData))
	if err != nil {
		return nil, fmt.Errorf("amazon-mcp connection failed: %v", err)
	}
	defer resp.Body.Close()

	body, _ := io.ReadAll(resp.Body)
	var amazonResponse map[string]interface{}
	json.Unmarshal(body, &amazonResponse)

	// Waria Audit
	s.tower.WariaUpdate(agentID, fmt.Sprintf("AMAZON: %s.%s", service, operation), 10)

	return amazonResponse, nil
}

// =============================================================================
// 9. AGNO ORCHESTRATE (B4 Kirktower) - CORE KIRKTOWER DNA
// =============================================================================

func (s *MCPServer) tool_AgnoOrchestrate(args map[string]interface{}, agentID string) (interface{}, error) {
	// SECURITY: Only Kirktower can call this
	if agentID != "B4_Kirktower" {
		return nil, fmt.Errorf("SECURITY VIOLATION: agno_orchestrate restricted to B4_Kirktower only")
	}

	operation, okOp := args["operation"].(string) // start, stop, status, coordinate
	agents, _ := args["agents"].([]interface{})
	task, _ := args["task"].(string)
	config, _ := args["config"].(map[string]interface{})

	if !okOp {
		return nil, fmt.Errorf("missing required argument: operation")
	}

	log.Printf("[MCP AUDIT: %s] Agno Orchestrate: operation=%s, agents=%d", agentID, operation, len(agents))

	// Call agno API (assumed running on localhost:8089)
	agnoURL := "http://localhost:8089/agno"
	payload := map[string]interface{}{
		"jsonrpc": "2.0",
		"method":  operation,
		"params": map[string]interface{}{
			"agents": agents,
			"task":   task,
			"config": config,
		},
		"id": 1,
	}

	jsonData, _ := json.Marshal(payload)
	resp, err := http.Post(agnoURL, "application/json", bytes.NewBuffer(jsonData))
	if err != nil {
		return nil, fmt.Errorf("agno connection failed: %v", err)
	}
	defer resp.Body.Close()

	body, _ := io.ReadAll(resp.Body)
	var agnoResponse map[string]interface{}
	json.Unmarshal(body, &agnoResponse)

	// Waria Audit
	s.tower.WariaUpdate(agentID, fmt.Sprintf("AGNO: %s", operation), 25)

	return agnoResponse, nil
}

// =============================================================================
// 10. OPENHANDS EXECUTE (C and D Series - CORE C/D DNA)
// =============================================================================

func (s *MCPServer) tool_OpenHandsExecute(args map[string]interface{}, agentID string) (interface{}, error) {
	operation, okOp := args["operation"].(string) // execute_skill, list_skills, get_workspace_info
	skill, _ := args["skill"].(string)
	params, _ := args["params"].(map[string]interface{})

	if !okOp {
		return nil, fmt.Errorf("missing required argument: operation")
	}

	log.Printf("[MCP AUDIT: %s] OpenHands Execute: operation=%s, skill=%s", agentID, operation, skill)

	// Call OpenHands API (assumed running on localhost:8090)
	openhandsURL := "http://localhost:8090/api"
	payload := map[string]interface{}{
		"jsonrpc": "2.0",
		"method":  operation,
		"params": map[string]interface{}{
			"skill":     skill,
			"agent_id":  agentID,
			"arguments": params,
		},
		"id": 1,
	}

	jsonData, _ := json.Marshal(payload)
	resp, err := http.Post(openhandsURL, "application/json", bytes.NewBuffer(jsonData))
	if err != nil {
		return nil, fmt.Errorf("openhands connection failed: %v", err)
	}
	defer resp.Body.Close()

	body, _ := io.ReadAll(resp.Body)
	var openhandsResponse map[string]interface{}
	json.Unmarshal(body, &openhandsResponse)

	// Waria Audit
	s.tower.WariaUpdate(agentID, fmt.Sprintf("OPENHANDS: %s", skill), 15)

	return openhandsResponse, nil
}

// =============================================================================
// 11. NARNIA EXECUTE (D2 Diplo → C2 Gunash in Phase 3)
// =============================================================================

func (s *MCPServer) tool_NarniaExecute(args map[string]interface{}, agentID string) (interface{}, error) {
	command, okCmd := args["command"].(string) // see, change, write, grab, pull, create

	if !okCmd {
		return nil, fmt.Errorf("missing required argument: command (string)")
	}

	log.Printf("[MCP AUDIT: %s] Narnia Execute: command=%s", agentID, command)

	// Build narnia CLI command: python -m narnia <command> [args...]
	cmdArgs := []string{"-m", "narnia", command}

	// Add command-specific arguments
	switch command {
	case "see":
		// No additional args

	case "change":
		path, ok := args["path"].(string)
		if !ok {
			return nil, fmt.Errorf("'change' command requires 'path' argument")
		}
		cmdArgs = append(cmdArgs, path)

	case "write":
		if dryRun, ok := args["dry_run"].(bool); ok && dryRun {
			cmdArgs = append(cmdArgs, "--dry-run")
		}
		if verbose, ok := args["verbose"].(bool); ok && verbose {
			cmdArgs = append(cmdArgs, "--verbose")
		}

	case "grab":
		repoURL, ok := args["repo_url"].(string)
		if !ok {
			return nil, fmt.Errorf("'grab' command requires 'repo_url' argument")
		}
		cmdArgs = append(cmdArgs, repoURL)
		if force, ok := args["force"].(bool); ok && force {
			cmdArgs = append(cmdArgs, "--force")
		}

	case "pull":
		// No additional args

	case "create":
		name, ok := args["name"].(string)
		if !ok {
			return nil, fmt.Errorf("'create' command requires 'name' argument")
		}
		cmdArgs = append(cmdArgs, name)

	default:
		return nil, fmt.Errorf("unknown narnia command: %s (valid: see, change, write, grab, pull, create)", command)
	}

	// Execute python -m narnia
	cmd := exec.Command("python3", cmdArgs...)
	output, err := cmd.CombinedOutput()
	outputStr := string(output)

	// Waria Audit
	s.tower.WariaUpdate(agentID, fmt.Sprintf("NARNIA: %s", command), len(outputStr)/4)

	result := map[string]interface{}{
		"command":   command,
		"output":    outputStr,
		"exit_code": 0,
		"success":   err == nil,
	}

	if err != nil {
		if exitErr, ok := err.(*exec.ExitError); ok {
			result["exit_code"] = exitErr.ExitCode()
		} else {
			result["exit_code"] = 1
		}
		result["error"] = err.Error()
	}

	return result, nil
}

// =============================================================================
// 12. VSCODE MCP (C3 Clash - Codespaces Crawler)
// =============================================================================

func (s *MCPServer) tool_VSCodeMCP(args map[string]interface{}, agentID string) (interface{}, error) {
	operation, okOp := args["operation"].(string) // navigate, search, edit, etc.
	file, _ := args["file"].(string)
	params, _ := args["params"].(map[string]interface{})

	if !okOp {
		return nil, fmt.Errorf("missing required argument: operation")
	}

	log.Printf("[MCP AUDIT: %s] VSCode MCP: operation=%s, file=%s", agentID, operation, file)

	// Call vscode-mcp server (assumed running on localhost:8091)
	vscodeURL := "http://localhost:8091/vscode"
	payload := map[string]interface{}{
		"jsonrpc": "2.0",
		"method":  operation,
		"params": map[string]interface{}{
			"file":      file,
			"agent_id":  agentID,
			"arguments": params,
		},
		"id": 1,
	}

	jsonData, _ := json.Marshal(payload)
	resp, err := http.Post(vscodeURL, "application/json", bytes.NewBuffer(jsonData))
	if err != nil {
		return nil, fmt.Errorf("vscode-mcp connection failed: %v", err)
	}
	defer resp.Body.Close()

	body, _ := io.ReadAll(resp.Body)
	var vscodeResponse map[string]interface{}
	json.Unmarshal(body, &vscodeResponse)

	// Waria Audit
	s.tower.WariaUpdate(agentID, fmt.Sprintf("VSCODE: %s", operation), 10)

	return vscodeResponse, nil
}

// =============================================================================
// 13. REDIS QUEUE (D2 Diplo - Memory & Task Queue Management)
// =============================================================================

func (s *MCPServer) tool_RedisQueue(args map[string]interface{}, agentID string) (interface{}, error) {
	operation, okOp := args["operation"].(string) // push, pop, peek, length, clear
	queue, okQueue := args["queue"].(string)      // queue name
	data, _ := args["data"].(string)              // payload for push operations

	if !okOp || !okQueue {
		return nil, fmt.Errorf("missing required arguments: operation (string), queue (string)")
	}

	log.Printf("[MCP AUDIT: %s] Redis Queue: operation=%s, queue=%s", agentID, operation, queue)

	// Call redis-mcp server (assumed running on localhost:8092)
	redisURL := "http://localhost:8092/redis"
	payload := map[string]interface{}{
		"jsonrpc": "2.0",
		"method":  operation,
		"params": map[string]interface{}{
			"queue":     queue,
			"data":      data,
			"agent_id":  agentID,
			"namespace": "librarian_agent",
		},
		"id": 1,
	}

	jsonData, _ := json.Marshal(payload)
	resp, err := http.Post(redisURL, "application/json", bytes.NewBuffer(jsonData))
	if err != nil {
		return nil, fmt.Errorf("redis-mcp connection failed: %v", err)
	}
	defer resp.Body.Close()

	body, _ := io.ReadAll(resp.Body)
	var redisResponse map[string]interface{}
	json.Unmarshal(body, &redisResponse)

	// Waria Audit - track queue activity
	s.tower.WariaUpdate(agentID, fmt.Sprintf("REDIS_Q: %s", operation), 5)

	return redisResponse, nil
}

// =============================================================================
// 14. VISUAL SOVEREIGN (TBD - To Be Loaded)
// =============================================================================

func (s *MCPServer) tool_VisualSovereign(args map[string]interface{}, agentID string) (interface{}, error) {
	// Placeholder for Visual Sovereign testing framework
	return nil, fmt.Errorf("visual_sovereign not yet implemented - awaiting framework load")
}

// =============================================================================
// AGENT AUTHORIZATION MATRIX
// =============================================================================

// AgentToolPermissions defines which tools each agent is authorized to use
var AgentToolPermissions = map[string][]string{
	// D-Class: OpenHands + specific tools
	"D1_Puckfairy": {"terminal_exec", "nvim_lsp", "openhands_execute"},
	"D2_Diplo":     {"memory_commit", "github_api", "narnia_execute", "redis_queue", "openhands_execute"},
	"D3_Waria":     {"fabric_execute", "openhands_execute"}, // Container ops via openhands

	// B-Class: Specialized tools
	"B1_Raw":       {"browser_navigate", "web_crawl"},
	"B2_Vision":    {"figma_api"},                      // Frontend/GUI design ONLY
	"B3_Concrete":  {"amazon_api", "visual_sovereign"}, // Amazon + Visual Sovereign
	"B4_Kirktower": {"agno_orchestrate"},               // AGNO is Kirktower's DNA

	// C-Class: OpenHands + execution tools (Container ops via openhands)
	"C1_Bash":   {"container_exec", "openhands_execute"},               // + nvim_lsp in Phase 3
	"C2_Gunash": {"container_exec", "openhands_execute"},               // + github_api + narnia in Phase 3
	"C3_Clash":  {"container_exec", "openhands_execute", "vscode_mcp"}, // VSCode + container ops

	// A-Class: No direct tool access (testing phase)
	"A1_Roark":  {}, // No direct tool access
	"A2_Josie":  {}, // No direct tool access (container ops via delegation to D3/C3)
	"A3_Athena": {}, // Uses internal RAG system
}

// NOTE: Container/Docker operations are ONLY available through:
// - D3 Waria (openhands_execute)
// - C3 Clash (openhands_execute + container_exec)
// - A2 Josie (delegation only, no direct tools)
// NO B-tier agents have container access.

// checkPermission validates if an agent is authorized to use a specific tool
func (s *MCPServer) checkPermission(agentID string, toolName string) bool {
	allowedTools, exists := AgentToolPermissions[agentID]
	if !exists {
		log.Printf("[AUTHORIZATION] Unknown agent ID: %s", agentID)
		return false
	}

	for _, tool := range allowedTools {
		if tool == toolName {
			return true
		}
	}

	log.Printf("[AUTHORIZATION] Agent %s denied access to tool %s", agentID, toolName)
	return false
}

// transferToolOwnership handles Phase 3 tool ownership transfers
// D1 Puckfairy → C1 Bash (nvim_lsp)
// D2 Diplo → C2 Gunash (github_api + narnia)
func (s *MCPServer) transferToolOwnership(phase int) {
	if phase == 3 {
		log.Println("[PHASE 3] Transferring tool ownership...")

		// Transfer nvim_lsp from D1 to C1
		AgentToolPermissions["C1_Bash"] = append(AgentToolPermissions["C1_Bash"], "nvim_lsp")
		log.Println("[PHASE 3] nvim_lsp transferred: D1_Puckfairy → C1_Bash")

		// Transfer github_api + narnia from D2 to C2 (git management)
		AgentToolPermissions["C2_Gunash"] = append(AgentToolPermissions["C2_Gunash"], "github_api", "narnia_execute")
		log.Println("[PHASE 3] github_api + narnia transferred: D2_Diplo → C2_Gunash (git management)")
	}
}
