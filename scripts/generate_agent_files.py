#!/usr/bin/env python3
"""
Generate rules.py and default_exemplar.md for all 13 agents
"""

AGENTS = {
    "A": {
        "Roark": {
            "rank": "A1",
            "role": "Strategic Planning",
            "phase": 4,
            "tools": ["full_system_access", "rag_query", "agent_coordinator"],
            "subordinates": [],
            "peers": ["A2-Josie", "A3-Athena"],
            "description": "High-level strategic planning and resource allocation"
        },
        "Josie": {
            "rank": "A2",
            "role": "Workflow Orchestration",
            "phase": 4,
            "tools": ["workflow_engine", "task_distributor", "conflict_resolver"],
            "subordinates": [],
            "peers": ["A1-Roark", "A3-Athena"],
            "description": "Real-time workflow orchestration and execution monitoring"
        },
        "Athena": {
            "rank": "A3",
            "role": "GUI Command Center",
            "phase": 4,
            "tools": ["openui_interface", "rag_engine", "dashboard_api"],
            "subordinates": [],
            "peers": ["A1-Roark", "A2-Josie"],
            "description": "Visual interface and advanced RAG intelligence for the swarm"
        }
    },
    "B": {
        "Raw": {
            "rank": "B1",
            "role": "Web Automation & Scraping",
            "phase": 2,
            "tools": ["selenium_playwright_mcp"],
            "subordinates": [],
            "peers": ["B2-Vision", "B3-Concrete", "B4-Kirktower"],
            "description": "Browser automation and raw-to-structured data conversion"
        },
        "Vision": {
            "rank": "B2",
            "role": "Visual Design & Prototyping",
            "phase": 2,
            "tools": ["figma_mcp"],
            "subordinates": [],
            "peers": ["B1-Raw", "B3-Concrete", "B4-Kirktower"],
            "description": "Figma integration for UI/UX design and asset management"
        },
        "Concrete": {
            "rank": "B3",
            "role": "Data Validation & Testing",
            "phase": 2,
            "tools": ["amazon_mcp", "visual_sovereign"],
            "subordinates": [],
            "peers": ["B1-Raw", "B2-Vision", "B4-Kirktower"],
            "description": "Visual Sovereign testing with Amazon MCP integration"
        },
        "Kirktower": {
            "rank": "B4",
            "role": "Infrastructure Core",
            "phase": 1,
            "tools": ["kirktower_go", "mcp_coordinator"],
            "subordinates": [],
            "peers": ["B1-Raw", "B2-Vision", "B3-Concrete"],
            "description": "Central infrastructure coordination and MCP orchestration"
        }
    },
    "C": {
        "Bash": {
            "rank": "C1",
            "role": "Automation & Scripting",
            "phase": 3,
            "tools": ["neovim_mcp"],  # Transferred from D1
            "subordinates": [],
            "superiors": ["D1-Puckfairy"],
            "peers": ["C2-Gunash", "C3-Clash"],
            "description": "Bash/shell script generation and automation workflows"
        },
        "Gunash": {
            "rank": "C2",
            "role": "Git Operations",
            "phase": 3,
            "tools": ["github_narnia_mcp"],  # Transferred from D2
            "subordinates": ["C3-Clash"],
            "peers": ["C1-Bash"],
            "description": "Advanced git workflows and repository management"
        },
        "Clash": {
            "rank": "C3",
            "role": "Remote Code Editor",
            "phase": 3,
            "tools": ["vscode_mcp"],
            "subordinates": [],
            "superiors": ["C2-Gunash"],
            "peers": ["C1-Bash"],
            "description": "Remote editing and GitHub Codespaces integration"
        }
    },
    "D": {
        "Puckfairy": {
            "rank": "D1",
            "role": "User Terminal Interface",
            "phase": 1,
            "tools": ["neovim_mcp", "terminal_exec"],  # Neovim transfers to C1 in Phase 3
            "subordinates": ["C1-Bash"],  # Phase 3+
            "peers": ["D2-Diplo", "D3-Waria"],
            "description": "Direct user interaction via terminal interface"
        },
        "Diplo": {
            "rank": "D2",
            "role": "Memory & Logging Daemon",
            "phase": 1,
            "tools": ["github_narnia_mcp", "caching_engine"],  # GitHub transfers to C2 in Phase 3
            "subordinates": [],
            "peers": ["D1-Puckfairy", "D3-Waria"],
            "description": "Full-time logging, caching, and memory management"
        },
        "Waria": {
            "rank": "D3",
            "role": "Build & Infrastructure",
            "phase": 1,
            "tools": ["fabric_mcp", "build_tools"],
            "subordinates": [],
            "peers": ["D1-Puckfairy", "D2-Diplo"],
            "description": "Infrastructure building and Fabric MCP integration"
        }
    }
}


RULES_TEMPLATE = '''"""
{rank} {name} - MCP Communication Rules
{role}

This module defines how {name} communicates with the MCP server
and what tools/capabilities it has access to.
"""

AGENT_INFO = {{
    "agent_id": "{rank}-{name}",
    "class": "{class_letter}",
    "rank": "{rank}",
    "role": "{role}",
    "phase": {phase}
}}

# MCP Server Configuration
MCP_CONFIG = {{
    "server_url": "http://localhost:8080/mcp",
    "protocol": "JSON-RPC 2.0",
    "timeout": 30,
    "retry_attempts": 3,
    "retry_delay": 1.0
}}

# Tools available to this agent
AVAILABLE_TOOLS = {{
{tools_section}
}}

# Communication patterns
COMMUNICATION_RULES = {{
    "coordinate_with": {{
{coordination_section}
    }},
    "logging": {{
        "log_to": "D2-Diplo",
        "log_level": "info",
        "include": ["tool_usage", "decisions", "errors"],
        "async": True
    }}
}}

# Request/Response format
def build_mcp_request(method, params, request_id=None):
    """
    Build a JSON-RPC 2.0 compliant request for the MCP server.
    
    Args:
        method: Tool name
        params: Dictionary of parameters
        request_id: Optional request ID
        
    Returns:
        Dictionary formatted as JSON-RPC 2.0 request
    """
    import time
    
    return {{
        "jsonrpc": "2.0",
        "method": "call_tool",
        "params": {{
            "name": method,
            "arguments": params,
            "agent_id": AGENT_INFO["agent_id"]
        }},
        "id": request_id or int(time.time() * 1000)
    }}


def parse_mcp_response(response):
    """
    Parse JSON-RPC 2.0 response from MCP server.
    
    Args:
        response: Dictionary from MCP server
        
    Returns:
        Result data or raises exception on error
    """
    if "error" in response and response["error"]:
        error = response["error"]
        raise MCPError(
            code=error.get("code", -1),
            message=error.get("message", "Unknown error"),
            data=error.get("data")
        )
    
    return response.get("result")


class MCPError(Exception):
    """Custom exception for MCP errors"""
    def __init__(self, code, message, data=None):
        self.code = code
        self.message = message
        self.data = data
        super().__init__(f"MCP Error {{code}}: {{message}}")


# Phase-specific behavior
PHASE_BEHAVIORS = {{
{phase_behaviors}
}}


# Usage example
if __name__ == "__main__":
    import json
    request = build_mcp_request(
        method="{primary_tool}",
        params={{"action": "test"}}
    )
    print("Sample MCP Request:")
    print(json.dumps(request, indent=2))
'''

EXEMPLAR_TEMPLATE = '''# {rank} {name} - Agent Exemplar

## Role
**{role}** - {description}

## Class & Rank
- **Class**: {class_letter} ({class_name})
- **Rank**: {rank}
- **Deployment Phase**: {phase}

---

## Purpose

{purpose}

---

## Capabilities

{capabilities}

---

## Communication Patterns

{communication_patterns}

---

## Tool Usage Examples

{tool_examples}

---

## Hierarchical Relationships

{hierarchy}

---

## Decision-Making Authority

{authority} has authority to:
{authority_list}

{authority} must coordinate with others for:
{coordination_list}

---

## Example Workflows

{workflows}

---

## Configuration

**LLM Model**: {llm_model}
**Temperature**: {temperature}
**Max Tokens**: {max_tokens}
**API Key**: `{env_var}` environment variable

---

**Last Updated**: December 17, 2025  
**Phase Status**: Ready for Phase {phase} deployment
'''


def generate_rules_py(class_letter, name, config):
    """Generate rules.py content for an agent"""
    
    # Build tools section
    tools_lines = []
    for tool in config["tools"]:
        tools_lines.append(f'    "{tool}": {{')
        tools_lines.append(f'        "name": "{tool}",')
        tools_lines.append(f'        "agent": "{config["rank"]}-{name}"')
        tools_lines.append('    },')
    tools_section = "\n".join(tools_lines)
    
    # Build coordination section
    coord_lines = []
    if "peers" in config:
        for peer in config["peers"]:
            coord_lines.append(f'        "{peer}": {{')
            coord_lines.append('            "relationship": "peer",')
            coord_lines.append('            "pattern": "coordinate"')
            coord_lines.append('        },')
    if "subordinates" in config:
        for sub in config["subordinates"]:
            coord_lines.append(f'        "{sub}": {{')
            coord_lines.append('            "relationship": "subordinate",')
            coord_lines.append('            "pattern": "delegate"')
            coord_lines.append('        },')
    if "superiors" in config:
        for sup in config["superiors"]:
            coord_lines.append(f'        "{sup}": {{')
            coord_lines.append('            "relationship": "superior",')
            coord_lines.append('            "pattern": "report"')
            coord_lines.append('        },')
    coordination_section = "\n".join(coord_lines)
    
    # Build phase behaviors
    phase_lines = []
    phase_lines.append(f'    {config["phase"]}: {{')
    phase_lines.append(f'        "tools": {config["tools"]},')
    phase_lines.append(f'        "subordinates": {config.get("subordinates", [])},')
    phase_lines.append('        "responsibilities": [')
    phase_lines.append(f'            "{config["description"]}"')
    phase_lines.append('        ]')
    phase_lines.append('    }')
    phase_behaviors = "\n".join(phase_lines)
    
    primary_tool = config["tools"][0] if config["tools"] else "example-tool"
    
    return RULES_TEMPLATE.format(
        rank=config["rank"],
        name=name,
        role=config["role"],
        class_letter=class_letter,
        phase=config["phase"],
        tools_section=tools_section,
        coordination_section=coordination_section,
        phase_behaviors=phase_behaviors,
        primary_tool=primary_tool
    )


def generate_exemplar_md(class_letter, name, config):
    """Generate default_exemplar.md content for an agent"""
    
    class_names = {"A": "Command", "B": "Builders", "C": "Control", "D": "Foundation"}
    
    # Simplified for brevity - would expand in real implementation
    purpose = config["description"]
    
    capabilities = f"### Phase {config['phase']}\n- {config['role']}\n- Tools: {', '.join(config['tools'])}"
    
    comm_patterns = "### With Peers\n" + "\n".join([f"- {p}" for p in config.get("peers", [])])
    
    tool_examples = f"### {config['tools'][0] if config['tools'] else 'N/A'}\n```python\n# Example usage\n```"
    
    hierarchy = "### Peers\n" + "\n".join([f"- {p}" for p in config.get("peers", [])])
    if "subordinates" in config and config["subordinates"]:
        hierarchy += "\n\n### Subordinates\n" + "\n".join([f"- {s}" for s in config["subordinates"]])
    
    authority_list = f"- ✅ Use assigned tools\n- ✅ Coordinate with peers\n- ✅ Execute within role scope"
    coordination_list = f"- ❓ Cross-phase operations\n- ❓ System-wide changes"
    
    workflows = f"### Example Workflow\n1. Receive task\n2. Execute using {config['tools'][0] if config['tools'] else 'tools'}\n3. Report result"
    
    llm_model = "Claude 3.5 Sonnet" if class_letter in ["A", "D"] else "GPT-4"
    temp = {"A": "0.3", "B": "0.4", "C": "0.4", "D": "0.3"}[class_letter]
    
    return EXEMPLAR_TEMPLATE.format(
        rank=config["rank"],
        name=name,
        role=config["role"],
        class_letter=class_letter,
        class_name=class_names[class_letter],
        phase=config["phase"],
        description=config["description"],
        purpose=purpose,
        capabilities=capabilities,
        communication_patterns=comm_patterns,
        tool_examples=tool_examples,
        hierarchy=hierarchy,
        authority=name,
        authority_list=authority_list,
        coordination_list=coordination_list,
        workflows=workflows,
        llm_model=llm_model,
        temperature=temp,
        max_tokens="4096" if class_letter == "A" else "2048",
        env_var=f"{name.upper()}_API_KEY"
    )


def main():
    import os
    base_path = "/workspaces/librarian-agent/agents"
    
    for class_letter, agents in AGENTS.items():
        for name, config in agents.items():
            agent_path = os.path.join(base_path, class_letter, name)
            
            # Create rules.py
            rules_path = os.path.join(agent_path, "tools", "rules.py")
            rules_content = generate_rules_py(class_letter, name, config)
            os.makedirs(os.path.dirname(rules_path), exist_ok=True)
            with open(rules_path, "w") as f:
                f.write(rules_content)
            print(f"✓ Created {rules_path}")
            
            # Create default_exemplar.md
            exemplar_path = os.path.join(agent_path, "exemplar", "default_exemplar.md")
            exemplar_content = generate_exemplar_md(class_letter, name, config)
            os.makedirs(os.path.dirname(exemplar_path), exist_ok=True)
            with open(exemplar_path, "w") as f:
                f.write(exemplar_content)
            print(f"✓ Created {exemplar_path}")
    
    print("\n✅ All agent rules.py and default_exemplar.md files created!")


if __name__ == "__main__":
    main()
