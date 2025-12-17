package kernel

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"sync"
	"time"
)

// =============================================================================
// AGENT QUEUEING SYSTEM (D1 DIPLO + D3 WARIA)
// =============================================================================

// AgentRequest represents a request to run an agent with an LLM
type AgentRequest struct {
	ID           string                 `json:"id"`
	Agent        string                 `json:"agent"`            // e.g., "B3_Concrete"
	Task         string                 `json:"task"`             // Task description
	LLMModel     string                 `json:"llm_model"`        // e.g., "qwen3-vl:32b"
	Priority     int                    `json:"priority"`         // 0-10 (10 = highest)
	RequiredVRAM uint64                 `json:"required_vram_mb"` // Estimated VRAM needed
	Status       string                 `json:"status"`           // queued, running, completed, failed
	GPUAssigned  int                    `json:"gpu_assigned"`     // -1 if CPU-only
	SubmitTime   time.Time              `json:"submit_time"`
	StartTime    time.Time              `json:"start_time,omitempty"`
	EndTime      time.Time              `json:"end_time,omitempty"`
	Result       string                 `json:"result,omitempty"`
	Error        string                 `json:"error,omitempty"`
	Metadata     map[string]interface{} `json:"metadata,omitempty"`
}

// AgentQueue manages the execution queue for LLM agents
type AgentQueue struct {
	requests     map[string]*AgentRequest
	queue        chan *AgentRequest
	workers      int
	hwMonitor    *HardwareMonitor
	towerControl *TowerControl
	mu           sync.RWMutex
	workerWg     sync.WaitGroup
	ctx          context.Context
	cancel       context.CancelFunc
}

// NewAgentQueue creates the agent queueing system
func NewAgentQueue(workers int, hwMonitor *HardwareMonitor, tower *TowerControl) *AgentQueue {
	ctx, cancel := context.WithCancel(context.Background())

	aq := &AgentQueue{
		requests:     make(map[string]*AgentRequest),
		queue:        make(chan *AgentRequest, 100),
		workers:      workers,
		hwMonitor:    hwMonitor,
		towerControl: tower,
		ctx:          ctx,
		cancel:       cancel,
	}

	// Start worker goroutines
	for i := 0; i < workers; i++ {
		aq.workerWg.Add(1)
		go aq.worker(i)
	}

	log.Printf("Agent queue started with %d workers", workers)
	return aq
}

// Submit adds a new agent request to the queue
func (aq *AgentQueue) Submit(req *AgentRequest) error {
	aq.mu.Lock()
	defer aq.mu.Unlock()

	// Generate ID if not provided
	if req.ID == "" {
		req.ID = fmt.Sprintf("req-%d", time.Now().UnixNano()/int64(time.Millisecond))
	}

	// Set initial state
	req.Status = "queued"
	req.SubmitTime = time.Now()
	req.GPUAssigned = -1

	// Store request
	aq.requests[req.ID] = req

	// Add to queue (non-blocking)
	select {
	case aq.queue <- req:
		log.Printf("[Queue] Request %s submitted: %s (%s)", req.ID, req.Agent, req.LLMModel)
		return nil
	default:
		req.Status = "failed"
		req.Error = "queue full"
		return fmt.Errorf("queue full")
	}
}

// worker processes agent requests from the queue
func (aq *AgentQueue) worker(id int) {
	defer aq.workerWg.Done()
	log.Printf("[Worker %d] Started", id)

	for {
		select {
		case <-aq.ctx.Done():
			log.Printf("[Worker %d] Shutting down", id)
			return

		case req := <-aq.queue:
			log.Printf("[Worker %d] Processing request %s", id, req.ID)
			aq.processRequest(req)
		}
	}
}

// processRequest executes a single agent request
func (aq *AgentQueue) processRequest(req *AgentRequest) {
	// Update status
	aq.mu.Lock()
	req.Status = "running"
	req.StartTime = time.Now()
	aq.mu.Unlock()

	// 1. WARIA HARDWARE SELECTION
	// Find available GPU if VRAM required
	if req.RequiredVRAM > 0 {
		gpuID, err := aq.hwMonitor.FindAvailableGPU(req.RequiredVRAM)
		if err != nil {
			log.Printf("[Queue] No GPU available for %s: %v", req.ID, err)
			req.GPUAssigned = -1 // Fall back to CPU
		} else {
			req.GPUAssigned = gpuID
			log.Printf("[Queue] Assigned GPU %d to request %s", gpuID, req.ID)
		}
	}

	// 2. TOOL LIFECYCLE: INIT PHASE
	// (In real system, this would load the LLM into memory)
	log.Printf("[Queue] INIT: Loading %s on GPU %d", req.LLMModel, req.GPUAssigned)
	time.Sleep(500 * time.Millisecond) // Simulate model load time

	// 3. TOOL LIFECYCLE: USE PHASE
	// Execute the agent task (placeholder - in real system, call LLM API)
	log.Printf("[Queue] USE: Executing task for %s", req.Agent)
	result, err := aq.executeAgent(req)

	// 4. TOOL LIFECYCLE: CLEANUP PHASE
	// (In real system, unload model from GPU to free VRAM)
	log.Printf("[Queue] CLEANUP: Unloading %s from GPU %d", req.LLMModel, req.GPUAssigned)

	// 5. Update request state
	aq.mu.Lock()
	req.EndTime = time.Now()
	if err != nil {
		req.Status = "failed"
		req.Error = err.Error()
		log.Printf("[Queue] Request %s FAILED: %v", req.ID, err)
	} else {
		req.Status = "completed"
		req.Result = result
		log.Printf("[Queue] Request %s COMPLETED", req.ID)
	}
	aq.mu.Unlock()

	// 6. Update Kirktower state (Waria metrics)
	if aq.towerControl != nil {
		duration := req.EndTime.Sub(req.StartTime)
		aq.towerControl.WariaUpdate(
			req.Agent,
			fmt.Sprintf("Completed in %s", duration),
			1000, // Placeholder token count
		)
	}
}

// executeAgent calls Ollama to execute the agent task
func (aq *AgentQueue) executeAgent(req *AgentRequest) (string, error) {
	// Build Ollama request
	ollamaURL := "http://localhost:11434/api/generate"

	// Build agent-specific system prompt
	systemPrompt := fmt.Sprintf("You are %s. %s", req.Agent, req.Task)

	// Create payload
	payload := map[string]interface{}{
		"model":  req.LLMModel,
		"prompt": systemPrompt,
		"stream": false,
		"options": map[string]interface{}{
			"temperature": 0.7,
			"num_ctx":     4096,
		},
	}

	// Add metadata if present
	if req.Metadata != nil {
		if context, ok := req.Metadata["context"].(string); ok {
			payload["prompt"] = fmt.Sprintf("%s\n\nContext: %s", systemPrompt, context)
		}
	}

	// Marshal JSON
	payloadBytes, err := json.Marshal(payload)
	if err != nil {
		return "", fmt.Errorf("failed to marshal payload: %w", err)
	}

	// Make HTTP POST request
	client := &http.Client{Timeout: 120 * time.Second}
	resp, err := client.Post(ollamaURL, "application/json",
		bytes.NewReader(payloadBytes))
	if err != nil {
		return "", fmt.Errorf("ollama request failed: %w", err)
	}
	defer resp.Body.Close()

	// Check status
	if resp.StatusCode != http.StatusOK {
		return "", fmt.Errorf("ollama returned status %d", resp.StatusCode)
	}

	// Parse response
	var ollamaResp struct {
		Response string `json:"response"`
		Done     bool   `json:"done"`
	}

	if err := json.NewDecoder(resp.Body).Decode(&ollamaResp); err != nil {
		return "", fmt.Errorf("failed to decode ollama response: %w", err)
	}

	if !ollamaResp.Done {
		return "", fmt.Errorf("ollama response incomplete")
	}

	log.Printf("[Ollama] Agent %s completed: %d chars", req.Agent, len(ollamaResp.Response))
	return ollamaResp.Response, nil
}

// GetStatus returns the status of a specific request
func (aq *AgentQueue) GetStatus(id string) (*AgentRequest, error) {
	aq.mu.RLock()
	defer aq.mu.RUnlock()

	req, exists := aq.requests[id]
	if !exists {
		return nil, fmt.Errorf("request %s not found", id)
	}

	return req, nil
}

// GetAllRequests returns all requests
func (aq *AgentQueue) GetAllRequests() []*AgentRequest {
	aq.mu.RLock()
	defer aq.mu.RUnlock()

	requests := make([]*AgentRequest, 0, len(aq.requests))
	for _, req := range aq.requests {
		requests = append(requests, req)
	}

	return requests
}

// GetQueueDepth returns the number of queued requests
func (aq *AgentQueue) GetQueueDepth() int {
	return len(aq.queue)
}

// Shutdown gracefully stops the queue
func (aq *AgentQueue) Shutdown() {
	log.Println("[Queue] Shutting down...")
	aq.cancel()
	aq.workerWg.Wait()
	log.Println("[Queue] Shutdown complete")
}

// =============================================================================
// HTTP HANDLERS
// =============================================================================

// handleSubmit processes POST /api/queue/submit
func (aq *AgentQueue) handleSubmit(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	var req AgentRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	if err := aq.Submit(&req); err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]interface{}{
		"success":    true,
		"request_id": req.ID,
	})
}

// handleStatus processes GET /api/queue/status/:id
func (aq *AgentQueue) handleStatus(w http.ResponseWriter, r *http.Request) {
	// Extract ID from path (simplified - in production use a router)
	id := r.URL.Query().Get("id")
	if id == "" {
		http.Error(w, "Missing request ID", http.StatusBadRequest)
		return
	}

	req, err := aq.GetStatus(id)
	if err != nil {
		http.Error(w, err.Error(), http.StatusNotFound)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(req)
}

// handleList processes GET /api/queue/list
func (aq *AgentQueue) handleList(w http.ResponseWriter, r *http.Request) {
	requests := aq.GetAllRequests()

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]interface{}{
		"queue_depth":    aq.GetQueueDepth(),
		"total_requests": len(requests),
		"requests":       requests,
	})
}

// RegisterHandlers registers queue HTTP handlers
func (aq *AgentQueue) RegisterHandlers(mux *http.ServeMux) {
	mux.HandleFunc("/api/queue/submit", aq.handleSubmit)
	mux.HandleFunc("/api/queue/status", aq.handleStatus)
	mux.HandleFunc("/api/queue/list", aq.handleList)
}
