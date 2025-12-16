"""
josiedesk_memory.py - The Swarm's Long-Term Memory
Managed by Diplo (D2). Powered by LlamaIndex and Flask (for MCP integration).
"""

import os
import json
from datetime import datetime
from typing import List, Dict, Optional

# --- Dependency Imports ---
# NOTE: Ensure 'flask' is added to setup.py's install_requires
from flask import Flask, request, jsonify 

# LlamaIndex Imports
from llama_index.core import Document, VectorStoreIndex, StorageContext, load_index_from_storage
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.query_engine import RetrieverQueryEngine

# --- Persistence Configuration ---
# Must be mounted to a persistent volume in the VPS deployment
STORAGE_DIR = "./josiedesk/memory_store" 

# =============================================================================
# 1. SWARM MEMORY CLASS (The Persistence Logic)
# =============================================================================

class SwarmMemory:
    """
    The LlamaIndex wrapper.
    Stores Blueprints (A-Class output) and Execution Logs (C-Class output).
    """
    def __init__(self):
        self.index = None
        self._initialize_index()

    def _initialize_index(self):
        """Loads existing vector store or creates a new one."""
        if os.path.exists(STORAGE_DIR) and len(os.listdir(STORAGE_DIR)) > 0:
            try:
                # Attempt to load existing index from persistent storage
                storage_context = StorageContext.from_defaults(persist_dir=STORAGE_DIR)
                self.index = load_index_from_storage(storage_context)
                print(f"[Diplo] Swarm Memory loaded from {STORAGE_DIR}.")
            except Exception as e:
                # Corruption or incompatibility detected
                print(f"[Diplo] CRITICAL: Memory corruption detected, rebuilding: {e}")
                self.index = VectorStoreIndex([])
                os.makedirs(STORAGE_DIR, exist_ok=True)
        else:
            # First run
            self.index = VectorStoreIndex([])
            os.makedirs(STORAGE_DIR, exist_ok=True)
            print(f"[Diplo] New Swarm Memory initialized at {STORAGE_DIR}.")


    def ingest_blueprint(self, blueprint: str, task_name: str):
        """Diplo ingests a finalized Roark Blueprint."""
        doc = Document(
            text=blueprint,
            metadata={
                "type": "blueprint",
                "task": task_name,
                "timestamp": datetime.now().isoformat(),
                "author": "Roark"
            }
        )
        self.index.insert(doc)
        self.index.storage_context.persist(persist_dir=STORAGE_DIR)
        print(f"[Diplo] Blueprint for '{task_name}' cached in Vector Store.")

    def ingest_log(self, agent: str, phase: str, content: str):
        """
        Inferred from the MCP call (Kirktower).
        Ingests runtime logs and context for low-energy recall.
        """
        doc = Document(
            text=content,
            metadata={
                "type": "execution_log",
                "agent": agent,
                "phase": phase,
                "timestamp": datetime.now().isoformat()
            }
        )
        self.index.insert(doc)
        # NOTE: Persist is a disk IO operation. We only persist on major events or periodic sync.
        # For simplicity, we persist after every log, but optimization is a future step.
        self.index.storage_context.persist(persist_dir=STORAGE_DIR) 
        print(f"[Diplo] Log indexed for {agent} in phase {phase}. Memory synced.")


    def query_memory(self, query_str: str) -> str:
        """Retrieves context. Used by Diplo to advise the C-Class loop."""
        if not self.index:
            return "Memory empty."

        retriever = VectorIndexRetriever(index=self.index, similarity_top_k=3)
        query_engine = RetrieverQueryEngine(retriever=retriever)
        response = query_engine.query(query_str)
        return str(response)

# Singleton Instance for the Swarm (Must be defined after the class)
diplo_memory = SwarmMemory()


# =============================================================================
# 2. FLASK SERVICE (The External HTTP Dependency for MCP)
# =============================================================================

app = Flask("DiploMemoryService")

@app.route('/ingest_log', methods=['POST'])
def ingest_log_endpoint():
    """
    Endpoint hit by the Go Kirktower Kernel's 'memory_commit' tool.
    This routes the data to the SwarmMemory persistence logic.
    """
    try:
        data = request.get_json()
        agent = data.get('agent')
        phase = data.get('phase')
        content = data.get('content')
        
        if not all([agent, phase, content]):
            return jsonify({"status": "error", "message": "Missing required fields (agent, phase, content)"}), 400

        # Pass the data to the core persistence logic (diplo_memory instance)
        diplo_memory.ingest_log(agent, phase, content)

        # Success message reported back to the Kirktower Kernel
        return jsonify({"status": "success", "message": "Log ingested and indexed."}), 200
        
    except Exception as e:
        # CRITICAL: Report LlamaIndex/disk errors back to Kirktower for audit
        print(f"[Diplo ERROR] Indexing failure: {e}")
        return jsonify({"status": "error", "message": f"Memory Indexing Failure: {str(e)}"}), 500


def start_memory_service():
    """
    The dedicated runner function called by the Diplo (D2) agent process.
    """
    print("\n[Diplo] Starting Swarm Memory Service on http://127.0.0.1:8081...")
    # host='127.0.0.1' ensures ONLY the local Kirktower Kernel can access the endpoint.
    app.run(host='127.0.0.1', port=8081, threaded=True)

# The main execution block
if __name__ == '__main__':
    start_memory_service()