package main

import (
	"fmt"
	"log"
	"os"
	"strings"
	"time"

	"github.com/charmbracelet/bubbles/table"
	"github.com/charmbracelet/bubbles/viewport"
	tea "github.com/charmbracelet/bubbletea"
	"github.com/charmbracelet/lipgloss"
	"github.com/gorilla/websocket"
)

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
	selectedRow   int
	width         int
	height        int
	err           error
}

type stateMsg SystemState
type errMsg error

func initialModel() model {
	// Connect to Kirktower WebSocket
	ws, _, err := websocket.DefaultDialer.Dial("ws://localhost:9090/ws", nil)
	if err != nil {
		log.Fatal("WebSocket connection failed:", err)
	}

	columns := []table.Column{
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
	}

	return m
}

func (m model) Init() tea.Cmd {
	return tea.Batch(
		listenForStateUpdates(m.ws),
		tea.EnterAltScreen,
	)
}

func listenForStateUpdates(ws *websocket.Conn) tea.Cmd {
	return func() tea.Msg {
		var state SystemState
		err := ws.ReadJSON(&state)
		if err != nil {
			return errMsg(err)
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
			m.ws.Close()
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
			// Pause selected process
			if m.selectedPanel == 0 {
				m.sendCommand("pause")
			}

		case "r":
			// Resume selected process
			if m.selectedPanel == 0 {
				m.sendCommand("resume")
			}

		case "x":
			// Kill selected process
			if m.selectedPanel == 0 {
				m.sendCommand("kill")
			}

		case "K":
			// Kill entire loop
			if m.selectedPanel == 0 {
				m.sendCommand("kill_loop")
			}
		}

	case stateMsg:
		m.state = SystemState(msg)
		m.updateProcessTable()
		m.updateWariaView()
		return m, listenForStateUpdates(m.ws)

	case errMsg:
		m.err = msg
		return m, tea.Quit

	case tea.WindowSizeMsg:
		m.width = msg.Width
		m.height = msg.Height
		m.processTable.SetWidth(msg.Width - 4)
		m.wariaViewport.Width = msg.Width - 4
		return m, nil
	}

	return m, cmd
}

func (m *model) updateProcessTable() {
	var rows []table.Row

	for _, ps := range m.state.Processes {
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

		pct := (t.Current / t.Threshold) * 100
		content.WriteString(fmt.Sprintf("  %s: %.0f/%.0f (%.0f%%) %s\n",
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

		for i, tip := range m.state.Waria.TipPackets {
			if i >= 3 { // Show last 3 tips only
				break
			}
			content.WriteString(panelStyle.Render(tip))
			content.WriteString("\n")
		}
	}

	m.wariaViewport.SetContent(content.String())
}

func (m *model) sendCommand(action string) {
	if len(m.processTable.Rows()) == 0 {
		return
	}

	row := m.processTable.SelectedRow()
	if row == nil {
		return
	}

	// Extract process ID from first column (agent name)
	// In real implementation, store ID separately
	agent := row[0]

	var cmd map[string]interface{}

	switch action {
	case "pause", "resume", "kill":
		// Find process ID
		for id, ps := range m.state.Processes {
			if ps.Agent == agent {
				cmd = map[string]interface{}{
					"action": action,
					"id":     id,
				}
				break
			}
		}
	case "kill_loop":
		phase := row[1]
		cmd = map[string]interface{}{
			"action": action,
			"loop":   phase,
		}
	}

	if cmd != nil {
		m.ws.WriteJSON(cmd)
	}
}

func (m model) View() string {
	if m.err != nil {
		return fmt.Sprintf("Error: %v\n", m.err)
	}

	// Header
	header := titleStyle.Render("╔═══════════════════════════════════════════════════════════╗")
	header += "\n"
	header += titleStyle.Render("║  KIRKTOWER - JOSIEDESK PROCESS CONTROL TOWER             ║")
	header += "\n"
	header += titleStyle.Render("╚═══════════════════════════════════════════════════════════╝")

	// System stats
	stats := fmt.Sprintf(
		"Active: %d/%d | VRAM: %.2f GB | Tokens: %d",
		m.state.ActiveProcesses,
		m.state.TotalProcesses,
		m.state.TotalVRAM,
		m.state.TotalTokens,
	)

	// Process panel
	processPanel := panelStyle.Render(m.processTable.View())

	// Waria panel
	wariaPanel := panelStyle.Render(m.wariaViewport.View())

	// Controls
	controls := lipgloss.NewStyle().
		Foreground(lipgloss.Color("#666666")).
		Render("TAB: switch panels | ↑↓: navigate | P: pause | R: resume | X: kill | K: kill loop | Q: quit")

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
		fmt.Printf("Error: %v", err)
		os.Exit(1)
	}
}
