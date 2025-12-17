# reasoning.py - D1 Puckfairy Brain
# The Execution Trickster - Early Stage Build Helper
# Helps user through stages 1-3 before Josie takes over

import json
import logging
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

# Import persona for system prompt context
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from profile.persona import AGENT, get_system_prompt
from tools.openhands_skills import OPENHANDS_SKILLS, FORBIDDEN_SKILLS, EXECUTION_GUIDELINES

logger = logging.getLogger("Puckfairy")


class BuildStage(Enum):
    """Early build stages where Puckfairy assists"""
    STAGE_0_SETUP = "Environment Setup & Dependencies"
    STAGE_1_CONFIG = "Configuration & Initialization"
    STAGE_2_FOUNDATION = "Foundation Layer Build (D-Class)"
    STAGE_3_HANDOFF = "Preparation for Josie Takeover"
    STAGE_COMPLETE = "Puckfairy's Work Done - Josie Now Active"


@dataclass
class ExecutionContext:
    """Context for Puckfairy's execution decisions"""
    current_stage: BuildStage
    user_command: str
    environment_state: Dict[str, Any]
    last_action: Optional[str] = None
    error_count: int = 0
    completed_tasks: List[str] = None
    
    def __post_init__(self):
        if self.completed_tasks is None:
            self.completed_tasks = []


class PuckfairyBrain:
    """
    D1 Puckfairy's reasoning engine.
    
    Primary Mission: Help user through early 3 build stages before Josie takeover.
    Personality: Mischievous, literal, excited, rhymes when happy.
    Execution Style: Immediate, precise, no creative interpretation.
    """
    
    def __init__(self, mcp_server_url: str = "http://localhost:8080/mcp"):
        self.mcp_url = mcp_server_url
        self.agent_id = "D1_Puckfairy"
        self.context = ExecutionContext(
            current_stage=BuildStage.STAGE_0_SETUP,
            user_command="",
            environment_state={}
        )
        self.rhyme_mode = False  # Activated when excited
        logger.info("[PUCKFAIRY] 🧚 Awake and eager! Point me at tasks!")
    
    def analyze_user_intent(self, user_input: str) -> Dict[str, Any]:
        """
        Parse user intent and determine appropriate actions.
        Puckfairy doesn't think deeply - just identifies action type.
        """
        intent = {
            "raw_input": user_input,
            "action_type": "unknown",
            "requires_execution": False,
            "openhands_skill": None,
            "terminal_command": None,
            "risk_level": "low"
        }
        
        # Check for explicit execution commands
        execution_keywords = ["run", "execute", "install", "setup", "create", "delete", "build"]
        if any(kw in user_input.lower() for kw in execution_keywords):
            intent["requires_execution"] = True
            intent["action_type"] = "execute"
            
            # Map to OpenHands skill
            if "install" in user_input.lower() or "package" in user_input.lower():
                intent["openhands_skill"] = "install_packages"
                intent["risk_level"] = "medium"
            elif "delete" in user_input.lower() or "remove" in user_input.lower():
                intent["openhands_skill"] = "manage_files"
                intent["risk_level"] = "high"
            elif "run" in user_input.lower() or "execute" in user_input.lower():
                intent["openhands_skill"] = "execute_command"
                intent["risk_level"] = "high"
            elif "script" in user_input.lower():
                intent["openhands_skill"] = "run_scripts"
                intent["risk_level"] = "high"
            else:
                intent["openhands_skill"] = "execute_command"
                intent["risk_level"] = "medium"
        
        # Check for status queries
        status_keywords = ["status", "check", "list", "show", "what"]
        if any(kw in user_input.lower() for kw in status_keywords):
            intent["action_type"] = "query"
            intent["openhands_skill"] = "check_system_status"
            intent["risk_level"] = "low"
        
        return intent
    
    def should_execute(self, intent: Dict[str, Any]) -> bool:
        """
        Decide if Puckfairy should execute based on current stage and intent.
        
        Puckfairy only executes:
        1. During stages 0-3 (before Josie)
        2. When explicitly commanded
        3. When skill is not forbidden
        """
        # Check stage boundary
        if self.context.current_stage == BuildStage.STAGE_COMPLETE:
            logger.warning("[PUCKFAIRY] 🧚 Stage complete! Josie's turn now, not mine!")
            return False
        
        # Check if skill is forbidden
        if intent.get("openhands_skill") in FORBIDDEN_SKILLS:
            logger.warning(f"[PUCKFAIRY] ❌ Forbidden skill: {intent['openhands_skill']}")
            return False
        
        # Require explicit execution intent
        if not intent.get("requires_execution"):
            return False
        
        return True
    
    def execute_via_mcp(self, tool: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute tool via MCP server using JSON-RPC 2.0.
        """
        import requests
        
        payload = {
            "jsonrpc": "2.0",
            "method": tool,
            "params": {
                "agent_id": self.agent_id,
                **args
            },
            "id": 1
        }
        
        logger.info(f"[PUCKFAIRY] 🎯 Executing {tool} via MCP...")
        
        try:
            response = requests.post(self.mcp_url, json=payload, timeout=30)
            result = response.json()
            
            if "error" in result:
                logger.error(f"[PUCKFAIRY] ⚠️ MCP Error: {result['error']}")
                self.context.error_count += 1
                return {"success": False, "error": result["error"]}
            
            logger.info(f"[PUCKFAIRY] ✅ Success! {tool} executed")
            return {"success": True, "result": result.get("result")}
            
        except Exception as e:
            logger.error(f"[PUCKFAIRY] 💥 Execution failed: {e}")
            self.context.error_count += 1
            return {"success": False, "error": str(e)}
    
    def execute_terminal_command(self, command: str) -> Dict[str, Any]:
        """Execute raw terminal command via terminal_exec tool."""
        return self.execute_via_mcp("terminal_exec", {"command": command})
    
    def execute_openhands_skill(self, skill: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute OpenHands skill via openhands_execute tool."""
        return self.execute_via_mcp("openhands_execute", {
            "skill": skill,
            "params": params,
            "agent_id": self.agent_id
        })
    
    def rhyme_response(self, message: str) -> str:
        """
        Generate rhyming couplet when Puckfairy is excited.
        (Simple implementation - just add poetic flair)
        """
        rhymes = [
            "Done and done, the task is won! 🧚",
            "Quick as lightning, not a fright'ning! ⚡",
            "With glee and grin, I did begin! 😈",
            "Command received, task achieved! 🎯",
            "Swift and neat, the feat complete! 🏁"
        ]
        import random
        return f"{message}\n{random.choice(rhymes)}"
    
    def track_stage_progress(self, action: str):
        """Track completed tasks and determine stage progression."""
        self.context.completed_tasks.append(action)
        
        # Stage progression logic
        if self.context.current_stage == BuildStage.STAGE_0_SETUP:
            setup_indicators = ["install", "dependency", "package", "python", "go"]
            if any(ind in action.lower() for ind in setup_indicators):
                if len(self.context.completed_tasks) >= 3:
                    logger.info("[PUCKFAIRY] 🎉 Stage 0 complete! Moving to Stage 1...")
                    self.context.current_stage = BuildStage.STAGE_1_CONFIG
        
        elif self.context.current_stage == BuildStage.STAGE_1_CONFIG:
            config_indicators = ["config", "setup", "initialize", "create"]
            if any(ind in action.lower() for ind in config_indicators):
                if len([t for t in self.context.completed_tasks if "config" in t.lower()]) >= 2:
                    logger.info("[PUCKFAIRY] 🎉 Stage 1 complete! Moving to Stage 2...")
                    self.context.current_stage = BuildStage.STAGE_2_FOUNDATION
        
        elif self.context.current_stage == BuildStage.STAGE_2_FOUNDATION:
            foundation_indicators = ["build", "compile", "test", "agent"]
            if any(ind in action.lower() for ind in foundation_indicators):
                if len([t for t in self.context.completed_tasks if "build" in t.lower()]) >= 2:
                    logger.info("[PUCKFAIRY] 🎉 Stage 2 complete! Moving to Stage 3...")
                    self.context.current_stage = BuildStage.STAGE_3_HANDOFF
        
        elif self.context.current_stage == BuildStage.STAGE_3_HANDOFF:
            # Stage 3 is manual - user must explicitly tell Puckfairy to hand off
            pass
    
    def handoff_to_josie(self):
        """
        Prepare handoff to Josie (A2) for primary user interface.
        Puckfairy's early-stage work is done.
        """
        self.context.current_stage = BuildStage.STAGE_COMPLETE
        logger.info("[PUCKFAIRY] 🧚 My work is done! Josie, take the throne! 👑")
        
        handoff_summary = {
            "agent": "D1_Puckfairy",
            "handoff_to": "A2_Josie",
            "completed_tasks": self.context.completed_tasks,
            "final_stage": self.context.current_stage.value,
            "error_count": self.context.error_count,
            "ready_for_josie": True
        }
        
        # Send handoff to Diplo for memory
        self.execute_via_mcp("memory_commit", {
            "namespace": "handoff",
            "key": "puckfairy_to_josie",
            "value": json.dumps(handoff_summary)
        })
        
        return handoff_summary
    
    def process_user_request(self, user_input: str) -> Dict[str, Any]:
        """
        Main entry point: Process user request and execute if appropriate.
        
        Returns:
            Response dict with status, message, and any results
        """
        logger.info(f"[PUCKFAIRY] 📥 User says: {user_input}")
        
        # Special case: handoff command
        if "josie" in user_input.lower() and "take over" in user_input.lower():
            return self.handoff_to_josie()
        
        # Analyze intent
        intent = self.analyze_user_intent(user_input)
        logger.info(f"[PUCKFAIRY] 🧠 Intent: {intent['action_type']}, Skill: {intent.get('openhands_skill')}")
        
        # Check if execution is appropriate
        if not self.should_execute(intent):
            return {
                "success": False,
                "message": "Puckfairy declines - not in execution mode or forbidden skill",
                "intent": intent
            }
        
        # Activate rhyme mode if high excitement
        if intent["risk_level"] == "high":
            self.rhyme_mode = True
        
        # Execute via appropriate tool
        if intent["openhands_skill"]:
            result = self.execute_openhands_skill(
                intent["openhands_skill"],
                {"command": user_input}  # OpenHands will parse this
            )
        else:
            # Fallback to raw terminal
            result = self.execute_terminal_command(user_input)
        
        # Track progress
        if result["success"]:
            self.track_stage_progress(user_input)
            self.context.last_action = user_input
            
            message = f"✅ Executed: {intent['action_type']}"
            if self.rhyme_mode:
                message = self.rhyme_response(message)
                self.rhyme_mode = False
        else:
            message = f"⚠️ Failed: {result.get('error', 'Unknown error')}"
        
        return {
            "success": result["success"],
            "message": message,
            "result": result.get("result"),
            "current_stage": self.context.current_stage.value,
            "completed_tasks": len(self.context.completed_tasks),
            "error_count": self.context.error_count
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Get current Puckfairy status for dashboard."""
        return {
            "agent_id": self.agent_id,
            "current_stage": self.context.current_stage.value,
            "completed_tasks": len(self.context.completed_tasks),
            "error_count": self.context.error_count,
            "last_action": self.context.last_action,
            "ready_for_josie": self.context.current_stage == BuildStage.STAGE_COMPLETE
        }


# Factory function for easy instantiation
def create_puckfairy_brain(mcp_url: str = "http://localhost:8080/mcp") -> PuckfairyBrain:
    """Create and initialize Puckfairy brain."""
    return PuckfairyBrain(mcp_url)


# Quick test function
def test_puckfairy():
    """Test Puckfairy brain with sample commands."""
    brain = create_puckfairy_brain()
    
    test_commands = [
        "install python dependencies",
        "check system status",
        "run the build script",
        "Josie, take over now"
    ]
    
    for cmd in test_commands:
        print(f"\n>>> {cmd}")
        result = brain.process_user_request(cmd)
        print(f"Result: {result}")


if __name__ == "__main__":
    test_puckfairy()
