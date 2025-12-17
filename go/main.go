package main

import (
	"log"
	"net/http"

	"github.com/josiehq/librarian-agent/kernel"
)

func main() {
	log.Println("Starting Librarian Agent MCP Server...")

	// Initialize TowerControl (includes hardware monitor + agent queue)
	tower := kernel.NewTowerControl()

	// Initialize MCP Server
	server := kernel.NewMCPServer(tower)

	// Register HTTP handlers
	http.HandleFunc("/mcp", server.ServeHTTP)
	http.HandleFunc("/health", func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusOK)
		w.Write([]byte("OK"))
	})

	// Hardware monitoring endpoint (D3 Waria)
	http.Handle("/api/system/health", tower.GetHardwareMonitor())

	// Agent queue endpoints (D1 Diplo + D3 Waria)
	tower.GetAgentQueue().RegisterHandlers(http.DefaultServeMux)

	log.Println("[MCP SERVER] Listening on :8080")
	log.Println("[ENDPOINTS] /mcp (JSON-RPC 2.0), /health (Status)")
	log.Println("[ENDPOINTS] /api/system/health (Hardware Monitor)")
	log.Println("[ENDPOINTS] /api/queue/submit, /api/queue/status, /api/queue/list (Agent Queue)")

	if err := http.ListenAndServe(":8080", nil); err != nil {
		log.Fatalf("Server failed: %v", err)
	}
}
