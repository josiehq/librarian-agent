"""
Athena (A3) - GUI Agent Profile
The visual interface and command center for the Librarian Agent swarm.

Athena serves as the unified interface for all 12 agents in the workflow,
providing visual orchestration, real-time monitoring, and advanced RAG logic.
"""

import os


AGENT_PROFILE = {
    "name": "Athena",
    "class": "A",
    "rank": "A3",
    "role": "GUI/UI Command Center",
    "description": "Custom OpenUI-based interface for 12-agent workflow management",
    "phase": 4,
    "capabilities": [
        "Visual agent orchestration",
        "Real-time swarm status monitoring",
        "User interaction interface",
        "Advanced RAG logic implementation",
        "Multi-agent coordination dashboard"
    ],
    "dependencies": [
        "All A, B, C, D class agents",
        "Custom OpenUI fork",
        "C2 server infrastructure"
    ],
    "status": "planned"
}


def get_llm_config():
    """Return a dict with LLM configuration for Athena (A3).

    Athena coordinates the entire swarm, so it requires robust configuration.
    """
    return {
        "model": os.getenv("ATHENA_MODEL", "gpt-4"),
        "api_key": os.getenv("ATHENA_API_KEY", "sk-placeholder"),
        "temperature": float(os.getenv("ATHENA_TEMPERATURE", "0.3")),
        "timeout": int(os.getenv("ATHENA_TIMEOUT", "180")),
        "max_tokens": int(os.getenv("ATHENA_MAX_TOKENS", "4096")),
        "notes": "Athena (A3) - GUI Agent for swarm coordination"
    }
