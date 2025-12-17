package kernel

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"net/http"
	"os/exec"
	"runtime"
	"strconv"
	"strings"
	"sync"
	"time"
)

// =============================================================================
// HARDWARE DETECTION (D3 WARIA)
// =============================================================================

// HardwareState tracks system resources for Waria's scheduling decisions
type HardwareState struct {
	CPUCores      int          `json:"cpu_cores"`
	CPUUsage      float64      `json:"cpu_usage_percent"`
	MemoryTotal   uint64       `json:"memory_total_mb"`
	MemoryUsed    uint64       `json:"memory_used_mb"`
	MemoryPercent float64      `json:"memory_percent"`
	GPUs          []GPUInfo    `json:"gpus"`
	Timestamp     time.Time    `json:"timestamp"`
	mu            sync.RWMutex `json:"-"`
}

// GPUInfo represents a single GPU's state
type GPUInfo struct {
	ID            int     `json:"id"`
	Name          string  `json:"name"`
	MemoryTotal   uint64  `json:"memory_total_mb"`
	MemoryUsed    uint64  `json:"memory_used_mb"`
	MemoryPercent float64 `json:"memory_percent"`
	Utilization   float64 `json:"utilization_percent"`
	Temperature   int     `json:"temperature_c"`
	Available     bool    `json:"available"`
}

// HardwareMonitor continuously tracks system resources
type HardwareMonitor struct {
	state      *HardwareState
	updateChan chan *HardwareState
	stopChan   chan bool
}

// NewHardwareMonitor creates the hardware monitoring system
func NewHardwareMonitor() *HardwareMonitor {
	hm := &HardwareMonitor{
		state: &HardwareState{
			CPUCores: runtime.NumCPU(),
			GPUs:     []GPUInfo{},
		},
		updateChan: make(chan *HardwareState, 10),
		stopChan:   make(chan bool),
	}

	// Initial scan
	hm.scanHardware()

	// Start background monitoring
	go hm.monitor()

	return hm
}

// monitor runs periodic hardware scans
func (hm *HardwareMonitor) monitor() {
	ticker := time.NewTicker(5 * time.Second)
	defer ticker.Stop()

	for {
		select {
		case <-ticker.C:
			hm.scanHardware()
			hm.updateChan <- hm.GetState()
		case <-hm.stopChan:
			log.Println("Hardware monitor stopped")
			return
		}
	}
}

// scanHardware performs a full system scan
func (hm *HardwareMonitor) scanHardware() {
	hm.state.mu.Lock()
	defer hm.state.mu.Unlock()

	hm.state.Timestamp = time.Now()

	// CPU Usage
	hm.state.CPUUsage = getCPUUsage()

	// Memory Usage
	memTotal, memUsed, memPercent := getMemoryUsage()
	hm.state.MemoryTotal = memTotal
	hm.state.MemoryUsed = memUsed
	hm.state.MemoryPercent = memPercent

	// GPU Detection (NVIDIA only for now)
	hm.state.GPUs = detectGPUs()
}

// GetState returns the current hardware state
func (hm *HardwareMonitor) GetState() *HardwareState {
	hm.state.mu.RLock()
	defer hm.state.mu.RUnlock()

	// Deep copy
	stateCopy := &HardwareState{
		CPUCores:      hm.state.CPUCores,
		CPUUsage:      hm.state.CPUUsage,
		MemoryTotal:   hm.state.MemoryTotal,
		MemoryUsed:    hm.state.MemoryUsed,
		MemoryPercent: hm.state.MemoryPercent,
		GPUs:          make([]GPUInfo, len(hm.state.GPUs)),
		Timestamp:     hm.state.Timestamp,
	}
	copy(stateCopy.GPUs, hm.state.GPUs)

	return stateCopy
}

// FindAvailableGPU returns the GPU with the most free memory
func (hm *HardwareMonitor) FindAvailableGPU(minMemoryMB uint64) (int, error) {
	hm.state.mu.RLock()
	defer hm.state.mu.RUnlock()

	bestGPU := -1
	maxFreeMemory := uint64(0)

	for _, gpu := range hm.state.GPUs {
		freeMemory := gpu.MemoryTotal - gpu.MemoryUsed
		if freeMemory >= minMemoryMB && freeMemory > maxFreeMemory {
			bestGPU = gpu.ID
			maxFreeMemory = freeMemory
		}
	}

	if bestGPU == -1 {
		return -1, fmt.Errorf("no GPU with %d MB free found", minMemoryMB)
	}

	return bestGPU, nil
}

// Stop terminates the hardware monitor
func (hm *HardwareMonitor) Stop() {
	hm.stopChan <- true
}

// =============================================================================
// HARDWARE DETECTION HELPERS
// =============================================================================

// getCPUUsage reads from /proc/stat (Linux-only)
func getCPUUsage() float64 {
	// Read /proc/stat for CPU usage
	data, err := ioutil.ReadFile("/proc/stat")
	if err != nil {
		return 0.0
	}

	lines := strings.Split(string(data), "\n")
	if len(lines) == 0 {
		return 0.0
	}

	// Parse first line (aggregate CPU)
	fields := strings.Fields(lines[0])
	if len(fields) < 8 || fields[0] != "cpu" {
		return 0.0
	}

	// Calculate usage (simplified)
	// cpu user nice system idle iowait irq softirq steal
	var total, idle uint64
	for i := 1; i < len(fields); i++ {
		val, _ := strconv.ParseUint(fields[i], 10, 64)
		total += val
		if i == 4 { // idle is field 4
			idle = val
		}
	}

	if total == 0 {
		return 0.0
	}

	usage := 100.0 * float64(total-idle) / float64(total)
	return usage
}

// getMemoryUsage reads from /proc/meminfo (Linux-only)
func getMemoryUsage() (total, used uint64, percent float64) {
	data, err := ioutil.ReadFile("/proc/meminfo")
	if err != nil {
		return 0, 0, 0.0
	}

	lines := strings.Split(string(data), "\n")
	memTotal := uint64(0)
	memAvailable := uint64(0)

	for _, line := range lines {
		fields := strings.Fields(line)
		if len(fields) < 2 {
			continue
		}

		if fields[0] == "MemTotal:" {
			memTotal, _ = strconv.ParseUint(fields[1], 10, 64)
		} else if fields[0] == "MemAvailable:" {
			memAvailable, _ = strconv.ParseUint(fields[1], 10, 64)
		}
	}

	// Convert KB to MB
	total = memTotal / 1024
	used = (memTotal - memAvailable) / 1024

	if total > 0 {
		percent = 100.0 * float64(used) / float64(total)
	}

	return total, used, percent
}

// detectGPUs uses nvidia-smi to detect NVIDIA GPUs
func detectGPUs() []GPUInfo {
	gpus := []GPUInfo{}

	// Check if nvidia-smi exists
	cmd := exec.Command("nvidia-smi", "--query-gpu=index,name,memory.total,memory.used,utilization.gpu,temperature.gpu", "--format=csv,noheader,nounits")
	output, err := cmd.Output()
	if err != nil {
		// No NVIDIA GPUs or nvidia-smi not installed
		return gpus
	}

	lines := strings.Split(strings.TrimSpace(string(output)), "\n")
	for _, line := range lines {
		fields := strings.Split(line, ",")
		if len(fields) < 6 {
			continue
		}

		id, _ := strconv.Atoi(strings.TrimSpace(fields[0]))
		name := strings.TrimSpace(fields[1])
		memTotal, _ := strconv.ParseUint(strings.TrimSpace(fields[2]), 10, 64)
		memUsed, _ := strconv.ParseUint(strings.TrimSpace(fields[3]), 10, 64)
		util, _ := strconv.ParseFloat(strings.TrimSpace(fields[4]), 64)
		temp, _ := strconv.Atoi(strings.TrimSpace(fields[5]))

		memPercent := 0.0
		if memTotal > 0 {
			memPercent = 100.0 * float64(memUsed) / float64(memTotal)
		}

		gpu := GPUInfo{
			ID:            id,
			Name:          name,
			MemoryTotal:   memTotal,
			MemoryUsed:    memUsed,
			MemoryPercent: memPercent,
			Utilization:   util,
			Temperature:   temp,
			Available:     memPercent < 90.0, // Consider available if < 90% used
		}
		gpus = append(gpus, gpu)
	}

	return gpus
}

// =============================================================================
// HTTP HANDLERS
// =============================================================================

// ServeHTTP handles /api/system/health requests
func (hm *HardwareMonitor) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")

	state := hm.GetState()
	json.NewEncoder(w).Encode(state)
}
