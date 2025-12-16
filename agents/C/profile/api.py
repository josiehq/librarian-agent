"""
Agent profile API template

Place per-agent LLM config and profile code here.  Copy/modify per agent.
"""

import os


def get_llm_config():
    """Return a dict with LLM configuration for this agent.

    Use environment variables to inject secrets in deployment.
    """
    return {
        "model": os.getenv("AGENT_MODEL", "gpt-4"),
        "api_key": os.getenv("AGENT_API_KEY", "sk-placeholder"),
        "temperature": float(os.getenv("AGENT_TEMPERATURE", "0.4")),
        "timeout": int(os.getenv("AGENT_TIMEOUT", "120")),
        "notes": "Edit this template in agents/<class>/profile/api.py"
    }
