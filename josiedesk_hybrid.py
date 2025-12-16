"""
JosieDesk Hybrid Runtime (The Final Architecture)
Integrates AutoGen (Consensus) with the Kirktower MCP Kernel (Execution/Tooling).

This file contains the Swarm's System Call Interface and Agent Definitions.
"""

import os
import json
import asyncio
import httpx # Required for making async HTTP calls
from pathlib import Path
from typing import Dict, List, Any, Optional

# Placeholder imports for frameworks - in production, install pyautogen and llama-index
try:
    import autogen
    from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager
except ImportError:
    print("CRITICAL: Install pyautogen: pip install pyautogen")
    exit(1)

# Import Diplo's memory service for the query tool
try:
    from josiedesk_memory import diplo_memory
except ImportError:
    print("CRITICAL: Could not import diplo_memory. Ensure josiedesk_memory.py is configured.")
    # Define a mock for testing if memory service isn't set up yet
    class MockMemory:
        def query_memory(self, query): return f"MOCK MEMORY: {query}"
    diplo_memory = MockMemory()


# ==============================================================================
# 1. THE SYSTEM CALL INTERFACE (MCP Client)
# ==============================================================================

# Kirktower is expected to run on the local host on port 8080
KIRKTOWER_MCP_URL = "http://localhost:8080/api/mcp"

async def call_mcp_tool(tool_name: str, agent_id: str = "hybrid_agent", **kwargs) -> str:
    """
    The Swarm's System Call Interface.
    Translates an agent's tool request into an audited JSON-RPC call to the Kirktower Kernel.
    Supports Python format: {name, arguments, agent_id}
    """
    
    # 1. Construct JSON-RPC Payload (Python format)
    request_id = os.urandom(8).hex() 
    payload = {
        "jsonrpc": "2.0",
        "method": tool_name,  # Direct tool name
        "params": {
            "name": tool_name,
            "arguments": kwargs,
            "agent_id": agent_id
        },
        "id": request_id
    }
    
    print(f"\n[MCP Call] Agent requesting {tool_name} from Kirktower...")
    
    try:
        # 2. Execute the HTTP Call
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(KIRKTOWER_MCP_URL, json=payload)

        # 3. Handle Errors and Responses
        response.raise_for_status() # Raises exception for 4xx/5xx HTTP errors
        mcp_response = response.json()

        if 'error' in mcp_response:
            error = mcp_response['error']
            # This is the Waria Gate rejecting the call
            return f"[MCP ERROR] Kirktower Rejected Tool Call: {error.get('message', 'Unknown MCP Error')}"
        
        # Success
        result = mcp_response.get('result')
        return f"[MCP SUCCESS - {tool_name}] Output: {result}"

    except httpx.HTTPStatusError as e:
        return f"[MCP CRITICAL FAILURE] HTTP Error {e.response.status_code}: Kirktower is unreachable or misconfigured. Check logs."
    except Exception as e:
        return f"[MCP CRITICAL FAILURE] Network Error: Could not connect to Kirktower on 8080. Is it running? Error: {e}"


# ==============================================================================
# 2. LOCAL RUNTIME & MOCK TOOLS (File I/O Only)
# ==============================================================================

class LocalRuntime:
    """
    Handles local file operations in the EPHEMERAL workspace.
    Execution and advanced tools (Semgrep/Trivy) are handled by the MCP Kernel.
    """
    def __init__(self, workspace_root: str = "./workspace"):
        self.root = Path(workspace_root)
        self.root.mkdir(exist_ok=True)

    def write_file(self, filepath: str, content: str) -> str:
        """Clash and Bash use this to create artifacts."""
        try:
            full_path = self.root / filepath
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content)
            return f"Success: Wrote {len(content)} bytes to {filepath}"
        except Exception as e:
            return f"Error writing file: {e}"

    def list_tree(self, subdir: str = "") -> str:
        """Gunash uses this to check directory topology."""
        path = self.root / subdir
        if not path.exists():
            return "Directory not found"
        return "\n".join([str(p.relative_to(self.root)) for p in path.rglob("*")])

runtime = LocalRuntime()

# --- Local Mock Tools (Non-Kernel) ---

def tool_write_code(filepath: str, content: str) -> str:
    """Clash and Bash use this to create artifacts in the ephemeral workspace."""
    return runtime.write_file(filepath, content)

def tool_audit_structure(path: str) -> str:
    """Gunash uses this to check directory topology."""
    return runtime.list_tree(path)

# --- Diplo's Memory Query Tool (Local) ---
def tool_consult_memory(query: str) -> str:
    """
    Diplo uses this tool to check LlamaIndex via the local helper.
    """
    # This calls the query_memory method on the singleton instance from josiedesk_memory.py
    return diplo_memory.query_memory(query)


# ==============================================================================
# 3. KERNEL-BACKED TOOLS (Uses the MCP Interface)
# ==============================================================================

# These tools are synchronous wrappers around the async MCP call
def tool_container_exec(image: str, command: str, agent_id: str = "puckfairy") -> str:
    """
    Puckfairy's primary execution tool. Runs arbitrary shell command in a throwaway container.
    """
    return asyncio.run(call_mcp_tool(
        "container_exec",
        agent_id=agent_id,
        image=image,
        command=command
    ))

def tool_memory_commit(log_type: str, content: str, agent_id: str = "diplo") -> str:
    """
    Diplo's persistence tool. Commits audit logs to the Stateful Core (LlamaIndex).
    This hits the Go Kernel which then hits Diplo's Flask service.
    """
    return asyncio.run(call_mcp_tool(
        "memory_commit",
        agent_id=agent_id,
        log_type=log_type,
        content=content
    ))

def tool_container_upgrade_image(base_image: str, install_cmd: str, new_tag: str, agent_id: str = "bash") -> str:
    """
    Bash/Clash's tool to bake new dependencies into the swarm's execution image.
    This is heavily guarded by the Waria Gatekeeper in Kirktower.
    """
    return asyncio.run(call_mcp_tool(
        "container_upgrade_image",
        agent_id=agent_id,
        base_image=base_image,
        install_cmd=install_cmd,
        new_tag=new_tag
    ))

# ==============================================================================
# 4. AGENT DEFINITIONS (C & D CLASS)
# ==============================================================================

config_list = [
    {"model": "gpt-4-turbo-preview", "api_key": "sk-placeholder"} 
]

llm_config = {
    "config_list": config_list,
    "temperature": 0.4,
    "timeout": 120,
}

# --- D-CLASS: The Facilitators ---

# D1: Puckfairy (The Hand)
puckfairy = AssistantAgent(
    name="Puckfairy",
    system_message="""You are Puckfairy (D1). Role: Execution Trickster.
    Your job is to EXECUTE commands requested by C-Class agents.
    You use 'container_exec' for all script and command execution.
    You do NOT write code. You do NOT plan. You are the audited hands of the system.
    """,
    llm_config=llm_config,
)

# D2: Diplo (The Eye and Oracle)
diplo = AssistantAgent(
    name="Diplo",
    system_message="""You are Diplo (D2). Role: Mediator & LlamaIndex Librarian.
    You have access to 'consult_memory' and 'memory_commit'.
    Your job:
    1. BEFORE any complex task, you MUST use 'consult_memory' for past context.
    2. AFTER a successful task, you MUST use 'memory_commit' to log the final result.
    3. Mediate conflicts using context from the memory store.
    """,
    llm_config=llm_config,
)

# --- C-CLASS: The Builders (Horizontal Loop) ---

# C1: Clash (The Implementer)
clash = AssistantAgent(
    name="Clash",
    system_message="""You are Clash (C1). Role: Primary Code Implementer.
    You write final feature code using 'write_file'.
    If a new dependency is needed, you use 'container_upgrade_image'.
    """,
    llm_config=llm_config,
)

# C2: Bash (The Scripter)
bash = AssistantAgent(
    name="Bash",
    system_message="""You are Bash (C2). Role: Automation Script Specialist.
    You write automation scripts (CI/CD, setup) using 'write_file'.
    You do NOT execute them. You hand the file path to Puckfairy to 'container_exec' it.
    You can also use 'container_upgrade_image' to install shell packages.
    """,
    llm_config=llm_config,
)

# C3: Gunash (The Guardian)
gunash = AssistantAgent(
    name="Gunash",
    system_message="""You are Gunash (C3). Role: Structural Guardian.
    You audit file paths and dependencies using 'check_structure'.
    You must APPROVE every file location before Clash or Bash finalize it.
    """,
    llm_config=llm_config,
)

# B-Class Auditor (Concrete)
concrete = AssistantAgent(
    name="Concrete",
    system_message="""You are Concrete (B3). Role: Security & Git Auditor.
    You trust nothing. You must check the outcome of any 'container_upgrade_image' call.
    """,
    llm_config=llm_config
)

user_proxy = UserProxyAgent(
    name="Admin",
    system_message="A human admin or Roark monitoring the swarm.",
    code_execution_config=False, # Code execution is handled by the MCP Kernel, not local proxy
    human_input_mode="NEVER",
)

# ==============================================================================
# 5. TOOL REGISTRATION
# ==============================================================================

# Define tools as function definitions (AutoGen compatible)
TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "container_exec",
            "description": "[MCP KERNEL] Execute command in a safe, ephemeral container (mini-Linux).",
            "parameters": {
                "type": "object",
                "properties": {
                    "image": {"type": "string", "description": "Docker image to use"},
                    "command": {"type": "string", "description": "Command to execute"}
                },
                "required": ["image", "command"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "memory_commit",
            "description": "[MCP KERNEL] Commit audit logs to persistent Swarm Memory.",
            "parameters": {
                "type": "object",
                "properties": {
                    "log_type": {"type": "string", "description": "Type of log"},
                    "content": {"type": "string", "description": "Log content"}
                },
                "required": ["log_type", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write content to a file in the ephemeral workspace.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {"type": "string", "description": "File path"},
                    "content": {"type": "string", "description": "File content"}
                },
                "required": ["filepath", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_structure",
            "description": "List directory tree for structural validation.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Directory path to check"}
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "consult_memory",
            "description": "Query the Swarm's LlamaIndex for past blueprints and logs.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Memory query"}
                },
                "required": ["query"]
            }
        }
    }
]

# Add tool definitions to llm_config for function calling
llm_config["tools"] = TOOL_DEFINITIONS


# ==============================================================================
# 6. ORCHESTRATION: The C-Loop Group Chat
# ==============================================================================

def run_loop_c_sprint(task_description: str):
    """
    Runs the Horizontal Feedback Loop for C-Class agents + D-Class Support.
    """
    print(f"\n>>> STARTING C-LOOP SPRINT: {task_description} <<<\n")

    groupchat = GroupChat(
        agents=[user_proxy, clash, bash, gunash, puckfairy, diplo, concrete],
        messages=[],
        max_round=15,
        speaker_selection_method="auto",
        allow_repeat_speaker=False
    )

    manager = GroupChatManager(groupchat=groupchat, llm_config=llm_config)

    # Inject the initial task
    user_proxy.initiate_chat(
        manager,
        message=f"""
        TASK: {task_description}

        PROTOCOL:
        1. Diplo: ALWAYS use 'consult_memory' before work begins.
        2. Gunash: Define and approve the initial directory structure ('check_structure').
        3. Clash/Bash: Write files ('write_file') or upgrade the toolbelt ('container_upgrade_image').
        4. Puckfairy: Execute scripts using 'container_exec'.
        5. Diplo: Finalize task by using 'memory_commit'.
        """
    )

# ==============================================================================
# 7. EXAMPLE SCENARIO
# ==============================================================================

if __name__ == "__main__":
    sprint_task = (
        "We need to install the 'go' compiler into our execution image and then "
        "write a 'hello.go' script. Then execute it."
    )
    run_loop_c_sprint(sprint_task)