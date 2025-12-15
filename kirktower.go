package main

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"os/exec"
	"sync"
	"time"

	"github.com/gorilla/websocket"
)

// ProcessState tracks individual agent/process execution
type ProcessState struct {
	ID         string    `json:"id"`
	Agent      string    `json:"agent"`
	Phase      string    `json:"phase"`
	Status     string    `json:"status"` // idle, running, paused, killed
	StartTime  time.Time `json:"start_time"`
	GPU        int       `json:"gpu"`         // GPU ID if assigned
	VRAMUsage  float64   `json:"vram_usage"`  // GB
	TokenCount int       `json:"token_count"` // cumulative
	LastOutput string    `json:"last_output"`
	Ctx        context.Context
	Cancel     context.CancelFunc
}

// WariaThreshold monitors reasoning horizon breaches
type WariaThreshold struct {
	Name      string  `json:"name"`
	Current   float64 `json:"current"`
	Threshold float64 `json:"threshold"`
	Breached  bool    `json:"breached"`
}

// WariaState tracks meta-cognitive hygiene
type WariaState struct {
	PromptLength      int              `json:"prompt_length"`
	ContextReuse      int              `json:"context_reuse"`
	CrossPhaseRefs    int              `json:"cross_phase_refs"`
	ConfidencePlateau bool             `json:"confidence_plateau"`
	VerbosityIncrease bool             `json:"verbosity_increase"`
	Thresholds        []WariaThreshold `json:"thresholds"`
	TipPackets        []string         `json:"tip_packets"`
	mu                sync.RWMutex
}

// TowerControl is Kirktower's main control system
type TowerControl struct {
	processes map[string]*ProcessState
	waria     *WariaState
	mu        sync.RWMutex
	wsClients map[*websocket.Conn]bool
	clientsMu sync.RWMutex
	broadcast chan interface{}
}

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

// StartProcess launches a new agent process
func (tc *TowerControl) StartProcess(agent, phase string, gpuID int) (string, error) {
	tc.mu.Lock()
	defer tc.mu.Unlock()

	id := fmt.Sprintf("%s-%d", agent, time.Now().Unix())
	ctx, cancel := context.WithCancel(context.Background())

	ps := &ProcessState{
		ID:        id,
		Agent:     agent,
		Phase:     phase,
		Status:    "running",
		StartTime: time.Now(),
		GPU:       gpuID,
		Ctx:       ctx,
		Cancel:    cancel,
	}

	tc.processes[id] = ps
	tc.broadcastState()

	// Start monitoring goroutine
	go tc.monitorProcess(ps)

	return id, nil
}

// PauseProcess suspends execution
func (tc *TowerControl) PauseProcess(id string) error {
	tc.mu.Lock()
	defer tc.mu.Unlock()

	ps, exists := tc.processes[id]
	if !exists {
		return fmt.Errorf("process %s not found", id)
	}

	if ps.Status != "running" {
		return fmt.Errorf("process %s not running", id)
	}

	ps.Status = "paused"
	tc.broadcastState()
	return nil
}

// ResumeProcess continues execution
func (tc *TowerControl) ResumeProcess(id string) error {
	tc.mu.Lock()
	defer tc.mu.Unlock()

	ps, exists := tc.processes[id]
	if !exists {
		return fmt.Errorf("process %s not found", id)
	}

	if ps.Status != "paused" {
		return fmt.Errorf("process %s not paused", id)
	}

	ps.Status = "running"
	tc.broadcastState()
	return nil
}

// KillProcess terminates execution
func (tc *TowerControl) KillProcess(id string) error {
	tc.mu.Lock()
	defer tc.mu.Unlock()

	ps, exists := tc.processes[id]
	if !exists {
		return fmt.Errorf("process %s not found", id)
	}

	ps.Cancel()
	ps.Status = "killed"
	tc.broadcastState()
	return nil
}

// KillLoop terminates all processes in a specific loop
func (tc *TowerControl) KillLoop(loop string) error {
	tc.mu.Lock()
	defer tc.mu.Unlock()

	killed := 0
	for _, ps := range tc.processes {
		if ps.Phase == loop && ps.Status == "running" {
			ps.Cancel()
			ps.Status = "killed"
			killed++
		}
	}

	tc.broadcastState()
	log.Printf("Killed %d processes in loop %s", killed, loop)
	return nil
}

// GetSystemState returns current system snapshot
func (tc *TowerControl) GetSystemState() map[string]interface{} {
	tc.mu.RLock()
	defer tc.mu.RUnlock()

	activeCount := 0
	totalVRAM := 0.0
	totalTokens := 0

	for _, ps := range tc.processes {
		if ps.Status == "running" {
			activeCount++
			totalVRAM += ps.VRAMUsage
			totalTokens += ps.TokenCount
		}
	}

	return map[string]interface{}{
		"active_processes": activeCount,
		"total_processes":  len(tc.processes),
		"total_vram":       totalVRAM,
		"total_tokens":     totalTokens,
		"processes":        tc.processes,
		"waria":            tc.waria,
	}
}

// monitorProcess tracks individual process metrics
func (tc *TowerControl) monitorProcess(ps *ProcessState) {
	ticker := time.NewTicker(2 * time.Second)
	defer ticker.Stop()

	for {
		select {
		case <-ps.Ctx.Done():
			return
		case <-ticker.C:
			tc.updateProcessMetrics(ps)
		}
	}
}

// updateProcessMetrics polls GPU and token usage
func (tc *TowerControl) updateProcessMetrics(ps *ProcessState) {
	tc.mu.Lock()
	defer tc.mu.Unlock()

	// Query nvidia-smi for VRAM usage
	if ps.GPU >= 0 {
		cmd := exec.Command("nvidia-smi",
			"--query-gpu=memory.used",
			"--format=csv,noheader,nounits",
			fmt.Sprintf("--id=%d", ps.GPU))

		output, err := cmd.Output()
		if err == nil {
			var vram float64
			fmt.Sscanf(string(output), "%f", &vram)
			ps.VRAMUsage = vram / 1024.0 // Convert to GB
		}
	}

	tc.broadcastState()
}

// WariaUpdate processes new agent output for threshold detection
func (tc *TowerControl) WariaUpdate(agent, output string, tokenCount int) {
	tc.waria.mu.Lock()
	defer tc.waria.mu.Unlock()

	// Update prompt length threshold
	tc.waria.PromptLength = tokenCount
	tc.waria.Thresholds[0].Current = float64(tokenCount)

	if tokenCount > int(tc.waria.Thresholds[0].Threshold) && !tc.waria.Thresholds[0].Breached {
		tc.waria.Thresholds[0].Breached = true
		tc.emitTipPacket("prompt_growth", agent)
	}

	// Check for verbosity increase (simple heuristic)
	if len(output) > 5000 && tokenCount > 2000 {
		if !tc.waria.VerbosityIncrease {
			tc.waria.VerbosityIncrease = true
			tc.emitTipPacket("verbosity", agent)
		}
	}

	tc.broadcastWaria()
}

// emitTipPacket generates Waria's menu-style suggestions
func (tc *TowerControl) emitTipPacket(threshold, agent string) {
	var tip string

	switch threshold {
	case "prompt_growth":
		tip = fmt.Sprintf(`WARIA TIP – Reasoning Horizon Detected (%s)

You may be exceeding the useful planning horizon for this phase.

Common options:
[1] Freeze scope and proceed with skeleton only
[2] Ask user a clarifying constraint question
[3] Defer this concern to next sprint
[4] Ignore (log only)

No action is required.`, agent)

	case "verbosity":
		tip = fmt.Sprintf(`WARIA TIP – Verbosity Increase (%s)

Output length increasing while token efficiency decreasing.

Common options:
[1] Request more concise output format
[2] Split task into smaller chunks
[3] Review exemplars for better templates
[4] Continue as-is

No action is required.`, agent)
	}

	tc.waria.TipPackets = append(tc.waria.TipPackets, tip)
	log.Println(tip)
}

// broadcaster sends state updates to all WebSocket clients
func (tc *TowerControl) broadcaster() {
	for msg := range tc.broadcast {
		tc.clientsMu.RLock()
		for client := range tc.wsClients {
			err := client.WriteJSON(msg)
			if err != nil {
				client.Close()
				delete(tc.wsClients, client)
			}
		}
		tc.clientsMu.RUnlock()
	}
}

func (tc *TowerControl) broadcastState() {
	tc.broadcast <- tc.GetSystemState()
}

func (tc *TowerControl) broadcastWaria() {
	tc.waria.mu.RLock()
	defer tc.waria.mu.RUnlock()

	tc.broadcast <- map[string]interface{}{
		"type":  "waria_update",
		"waria": tc.waria,
	}
}

// HTTP Handlers
var upgrader = websocket.Upgrader{
	CheckOrigin: func(r *http.Request) bool { return true },
}

func (tc *TowerControl) handleWebSocket(w http.ResponseWriter, r *http.Request) {
	conn, err := upgrader.Upgrade(w, r, nil)
	if err != nil {
		log.Println("WebSocket upgrade error:", err)
		return
	}

	tc.clientsMu.Lock()
	tc.wsClients[conn] = true
	tc.clientsMu.Unlock()

	// Send initial state
	conn.WriteJSON(tc.GetSystemState())

	// Read commands from client
	for {
		var cmd map[string]interface{}
		err := conn.ReadJSON(&cmd)
		if err != nil {
			tc.clientsMu.Lock()
			delete(tc.wsClients, conn)
			tc.clientsMu.Unlock()
			conn.Close()
			break
		}

		tc.handleCommand(cmd, conn)
	}
}

func (tc *TowerControl) handleCommand(cmd map[string]interface{}, conn *websocket.Conn) {
	action := cmd["action"].(string)

	var response map[string]interface{}

	switch action {
	case "start":
		agent := cmd["agent"].(string)
		phase := cmd["phase"].(string)
		gpu := int(cmd["gpu"].(float64))
		id, err := tc.StartProcess(agent, phase, gpu)
		if err != nil {
			response = map[string]interface{}{"error": err.Error()}
		} else {
			response = map[string]interface{}{"success": true, "id": id}
		}

	case "pause":
		id := cmd["id"].(string)
		err := tc.PauseProcess(id)
		if err != nil {
			response = map[string]interface{}{"error": err.Error()}
		} else {
			response = map[string]interface{}{"success": true}
		}

	case "resume":
		id := cmd["id"].(string)
		err := tc.ResumeProcess(id)
		if err != nil {
			response = map[string]interface{}{"error": err.Error()}
		} else {
			response = map[string]interface{}{"success": true}
		}

	case "kill":
		id := cmd["id"].(string)
		err := tc.KillProcess(id)
		if err != nil {
			response = map[string]interface{}{"error": err.Error()}
		} else {
			response = map[string]interface{}{"success": true}
		}

	case "kill_loop":
		loop := cmd["loop"].(string)
		err := tc.KillLoop(loop)
		if err != nil {
			response = map[string]interface{}{"error": err.Error()}
		} else {
			response = map[string]interface{}{"success": true}
		}
	}

	conn.WriteJSON(response)
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

func main() {
	tower := NewTowerControl()

	// REST API
	http.HandleFunc("/api/state", tower.handleState)
	http.HandleFunc("/api/waria", tower.handleWariaUpdate)

	// WebSocket for real-time updates
	http.HandleFunc("/ws", tower.handleWebSocket)

	// Serve CLI frontend
	http.Handle("/", http.FileServer(http.Dir("./web")))

	port := os.Getenv("KIRKTOWER_PORT")
	if port == "" {
		port = "9090"
	}

	log.Printf("Kirktower Control Tower listening on :%s", port)
	log.Fatal(http.ListenAndServe(":"+port, nil))
}
