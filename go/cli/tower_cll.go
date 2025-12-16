package main

import (
	"fmt"
	"net/http"
	"os"
	"strings"
	"time"

	"github.com/charmbracelet/bubbles/table"
	"github.com/charmbracelet/bubbles/viewport"
	tea "github.com/charmbracelet/bubbletea"
	"github.com/charmbracelet/lipgloss"
	"github.com/gorilla/websocket"
)

// NOTE: In a true multi-package Go project, the following types would be
// imported from a 'kirktower/types' package to avoid duplication with 'types.go'.
// For this single-file execution context, they must remain here, but should be
// tagged with an explanatory comment.

// =============================================================================
// DATA STRUCTURES (Mirroring types.go for CLI build)
// =============================================================================

type SystemState struct {
	ActiveProcesses int                      `json:"active_processes"`
	TotalProcesses  int                      `json:"total_processes"`
	TotalVRAM       float64                  `json:"total_vram"`
	TotalTokens     int                      `json:"total_tokens"`
	Processes       map[string]*ProcessState `json:"processes"`
	Waria           *WariaState              `json:"waria"`
}

type ProcessState struct {
	ID         string    `json:"id"`
	Agent      string    `json:"agent"`
	Phase      string    `json:"phase"`
	Status     string    `json:"status"`
	StartTime  time.Time `json:"start_time"`
	GPU        int       `json:"gpu"`
	VRAMUsage  float64   `json:"vram_usage"`
	TokenCount int       `json:"token_count"`
	LastOutput string    `json:"last_output"`
}

type WariaState struct {
	PromptLength      int              `json:"prompt_length"`
	ContextReuse      int              `json:"context_reuse"`
	CrossPhaseRefs    int              `json:"cross_phase_refs"`
	ConfidencePlateau bool             `json:"confidence_plateau"`
	VerbosityIncrease bool             `json:"verbosity_increase"`
	Thresholds        []WariaThreshold `json:"thresholds"`
	TipPackets        []string         `json:"tip_packets"`
}

type WariaThreshold struct {
	Name      string  `json:"name"`
	Current   float64 `json:"current"`
	Threshold float64 `json:"threshold"`
	Breached  bool    `json:"breached"`
}

// =============================================================================
// STYLES AND MODEL
// =============================================================================

// Styles
var (
	titleStyle = lipgloss.NewStyle().
			Bold(true).
			Foreground(lipgloss.Color("#00FF00")).
			Background(lipgloss.Color("#1a1a1a")).
			Padding(0, 1)

	activeStyle = lipgloss.NewStyle().
			Foreground(lipgloss.Color("#00FF00"))

	pausedStyle = lipgloss.NewStyle().
			Foreground(lipgloss.Color("#FFAA00"))

	killedStyle = lipgloss.NewStyle().
			Foreground(lipgloss.Color("#FF0000"))

	warningStyle = lipgloss.NewStyle().
			Bold(true).
			Foreground(lipgloss.Color("#FF4444")).
			Background(lipgloss.Color("#2a1a1a"))

	panelStyle = lipgloss.NewStyle().
			Border(lipgloss.RoundedBorder()).
			BorderForeground(lipgloss.Color("#444444")).
			Padding(1, 2)
)

type model struct {
	ws            *websocket.Conn
	state         SystemState
	processTable  table.Model
	wariaViewport viewport.Model
	selectedPanel int // 0: processes, 1: waria
	width         int
	height        int
	err           error
	// Service endpoints and statuses
	wsURL     string
	mcpURL    string
	memoryURL string
	wsOK      bool
	mcpOK     bool
	memoryOK  bool
}

type stateMsg SystemState
type errMsg error
type statusMsg struct {
	WS     bool
	MCP    bool
	Memory bool
}

// pollStatusCmd checks service endpoints and returns a statusMsg; reissued by Update.
func pollStatusCmd(wsURL, mcpURL, memoryURL string, haveWS bool) tea.Cmd {
	return func() tea.Msg {
		wsOK := false
		if haveWS {
			wsOK = true
		} else {
			// Try dialing briefly
			if _, _, err := websocket.DefaultDialer.Dial(wsURL, nil); err == nil {
				wsOK = true
			}
		}

		mcpOK := false
		if resp, err := http.Get(mcpURL + "/api/state"); err == nil {
			mcpOK = true
			resp.Body.Close()
		}

		memoryOK := false
		if resp, err := http.Get(memoryURL); err == nil {
			memoryOK = true
			resp.Body.Close()
		}

		time.Sleep(1500 * time.Millisecond)
		return statusMsg{WS: wsOK, MCP: mcpOK, Memory: memoryOK}
	}
}

// =============================================================================
// BUBBLETEA LIFE CYCLE
// =============================================================================

func initialModel() model {
	// Read endpoints from env with sensible defaults
	wsURL := os.Getenv("KIRKTOWER_WS")
	if wsURL == "" {
		wsURL = "ws://localhost:8080/ws"
	}
	mcpURL := os.Getenv("KIRKTOWER_HTTP")
	if mcpURL == "" {
		mcpURL = "http://localhost:8080"
	}
	memoryURL := os.Getenv("DIPLO_MEMORY_HTTP")
	if memoryURL == "" {
		memoryURL = "http://localhost:8081"
	}

	// Try to establish a WebSocket, but do not fail hard if it isn't available yet.
	var ws *websocket.Conn
	wsOK := false
	if conn, _, err := websocket.DefaultDialer.Dial(wsURL, nil); err == nil {
		ws = conn
		wsOK = true
	}

	columns := []table.Column{
		{Title: "ID", Width: 8}, // ADDED: Process ID for unique reference
		{Title: "Agent", Width: 12},
		{Title: "Phase", Width: 12},
		{Title: "Status", Width: 10},
		{Title: "GPU", Width: 5},
		{Title: "VRAM", Width: 8},
		{Title: "Tokens", Width: 10},
		{Title: "Runtime", Width: 10},
	}

	t := table.New(
		table.WithColumns(columns),
		table.WithFocused(true),
		table.WithHeight(10),
	)

	s := table.DefaultStyles()
	s.Header = s.Header.
		BorderStyle(lipgloss.NormalBorder()).
		BorderForeground(lipgloss.Color("240")).
		BorderBottom(true).
		Bold(false)
	s.Selected = s.Selected.
		Foreground(lipgloss.Color("229")).
		Background(lipgloss.Color("57")).
		Bold(false)
	t.SetStyles(s)

	vp := viewport.New(80, 10)

	m := model{
		ws:            ws,
		processTable:  t,
		wariaViewport: vp,
		selectedPanel: 0,
		wsURL:         wsURL,
		mcpURL:        mcpURL,
		memoryURL:     memoryURL,
		wsOK:          wsOK,
	}

	return m
}

func (m model) Init() tea.Cmd {
	if m.err != nil {
		return tea.Quit // Quit immediately if connection failed
	}
	// Start WS listener if we have a connection, and start periodic status polling
	cmds := []tea.Cmd{tea.EnterAltScreen}
	if m.ws != nil {
		cmds = append(cmds, listenForStateUpdates(m.ws))
	}
	cmds = append(cmds, pollStatusCmd(m.wsURL, m.mcpURL, m.memoryURL, m.ws != nil))
	return tea.Batch(cmds...)
}

func listenForStateUpdates(ws *websocket.Conn) tea.Cmd {
	return func() tea.Msg {
		var state SystemState
		err := ws.ReadJSON(&state)
		if err != nil {
			// Do not return errMsg here, let the main loop handle the ws closure error
			if websocket.IsUnexpectedCloseError(err) {
				return errMsg(fmt.Errorf("Kirktower connection lost: %w", err))
			}
			// Restart listener for next message if error is temporary/non-fatal
			return listenForStateUpdates(ws)()
		}
		return stateMsg(state)
	}
}

func (m model) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
	var cmd tea.Cmd

	switch msg := msg.(type) {
	case tea.KeyMsg:
		switch msg.String() {
		case "ctrl+c", "q":
			if m.ws != nil {
				m.ws.Close()
			}
			return m, tea.Quit

		case "tab":
			m.selectedPanel = (m.selectedPanel + 1) % 2
			if m.selectedPanel == 0 {
				m.processTable.Focus()
			} else {
				m.processTable.Blur()
			}

		case "up", "k":
			if m.selectedPanel == 0 {
				m.processTable, cmd = m.processTable.Update(msg)
			} else {
				m.wariaViewport, cmd = m.wariaViewport.Update(msg)
			}

		case "down", "j":
			if m.selectedPanel == 0 {
				m.processTable, cmd = m.processTable.Update(msg)
			} else {
				m.wariaViewport, cmd = m.wariaViewport.Update(msg)
			}

		case "p":
			if m.selectedPanel == 0 {
				m.sendCommand("pause")
			}
		case "r":
			if m.selectedPanel == 0 {
				m.sendCommand("resume")
			}
		case "x":
			if m.selectedPanel == 0 {
				m.sendCommand("kill")
			}
		case "K":
			if m.selectedPanel == 0 {
				m.sendCommand("kill_loop")
			}
		}

	case stateMsg:
		m.state = SystemState(msg)
		m.updateProcessTable()
		m.updateWariaView()
		// CRITICAL: Re-queue the listener to wait for the NEXT state update
		// continue polling status as well
		return m, tea.Batch(listenForStateUpdates(m.ws), pollStatusCmd(m.wsURL, m.mcpURL, m.memoryURL, m.ws != nil))

	case errMsg:
		m.err = msg
		if m.ws != nil {
			m.ws.Close()
		}
		return m, tea.Quit

	case tea.WindowSizeMsg:
		m.width = msg.Width
		m.height = msg.Height
		m.processTable.SetWidth(msg.Width - 4)
		m.wariaViewport.Width = msg.Width - 4

		// Update table height based on window size to prevent overflow
		tableHeight := m.height - 18 // Estimate space needed for header, stats, waria, and controls
		if tableHeight < 3 {
			tableHeight = 3
		}
		m.processTable.SetHeight(tableHeight)

		return m, nil
	}

	// Handle periodic status updates
	switch s := msg.(type) {
	case statusMsg:
		m.wsOK = s.WS
		m.mcpOK = s.MCP
		m.memoryOK = s.Memory

		// If WS became available and we don't have a persistent connection, try to connect now
		if m.ws == nil && m.wsOK {
			if conn, _, err := websocket.DefaultDialer.Dial(m.wsURL, nil); err == nil {
				m.ws = conn
				// start listening for state updates
				return m, tea.Batch(listenForStateUpdates(m.ws), pollStatusCmd(m.wsURL, m.mcpURL, m.memoryURL, true))
			}
		}

		// Continue polling
		return m, pollStatusCmd(m.wsURL, m.mcpURL, m.memoryURL, m.ws != nil)
	}

	return m, cmd
}

func (m *model) updateProcessTable() {
	var rows []table.Row

	// Sort processes by start time (or other useful metric)
	// For simplicity, we iterate over the map keys to get a deterministic sort
	var processIDs []string
	for id := range m.state.Processes {
		processIDs = append(processIDs, id)
	}
	// NOTE: Real implementation should sort by a meaningful metric like StartTime

	for _, id := range processIDs {
		ps := m.state.Processes[id]
		runtime := time.Since(ps.StartTime).Round(time.Second).String()

		status := ps.Status
		switch ps.Status {
		case "running":
			status = activeStyle.Render("●") + " running"
		case "paused":
			status = pausedStyle.Render("‖") + " paused"
		case "killed":
			status = killedStyle.Render("✕") + " killed"
		}

		rows = append(rows, table.Row{
			ps.ID[:6], // Use a truncated unique ID
			ps.Agent,
			ps.Phase,
			status,
			fmt.Sprintf("%d", ps.GPU),
			fmt.Sprintf("%.2fGB", ps.VRAMUsage),
			fmt.Sprintf("%d", ps.TokenCount),
			runtime,
		})
	}

	m.processTable.SetRows(rows)
}

func (m *model) updateWariaView() {
	if m.state.Waria == nil {
		return
	}

	var content strings.Builder

	content.WriteString(titleStyle.Render("WARIA - REASONING HORIZON SENTINEL"))
	content.WriteString("\n\n")

	// Thresholds
	content.WriteString("Thresholds:\n")
	for _, t := range m.state.Waria.Thresholds {
		status := "OK"
		style := lipgloss.NewStyle().Foreground(lipgloss.Color("#00FF00"))

		if t.Breached {
			status = "BREACH"
			style = warningStyle
		}

		pct := 0.0
		if t.Threshold > 0 {
			pct = (t.Current / t.Threshold) * 100
		} else {
			// Handle zero threshold for binary states (e.g., must be 0)
			if t.Current > 0 {
				status = "BREACH"
				style = warningStyle
			}
		}

		content.WriteString(fmt.Sprintf("  %s: %.2f/%.2f (%.0f%%) %s\n",
			t.Name,
			t.Current,
			t.Threshold,
			pct,
			style.Render(status)))
	}

	// Flags
	content.WriteString("\nFlags:\n")
	content.WriteString(fmt.Sprintf("  Confidence Plateau: %v\n", m.state.Waria.ConfidencePlateau))
	content.WriteString(fmt.Sprintf("  Verbosity Increase: %v\n", m.state.Waria.VerbosityIncrease))
	content.WriteString(fmt.Sprintf("  Cross-Phase Refs: %d\n", m.state.Waria.CrossPhaseRefs))

	// Tip Packets
	if len(m.state.Waria.TipPackets) > 0 {
		content.WriteString("\n")
		content.WriteString(warningStyle.Render("⚠ ACTIVE TIPS:"))
		content.WriteString("\n\n")

		// Show all tips, wrapping them in the panel style for clarity
		tipContent := strings.Join(m.state.Waria.TipPackets, "\n---\n")
		content.WriteString(panelStyle.Width(m.wariaViewport.Width - 4).Render(tipContent))
		content.WriteString("\n")
	}

	m.wariaViewport.SetContent(content.String())
}

func (m *model) sendCommand(action string) {
	row := m.processTable.SelectedRow()
	if row == nil || len(row) == 0 {
		return
	}

	// The process ID (truncated) is in the first column now
	selectedIDPrefix := row[0]

	// Find the full process ID by matching the prefix
	var processID string
	var phase string
	for id, ps := range m.state.Processes {
		if strings.HasPrefix(id, selectedIDPrefix) {
			processID = id
			phase = ps.Phase
			break
		}
	}

	if processID == "" {
		// Cannot find the process, fail silently
		return
	}

	var cmd map[string]interface{}

	switch action {
	case "pause", "resume", "kill":
		cmd = map[string]interface{}{
			"action": action,
			"id":     processID, // Use the full, unique ID
		}
	case "kill_loop":
		// This command targets the entire phase, not just one process
		cmd = map[string]interface{}{
			"action": action,
			"loop":   phase,
		}
	}

	if cmd != nil && m.ws != nil {
		m.ws.WriteJSON(cmd)
	}
}

func (m model) View() string {
	if m.err != nil {
		// Use the error view if connection failed on Init or during Update
		return fmt.Sprintf("CRITICAL ERROR: Kirktower Control Tower Failure\n\n%v\n\nPress 'Q' to quit.\n", warningStyle.Render(m.err.Error()))
	}

	// Header
	header := titleStyle.Render("╔═══════════════════════════════════════════════════════════╗")
	header += "\n"
	header += titleStyle.Render("║  KIRKTOWER - JOSIEDESK PROCESS CONTROL TOWER             ║")
	header += "\n"
	header += titleStyle.Render("╚═══════════════════════════════════════════════════════════╝")

	// System stats
	// Service status indicators
	wsStatus := lipgloss.NewStyle().Foreground(lipgloss.Color("#FF4444")).Render("✖ WS")
	if m.wsOK {
		wsStatus = lipgloss.NewStyle().Foreground(lipgloss.Color("#00FF00")).Render("● WS")
	}
	mcpStatus := lipgloss.NewStyle().Foreground(lipgloss.Color("#FF4444")).Render("✖ MCP")
	if m.mcpOK {
		mcpStatus = lipgloss.NewStyle().Foreground(lipgloss.Color("#00FF00")).Render("● MCP")
	}
	memStatus := lipgloss.NewStyle().Foreground(lipgloss.Color("#FF4444")).Render("✖ MEM")
	if m.memoryOK {
		memStatus = lipgloss.NewStyle().Foreground(lipgloss.Color("#00FF00")).Render("● MEM")
	}

	stats := fmt.Sprintf(
		"Active: %d/%d | VRAM: %.2f GB | Tokens: %d | %s %s %s | Time: %s",
		m.state.ActiveProcesses,
		m.state.TotalProcesses,
		m.state.TotalVRAM,
		m.state.TotalTokens,
		wsStatus,
		mcpStatus,
		memStatus,
		time.Now().Format("15:04:05 MST"),
	)

	// Process panel
	processPanel := panelStyle.Width(m.width - 4).Render(m.processTable.View())

	// Waria panel
	wariaPanel := panelStyle.Width(m.width - 4).Render(m.wariaViewport.View())

	// Controls
	controls := lipgloss.NewStyle().
		Foreground(lipgloss.Color("#666666")).
		Render("TAB: switch panels | ↑↓: navigate | P: pause | R: resume | X: kill process | K: kill loop | Q: quit")

	// Layout
	content := lipgloss.JoinVertical(
		lipgloss.Left,
		header,
		"\n"+stats+"\n",
		processPanel,
		"\n",
		wariaPanel,
		"\n"+controls,
	)

	return content
}

func main() {
	// Added check to prevent compilation/execution when types are not fully linked.
	if len(os.Args) > 1 && os.Args[1] == "stub" {
		fmt.Println("Kirktower CLI Stub. Run 'go run kirktower.go tower_cli.go' or build 'tower_cli'.")
		return
	}

	if len(os.Getenv("DEBUG")) > 0 {
		f, err := tea.LogToFile("debug.log", "debug")
		if err != nil {
			fmt.Println("fatal:", err)
			os.Exit(1)
		}
		defer f.Close()
	}

	p := tea.NewProgram(initialModel(), tea.WithAltScreen())
	if _, err := p.Run(); err != nil {
		fmt.Printf("Error running TUI: %v\n", err)
		os.Exit(1)
	}
}
