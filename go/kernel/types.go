package kernel

import (
	"context"
	"os/exec"
	"sync"
	"time"
)

// ProcessState tracks individual agent/process execution
type ProcessState struct {
	ID         string    `json:"id"`
	Agent      string    `json:"agent"`
	Phase      string    `json:"phase"`
	Status     string    `json:"status"` // idle, running, paused, killed, terminating
	StartTime  time.Time `json:"start_time"`
	GPU        int       `json:"gpu"`         // GPU ID if assigned
	VRAMUsage  float64   `json:"vram_usage"`  // GB
	TokenCount int       `json:"token_count"` // cumulative
	LastOutput string    `json:"last_output"`
	// Internal control fields (not exposed via JSON)
	Ctx      context.Context    `json:"-"`
	Cancel   context.CancelFunc `json:"-"`
	Cmd      *exec.Cmd          `json:"-"` // *exec.Cmd type
	WaitChan chan error         `json:"-"` // Channel to notify when process exits
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
	mu                sync.RWMutex     `json:"-"` // Internal use only
}

// SystemState represents the overall system snapshot
type SystemState struct {
	ActiveProcesses int                      `json:"active_processes"`
	TotalProcesses  int                      `json:"total_processes"`
	TotalVRAM       float64                  `json:"total_vram"`
	TotalTokens     int                      `json:"total_tokens"`
	Processes       map[string]*ProcessState `json:"processes"`
	Waria           *WariaState              `json:"waria"`
}
