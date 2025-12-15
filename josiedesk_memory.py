"""
josiedesk_memory.py - The Swarm's Long-Term Memory
Managed by Diplo (D2). Powered by LlamaIndex.
"""

import os
import json
from datetime import datetime
from typing import List, Dict, Optional

# LlamaIndex Imports
from llama_index.core import Document, VectorStoreIndex, StorageContext, load_index_from_storage
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.query_engine import RetrieverQueryEngine

# Persistence Path
STORAGE_DIR = "./josiedesk/memory_store"

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
        if os.path.exists(STORAGE_DIR):
            try:
                storage_context = StorageContext.from_defaults(persist_dir=STORAGE_DIR)
                self.index = load_index_from_storage(storage_context)
            except Exception as e:
                print(f"[Diplo] Memory corruption detected, rebuilding: {e}")
                self.index = VectorStoreIndex([])
        else:
            self.index = VectorStoreIndex([])
            os.makedirs(STORAGE_DIR, exist_ok=True)

    def ingest_blueprint(self, blueprint: str, task_name: str):
        """
        Diplo ingests a finalized Roark Blueprint.
        This allows future agents to query "How did we structure the X project?"
        """
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
        Ingests runtime logs.
        Useful for searching "What error did Clash hit last time?"
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

    def query_memory(self, query_str: str) -> str:
        """
        Retrieves context. Used by Diplo to advise the C-Class loop.
        """
        if not self.index:
            return "Memory empty."

        retriever = VectorIndexRetriever(index=self.index, similarity_top_k=3)
        query_engine = RetrieverQueryEngine(retriever=retriever)
        response = query_engine.query(query_str)
        return str(response)

# Singleton Instance for the Swarm
diplo_memory = SwarmMemory()
