package kernel

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"net/http"
	"os"
	"sync"
	"time"
)

// =============================================================================
// INTER-BOX MCP PROXY (4-Node Cluster Communication)
// =============================================================================

// BoxConfig represents a remote box's configuration
type BoxConfig struct {
	Name     string `json:"name"`
	BaseURL  string `json:"base_url"`
	Enabled  bool   `json:"enabled"`
	Priority int    `json:"priority"` // Higher = prefer this box
}

// MCPProxy handles routing between boxes
type MCPProxy struct {
	boxes      map[string]*BoxConfig
	httpClient *http.Client
	mu         sync.RWMutex

	// Auto-start Box 4 logic
	box4AutoStart bool
	box4IdleTimer *time.Timer
}

// NewMCPProxy creates the inter-box proxy
func NewMCPProxy() *MCPProxy {
	proxy := &MCPProxy{
		boxes: make(map[string]*BoxConfig),
		httpClient: &http.Client{
			Timeout: 30 * time.Second,
		},
		box4AutoStart: true,
	}

	// Load box configuration from environment
	proxy.loadBoxConfig()

	return proxy
}

// loadBoxConfig reads box addresses from environment variables
func (p *MCPProxy) loadBoxConfig() {
	// Box 1 (D-Agents - Orchestration) - Current box
	p.boxes["box1"] = &BoxConfig{
		Name:     "Box1_D_Agents",
		BaseURL:  getEnv("BOX1_URL", "http://localhost:8080"),
		Enabled:  true,
		Priority: 10,
	}

	// Box 2 (B-C Agents - AWS g5.xlarge)
	p.boxes["box2"] = &BoxConfig{
		Name:     "Box2_BC_Agents",
		BaseURL:  getEnv("BOX2_URL", "http://box2.internal:8083"), // Vision MCP entry point
		Enabled:  getEnv("BOX2_ENABLED", "false") == "true",
		Priority: 8,
	}

	// Box 3 (Clash - GitHub Codespace)
	p.boxes["box3"] = &BoxConfig{
		Name:     "Box3_Clash",
		BaseURL:  getEnv("BOX3_URL", "http://localhost:8086"), // Clash MCP
		Enabled:  getEnv("BOX3_ENABLED", "false") == "true",
		Priority: 5,
	}

	// Box 4 (A-Agents - Google Cloud)
	p.boxes["box4"] = &BoxConfig{
		Name:     "Box4_A_Agents",
		BaseURL:  getEnv("BOX4_URL", "http://box4.internal:11434"), // Ollama endpoint
		Enabled:  getEnv("BOX4_ENABLED", "false") == "true",
		Priority: 3, // Low priority (expensive, on-demand)
	}

	log.Printf("[MCP Proxy] Loaded %d box configurations", len(p.boxes))
}

// RouteByAgent determines which box should handle a given agent
func (p *MCPProxy) RouteByAgent(agent string) (*BoxConfig, error) {
	p.mu.RLock()
	defer p.mu.RUnlock()

	// UPDATED Agent → Box mapping for 4-box architecture
	agentBoxMap := map[string]string{
		// Box 1 (D-Agents - Orchestration) - Local
		"D1_Puckfairy": "box1",
		"D2_Diplo":     "box1",

		// Box 2 (B-C Agents - AWS g5.xlarge)
		"B1_Concrete": "box2", // Vision/Voice/Browser tools
		"C1_Bash":     "box2", // Shell automation

		// Box 3 (Clash - GitHub Codespace)
		"C2_Clash": "box3",

		// Box 4 (A-Agents - Google Cloud)
		"A1_Josie":  "box4",
		"A2_Roark":  "box4",
		"C3_Gunash": "box4", // Uses Cogito on Google Cloud
	}

	boxName, exists := agentBoxMap[agent]
	if !exists {
		return nil, fmt.Errorf("agent %s not found in routing table", agent)
	}

	box, exists := p.boxes[boxName]
	if !exists {
		return nil, fmt.Errorf("box %s not configured", boxName)
	}

	if !box.Enabled {
		// Special case: Box 4 auto-start (Google Cloud)
		if boxName == "box4" && p.box4AutoStart {
			log.Printf("[MCP Proxy] Box 4 offline, attempting auto-start")
			if err := p.startBox4(); err != nil {
				return nil, fmt.Errorf("failed to start box4: %v", err)
			}
			box.Enabled = true
		} else {
			return nil, fmt.Errorf("box %s is disabled", boxName)
		}
	}

	return box, nil
}

// ProxyRequest forwards an MCP request to the appropriate box
func (p *MCPProxy) ProxyRequest(agent string, method string, params interface{}) (interface{}, error) {
	// 1. Determine target box
	box, err := p.RouteByAgent(agent)
	if err != nil {
		return nil, err
	}

	// 2. If target is current box (box1), handle locally
	if box.Name == "Box1_D_Agents" {
		return nil, fmt.Errorf("local handling not via proxy")
	}

	// 3. Build MCP JSON-RPC request
	mcpRequest := map[string]interface{}{
		"jsonrpc": "2.0",
		"id":      time.Now().UnixNano(),
		"method":  method,
		"params": map[string]interface{}{
			"agent":  agent,
			"params": params,
		},
	}

	// 4. Serialize request
	requestBody, err := json.Marshal(mcpRequest)
	if err != nil {
		return nil, fmt.Errorf("failed to marshal request: %v", err)
	}

	// 5. Send HTTP request to remote box
	url := fmt.Sprintf("%s/mcp", box.BaseURL)
	log.Printf("[MCP Proxy] Routing %s → %s (%s)", agent, box.Name, url)

	req, err := http.NewRequest("POST", url, bytes.NewBuffer(requestBody))
	if err != nil {
		return nil, fmt.Errorf("failed to create request: %v", err)
	}

	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("X-Forwarded-From", "box1")

	// Add authentication token if configured
	if token := os.Getenv("MCP_SHARED_SECRET"); token != "" {
		req.Header.Set("Authorization", fmt.Sprintf("Bearer %s", token))
	}

	// 6. Execute request
	resp, err := p.httpClient.Do(req)
	if err != nil {
		return nil, fmt.Errorf("failed to send request: %v", err)
	}
	defer resp.Body.Close()

	// 7. Parse response
	responseBody, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("failed to read response: %v", err)
	}

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("remote box returned error: %d - %s", resp.StatusCode, string(responseBody))
	}

	var mcpResponse map[string]interface{}
	if err := json.Unmarshal(responseBody, &mcpResponse); err != nil {
		return nil, fmt.Errorf("failed to parse response: %v", err)
	}

	// 8. Check for JSON-RPC error
	if errObj, exists := mcpResponse["error"]; exists {
		return nil, fmt.Errorf("remote error: %v", errObj)
	}

	// 9. Return result
	return mcpResponse["result"], nil
}

// =============================================================================
// BOX 4 AUTO-START LOGIC
// =============================================================================

// startBox4 attempts to start the Box 4 instance (AWS EC2)
func (p *MCPProxy) startBox4() error {
	log.Println("[MCP Proxy] Starting Box 4 (Big Brain)...")

	// Check if AWS CLI is available
	awsRegion := getEnv("AWS_REGION", "us-east-1")
	box4InstanceID := getEnv("BOX4_INSTANCE_ID", "")

	if box4InstanceID == "" {
		return fmt.Errorf("BOX4_INSTANCE_ID not set")
	}

	// Execute AWS CLI command to start instance
	cmd := fmt.Sprintf("aws ec2 start-instances --region %s --instance-ids %s", awsRegion, box4InstanceID)
	log.Printf("[MCP Proxy] Executing: %s", cmd)

	// TODO: Replace with AWS SDK call in production
	// For now, simulate success
	log.Println("[MCP Proxy] Box 4 start initiated (simulated)")

	// Wait for instance to boot
	log.Println("[MCP Proxy] Waiting for Box 4 to boot (120s timeout)...")
	if err := p.waitForBox4Health(120 * time.Second); err != nil {
		return fmt.Errorf("box4 failed to start: %v", err)
	}

	log.Println("[MCP Proxy] Box 4 online and ready")

	// Start idle timer for auto-shutdown
	p.startBox4IdleTimer()

	return nil
}

// waitForBox4Health polls Box 4 health endpoint until ready
func (p *MCPProxy) waitForBox4Health(timeout time.Duration) error {
	box4URL := p.boxes["box4"].BaseURL
	healthURL := fmt.Sprintf("%s/health", box4URL)

	deadline := time.Now().Add(timeout)
	for time.Now().Before(deadline) {
		resp, err := p.httpClient.Get(healthURL)
		if err == nil && resp.StatusCode == http.StatusOK {
			resp.Body.Close()
			return nil
		}
		if resp != nil {
			resp.Body.Close()
		}

		time.Sleep(5 * time.Second)
	}

	return fmt.Errorf("timeout waiting for box4 health check")
}

// startBox4IdleTimer starts a timer to auto-shutdown Box 4 after 2 hours idle
func (p *MCPProxy) startBox4IdleTimer() {
	if p.box4IdleTimer != nil {
		p.box4IdleTimer.Stop()
	}

	p.box4IdleTimer = time.AfterFunc(2*time.Hour, func() {
		log.Println("[MCP Proxy] Box 4 idle timeout reached, shutting down...")
		p.stopBox4()
	})
}

// ResetBox4IdleTimer resets the idle timer (called on each Box 4 request)
func (p *MCPProxy) ResetBox4IdleTimer() {
	if p.box4IdleTimer != nil {
		p.box4IdleTimer.Reset(2 * time.Hour)
	}
}

// stopBox4 shuts down Box 4 to save costs
func (p *MCPProxy) stopBox4() error {
	log.Println("[MCP Proxy] Stopping Box 4 (Big Brain)...")

	awsRegion := getEnv("AWS_REGION", "us-east-1")
	box4InstanceID := getEnv("BOX4_INSTANCE_ID", "")

	if box4InstanceID == "" {
		return fmt.Errorf("BOX4_INSTANCE_ID not set")
	}

	// Execute AWS CLI command to stop instance
	cmd := fmt.Sprintf("aws ec2 stop-instances --region %s --instance-ids %s", awsRegion, box4InstanceID)
	log.Printf("[MCP Proxy] Executing: %s", cmd)

	// TODO: Replace with AWS SDK call in production
	log.Println("[MCP Proxy] Box 4 stop initiated (simulated)")

	p.boxes["box4"].Enabled = false

	return nil
}

// =============================================================================
// VISION FALLBACK ROUTING
// =============================================================================

// VisionFallback handles Box 3 → Box 4 escalation for complex vision
func (p *MCPProxy) VisionFallback(imageURL string, question string, clipConfidence float64) (interface{}, error) {
	log.Printf("[MCP Proxy] Vision fallback triggered (CLIP confidence: %.2f)", clipConfidence)

	// 1. Ensure Box 4 is online
	box4, err := p.RouteByAgent("A1_Roark") // Any Box 4 agent works
	if err != nil {
		return nil, fmt.Errorf("cannot reach Box 4: %v", err)
	}

	// 2. Build vision request
	visionRequest := map[string]interface{}{
		"image_url":       imageURL,
		"question":        question,
		"model":           "qwen3-vl:32b",
		"mode":            "detailed",
		"clip_confidence": clipConfidence,
	}

	// 3. Send to Box 4 vision endpoint
	requestBody, _ := json.Marshal(visionRequest)
	url := fmt.Sprintf("%s/vision/complex", box4.BaseURL)

	log.Printf("[MCP Proxy] Escalating to Box 4 vision: %s", url)

	req, err := http.NewRequest("POST", url, bytes.NewBuffer(requestBody))
	if err != nil {
		return nil, err
	}
	req.Header.Set("Content-Type", "application/json")

	resp, err := p.httpClient.Do(req)
	if err != nil {
		return nil, fmt.Errorf("vision fallback failed: %v", err)
	}
	defer resp.Body.Close()

	responseBody, _ := ioutil.ReadAll(resp.Body)
	var result map[string]interface{}
	json.Unmarshal(responseBody, &result)

	// 4. Reset Box 4 idle timer
	p.ResetBox4IdleTimer()

	return result, nil
}

// =============================================================================
// HTTP HANDLERS
// =============================================================================

// ServeHTTP handles proxy HTTP requests
func (p *MCPProxy) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	var request struct {
		Agent  string      `json:"agent"`
		Method string      `json:"method"`
		Params interface{} `json:"params"`
	}

	if err := json.NewDecoder(r.Body).Decode(&request); err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	result, err := p.ProxyRequest(request.Agent, request.Method, request.Params)
	if err != nil {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusInternalServerError)
		json.NewEncoder(w).Encode(map[string]interface{}{
			"error": err.Error(),
		})
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]interface{}{
		"success": true,
		"result":  result,
	})
}

// =============================================================================
// UTILITY FUNCTIONS
// =============================================================================

func getEnv(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}
