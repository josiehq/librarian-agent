package main

import (
	"context"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"os/exec"
	"strings"
	"sync"
	"time"

	"github.com/gorilla/websocket"
)

// NOTE: The struct definitions (ProcessState, WariaState, SystemState) are defined in types.go
// This file depends on types.go being compiled together (e.g., go run *.go or go build)


// =============================================================================
// TOWER CONTROL - CORE STATE MANAGEMENT
// =============================================================================

// TowerControl is Kirktower's main control system
type TowerControl struct {
	processes map[string]*ProcessState
	waria     *WariaState
	mu        sync.RWMutex 
	wsClients map[*websocket.Conn]bool
	clientsMu sync.RWMutex
	broadcast chan interface{}
}

// NOTE: MCPRequest and MCPResponse are defined in mcp_server.go

// NewTowerControl initializes the control tower
func NewTowerControl() *TowerControl {
	tc := &TowerControl{
		processes: make(map[string]*ProcessState),
		waria: &WariaState{
			Thresholds: []WariaThreshold{
				{Name: "prompt_growth", Threshold: 8000, Current: 0},
				{Name: "context_reuse", Threshold: 5, Current: 0},
				{Name: "abstraction_drift", Threshold: 0.7, Current: 0},
			},
			TipPackets: []string{},
		},
		wsClients: make(map[*websocket.Conn]bool),
		broadcast: make(chan interface{}, 100),
	}

	go tc.broadcaster()
	return tc
}

// =============================================================================
// PROCESS MANAGEMENT
// =============================================================================

// StartProcess launches a new agent process
func (tc *TowerControl) StartProcess(agent, phase string, gpuID int) (string, error) {
	tc.mu.Lock()
	defer tc.mu.Unlock()

	id := fmt.Sprintf("proc-%d", time.Now().UnixNano()/int64(time.Millisecond))
	
	ctx, cancel := context.WithCancel(context.Background())

	ps := &ProcessState{
		ID:        id,
		Agent:     agent,
		Phase:     phase,
		Status:    "running",
		StartTime: time.Now(),
		GPU:       gpuID,
		VRAMUsage: 0.1, // Small starting VRAM usage
		Ctx:       ctx,
		Cancel:    cancel,
		WaitChan:  make(chan error),
	}

	// SIMULATION: Launch a simple command that runs indefinitely until killed/canceled
	// In a real system, this would be a Docker container command.
	cmd := exec.CommandContext(ctx, "sleep", "3600") 
	ps.Cmd = cmd
	
	tc.processes[id] = ps
	
	go func() {
		err := ps.Cmd.Start() // Start the process

		if err == nil {
			ps.WaitChan <- ps.Cmd.Wait()
		} else {
			ps.WaitChan <- err
		}
		
		tc.mu.Lock()
		if ps.Status == "running" || ps.Status == "terminating" {
			ps.Status = "killed"
			ps.LastOutput = fmt.Sprintf("Process exited unexpectedly: %v", err)
		}
		ps.Cancel()
		tc.mu.Unlock()
		tc.broadcast <- tc.GetSystemState()
	}()

	tc.broadcast <- tc.GetSystemState()
	return id, nil
}

// KillProcess attempts to terminate a running process
func (tc *TowerControl) KillProcess(id string) error {
	tc.mu.Lock()
	defer tc.mu.Unlock()

	ps, exists := tc.processes[id]
	if !exists {
		return fmt.Errorf("process %s not found", id)
	}
	if ps.Status == "killed" || ps.Status == "terminating" {
		return nil
	}
	
	ps.Status = "terminating"
	ps.Cancel() // Triggers the CommandContext to kill the process

	go func() {
		<-ps.WaitChan
		tc.mu.Lock()
		ps.Status = "killed"
		ps.LastOutput = fmt.Sprintf("Process manually killed at %s", time.Now().Format("15:04:05"))
		tc.mu.Unlock()
		tc.broadcast <- tc.GetSystemState()
	}()
	
	tc.broadcast <- tc.GetSystemState()
	return nil
}

// KillLoop terminates all processes associated with a given phase/loop
func (tc *TowerControl) KillLoop(phase string) error {
	tc.mu.RLock()
	defer tc.mu.RUnlock()
	
	killedCount := 0
	for id, ps := range tc.processes {
		if ps.Phase == phase && (ps.Status == "running" || ps.Status == "paused") {
			tc.KillProcess(id)
			killedCount++
		}
	}
	
	if killedCount == 0 {
		return fmt.Errorf("no running processes found in phase %s", phase)
	}
	return nil
}

// togglePause handles pause/resume logic
func (tc *TowerControl) togglePause(id string, pause bool) map[string]interface{} {
	tc.mu.Lock()
	defer tc.mu.Unlock()
	
	ps, exists := tc.processes[id]
	if !exists { return map[string]interface{}{"error": "process not found"} }

	targetStatus := "running"
	if pause { targetStatus = "paused" }
	
	// SIMULATION: In a real system, we'd send SIGSTOP/SIGCONT to the process
	if ps.Cmd != nil && ps.Cmd.Process != nil {
		// Example: ps.Cmd.Process.Signal(syscall.SIGSTOP/syscall.SIGCONT)
	}

	ps.Status = targetStatus
	ps.LastOutput = fmt.Sprintf("Process %s at %s", targetStatus, time.Now().Format("15:04:05"))
	tc.broadcast <- tc.GetSystemState()
	return map[string]interface{}{"success": true, "status": targetStatus}
}

// processCommand handles commands from WebSocket or HTTP
func (tc *TowerControl) processCommand(cmd map[string]interface{}) map[string]interface{} {
	action, ok := cmd["action"].(string)
	if !ok {
		return map[string]interface{}{"error": "missing action"}
	}

	id, idOk := cmd["id"].(string)
	loop, loopOk := cmd["loop"].(string)

	switch action {
	case "pause", "resume":
		if !idOk { return map[string]interface{}{"error": "missing id for pause/resume"} }
		return tc.togglePause(id, action == "pause")
		
	case "kill":
		if !idOk { return map[string]interface{}{"error": "missing id for kill"} }
		if err := tc.KillProcess(id); err != nil {
			return map[string]interface{}{"error": err.Error()}
		}
		return map[string]interface{}{"success": true}
		
	case "kill_loop":
		if !loopOk { return map[string]interface{}{"error": "missing loop for kill_loop"} }
		if err := tc.KillLoop(loop); err != nil {
			return map[string]interface{}{"error": err.Error()}
		}
		return map[string]interface{}{"success": true}
	default:
		return map[string]interface{}{"error": "unknown action"}
	}
}


// =============================================================================
// STATE & BROADCASTING
// =============================================================================

// GetSystemState aggregates the current status for the CLI
func (tc *TowerControl) GetSystemState() SystemState {
	tc.mu.RLock()
	defer tc.mu.RUnlock()

	state := SystemState{
		Processes: make(map[string]*ProcessState),
		Waria:     tc.waria,
	}

	activeCount := 0
	totalVRAM := 0.0
	totalTokens := 0

	for id, ps := range tc.processes {
		state.Processes[id] = ps
		
		if ps.Status == "running" {
			activeCount++
			// Simulate VRAM usage growth
			ps.VRAMUsage += 0.01 
			ps.TokenCount += 100 // Simulate token generation
			totalVRAM += ps.VRAMUsage
		}
		totalTokens += ps.TokenCount
	}

	state.ActiveProcesses = activeCount
	state.TotalProcesses = len(tc.processes)
	state.TotalVRAM = totalVRAM
	state.TotalTokens = totalTokens
	return state
}

// broadcaster sends the system state to all connected WebSocket clients
func (tc *TowerControl) broadcaster() {
	for {
		state := <-tc.broadcast // Wait for a message on the broadcast channel
		
		tc.clientsMu.RLock()
		clients := make(map[*websocket.Conn]bool)
		for client := range tc.wsClients {
			clients[client] = true
		}
		tc.clientsMu.RUnlock()

		for client := range clients {
			err := client.WriteJSON(state)
			if err != nil {
				log.Printf("WebSocket error: %v, client removed", err)
				client.Close()
				tc.clientsMu.Lock()
				delete(tc.wsClients, client)
				tc.clientsMu.Unlock()
			}
		}
	}
}

// WariaUpdate receives updates from agents and checks thresholds
func (tc *TowerControl) WariaUpdate(agent, output string, tokenCount int) {
	tc.waria.mu.Lock()
	defer tc.waria.mu.Unlock()

	// 1. Update Process State (Token Count, Last Output)
	for _, ps := range tc.processes {
		if ps.Agent == agent {
			ps.TokenCount += tokenCount
			ps.LastOutput = output
		}
	}
	
	// 2. Update Waria State Metrics
	tc.waria.PromptLength += len(output) / 10
	tc.waria.ContextReuse++ 
	
	// 3. Check Thresholds
	for i := range tc.waria.Thresholds {
		t := &tc.waria.Thresholds[i]
		switch t.Name {
		case "prompt_growth":
			t.Current = float64(tc.waria.PromptLength)
		case "context_reuse":
			t.Current = float64(tc.waria.ContextReuse)
		}
		t.Breached = t.Current > t.Threshold
	}

	// 4. Update Tip Packets (e.g., if a breach occurs)
	if tc.waria.Thresholds[0].Breached && len(tc.waria.TipPackets) == 0 {
		tc.waria.TipPackets = append(tc.waria.TipPackets, "High prompt growth detected. Consider aggressive summarization.")
	}

	// 5. Broadcast new state
	tc.broadcast <- tc.GetSystemState()
}


// =============================================================================
// MULTI-CORE PROCESSOR (MCP) - AGENT TOOL INTERFACE
// =============================================================================

// tool_ContainerExec is the audited wrapper for code execution (Docker)
func (tc *TowerControl) tool_ContainerExec(arguments []interface{}) MCPResponse {
	// arguments: [command string, agent_id string]
	if len(arguments) < 2 {
		return MCPResponse{Error: "container_exec requires command and agent_id", Success: false}
	}
	command := arguments[0].(string)
	agentID := arguments[1].(string)
	
	log.Printf("[MCP AUDIT] Agent %s executing: %s", agentID, command)

	// Simulated Command Output
	if strings.Contains(command, "test") {
		return MCPResponse{Output: "TESTS PASSED: All 45 unit tests passed in 1.2s.", Success: true}
	}
	if strings.Contains(command, "build") {
		return MCPResponse{Output: "BUILD COMPLETE: Artifact josiedesk-0.1.0.tar.gz created.", Success: true}
	}
	
	return MCPResponse{Output: fmt.Sprintf("[CONTAINER_EXEC] Executed: '%s'", command), Success: true}
}

// tool_MemoryCommit is the audited wrapper for writing to Diplo's memory
func (tc *TowerControl) tool_MemoryCommit(arguments []interface{}) MCPResponse {
	// arguments: [log_type string, content string, agent_id string]
	if len(arguments) < 3 {
		return MCPResponse{Error: "memory_commit requires log_type, content, and agent_id", Success: false}
	}
	// logType := arguments[0].(string)
	// content := arguments[1].(string)
	agentID := arguments[2].(string)
	
	log.Printf("[MCP AUDIT] Agent %s committed memory.", agentID)

	return MCPResponse{Output: fmt.Sprintf("[MEMORY_COMMIT] Log committed by Agent %s.", agentID), Success: true}
}

// handleMCPRequest is the JSON-RPC interface for Python agents
func (tc *TowerControl) handleMCPRequest(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "method not allowed", http.StatusMethodNotAllowed)
		return
	}
	
	var req MCPRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "invalid request body", http.StatusBadRequest)
		return
	}

	var response MCPResponse

	// Route the tool call to the corresponding native function
	switch req.Tool {
	case "container_exec":
		response = tc.tool_ContainerExec(req.Arguments)
	case "memory_commit":
		response = tc.tool_MemoryCommit(req.Arguments)
	case "container_upgrade_image":
		response = MCPResponse{Output: "CONTAINER_UPGRADE: Base image marked for next sprint.", Success: true}
	default:
		response = MCPResponse{Error: fmt.Sprintf("unknown tool: %s", req.Tool), Success: false}
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)
}


// =============================================================================
// HTTP & WS HANDLERS
// =============================================================================

var upgrader = websocket.Upgrader{
	CheckOrigin: func(r *http.Request) bool {
		return true // Allow all origins for local development
	},
}

func (tc *TowerControl) handleState(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(tc.GetSystemState())
}

func (tc *TowerControl) handleWariaUpdate(w http.ResponseWriter, r *http.Request) {
	var update struct {
		Agent      string `json:"agent"`
		Output     string `json:"output"`
		TokenCount int    `json:"token_count"`
	}

	if err := json.NewDecoder(r.Body).Decode(&update); err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	tc.WariaUpdate(update.Agent, update.Output, update.TokenCount)
	w.WriteHeader(http.StatusOK)
}

func (tc *TowerControl) handleWS(w http.ResponseWriter, r *http.Request) {
	conn, err := upgrader.Upgrade(w, r, nil)
	if err != nil {
		log.Println("WebSocket upgrade failed:", err)
		return
	}

	tc.clientsMu.Lock()
	tc.wsClients[conn] = true
	tc.clientsMu.Unlock()
	log.Printf("New WebSocket client connected: %s", conn.RemoteAddr())
	
	conn.WriteJSON(tc.GetSystemState())

	go func() {
		defer func() {
			conn.Close()
			tc.clientsMu.Lock()
			delete(tc.wsClients, conn)
			tc.clientsMu.Unlock()
			log.Printf("WebSocket client disconnected: %s", conn.RemoteAddr())
		}()
		
		for {
			var cmd map[string]interface{}
			err := conn.ReadJSON(&cmd)
			if err != nil {
				if websocket.IsCloseError(err, websocket.CloseGoingAway, websocket.CloseAbnormalClosure) {
				} else if err != io.EOF {
					log.Println("WebSocket read error:", err)
				}
				break
			}
			tc.handleCommandWS(conn, cmd)
		}
	}()
}

func (tc *TowerControl) handleCommandWS(conn *websocket.Conn, cmd map[string]interface{}) {
	response := tc.processCommand(cmd)
	conn.WriteJSON(response)
}


// =============================================================================
// MAIN FUNCTION
// =============================================================================

func main() {
	tower := NewTowerControl()
	
	// Initialize the MCP Server with TowerControl reference
	mcpServer := NewMCPServer(tower)
	
	// SIMULATE: Start initial processes for demonstration on the CLI
	tower.StartProcess("Clash", "C_LOOP_SPRINT", 0)
	tower.StartProcess("Bash", "C_LOOP_SPRINT", 0)
	tower.StartProcess("Diplo", "AUDIT_MEMORY", 1)

	// REST API Handlers
	http.HandleFunc("/api/state", tower.handleState)
	http.HandleFunc("/api/waria", tower.handleWariaUpdate)
	
	// CRITICAL MCP ENDPOINT (Agent Interface) - Uses MCPServer HTTP handler
	http.Handle("/api/mcp", mcpServer)

	// WebSocket for TUI CLI
	http.HandleFunc("/ws", tower.handleWS)

	port := ":8080"
	log.Printf("Kirktower Control Kernel starting on http://localhost%s", port)
	log.Printf("MCP Endpoint available at http://localhost%s/api/mcp", port)
	
	// Note: Must be run with `go run types.go kirktower.go mcp_server.go` or `go run *.go`
	if err := http.ListenAndServe(port, nil); err != nil {
		log.Fatal("ListenAndServe: ", err)
	}
}