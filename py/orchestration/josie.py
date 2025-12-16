"""
josie.py - Core Vertical Loop Orchestrator
Foundational orchestration layer for phase-based agent coordination.
"""

import json
import asyncio
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable, Any, Type
from pathlib import Path
from enum import Enum
import httpx
import time

# ==============================================================================
# --- EXTERNAL DEPENDENCIES ---
# ==============================================================================
try:
    from py.memory.diplo import diplo_memory
    from py.orchestration.c_loop import run_loop_c_sprint
except ImportError:
    print("[CORE] CRITICAL: Missing dependencies. Using Mocks.")
    
    class MockMemory:
        def ingest_blueprint(self, context, task_name):
            print(f"[CORE MOCK] Ingesting blueprint for '{task_name}' to mock memory.")
        def query_memory(self, query):
            return "MOCK: No historical context available."
    diplo_memory = MockMemory()

    def run_loop_c_sprint(**kwargs):
        print(f"[CORE MOCK] Triggering mock C-Loop with: {kwargs.get('task_description', 'No task')[:50]}...")
        return "MOCK_ARTIFACT_ID"


# ==============================================================================
# 1. CORE ARCHITECTURAL DEFINITIONS
# ==============================================================================

class Phase(Enum):
    """Feedback loop phases - strictly ordered (The Vertical Flow)."""
    BEGINNING = "beginning"
    BLUEPRINT = "blueprint"   # Roark is active (A-Class)
    DOCTRINE_CHECK = "doctrine_check" # Josie is active (B-Class Audit)
    C_LOOP_SPRINT = "c_loop_sprint" # C-Class Swarm is active (Horizontal)
    SUPERVISION = "supervision" # Post-C-Loop audit (B-Class Audit)
    CONCLUSION = "conclusion"


class ModelClass(Enum):
    """Model hierarchy for cost and capability management."""
    A = "70B+"
    B = "15-60B"
    C = "3.5-13B"
    D = "<3B"


@dataclass
class Agent:
    """Core Agent definition with identity, constraints, and capabilities."""
    name: str
    codename: str
    model_class: ModelClass
    model_endpoint: str
    role: str
    persona: str

    temporal_scope: str
    authority_type: str
    irreversibility_level: float


# ==============================================================================
# 2. ORCHESTRATION FRAMEWORK (Action/Role Pattern)
# ==============================================================================

@dataclass
class JosieAction:
    """Base class for all discrete, atomic actions in the Vertical Loop."""
    name: str
    phase: Phase
    
    async def run(self, context: Any) -> Dict[str, Any]:
        """Execute the action and return a structured result."""
        raise NotImplementedError

@dataclass
class JosieRole:
    """Base class for Josie and other phase-managing Agents (The Vertical Orchestrators)."""
    name: str
    profile: str
    goal: str
    
    actions: List[Type[JosieAction]] = field(default_factory=list)
    watch_signals: List[Phase] = field(default_factory=list)

    def set_actions(self, actions: List[Type[JosieAction]]):
        self.actions = actions

    def _watch(self, phases: List[Phase]):
        """Defines which phases this orchestrator monitors."""
        self.watch_signals = phases


# ==============================================================================
# 3. VERTICAL ACTIONS (Josie's Primary Commands)
# ==============================================================================

class DoctrineCheck(JosieAction):
    """
    Action: Ensures the Roark Blueprint complies with core architectural doctrine
    before allowing the C-Loop (cost, resource, security checks).
    """
    name: str = "DoctrineCheck"
    phase: Phase = Phase.DOCTRINE_CHECK

    async def run(self, blueprint_context: str) -> Dict[str, Any]:
        print(f"\n[Josie: DoctrineCheck] Auditing blueprint (length: {len(blueprint_context)})...")
        await asyncio.sleep(0.5)

        if len(blueprint_context) > 10000:
             return {"status": "REJECTED", "message": "Blueprint exceeds size threshold, too complex for one sprint."}

        if "git push --force" in blueprint_context.lower():
            return {"status": "NEEDS_APPROVAL", "message": "High-risk git operation detected. Halting for Concrete (B3) approval."}

        return {"status": "APPROVED", "message": "Blueprint is compliant with all core doctrines."}

class HandOffToBuilders(JosieAction):
    """
    Action: 1. Commits the final Blueprint to Diplo's memory.
            2. Triggers the C-Class AutoGen Swarm (run_loop_c_sprint).
    """
    name: str = "HandOffToBuilders"
    phase: Phase = Phase.C_LOOP_SPRINT

    async def run(self, blueprint_context: str) -> Dict[str, Any]:
        task_name = blueprint_context.split('\n')[0].strip()
        print(f"\n[Josie] Handing blueprint to Diplo for indexing ('{task_name}')...")
        diplo_memory.ingest_blueprint(blueprint_context, task_name)

        print(f"\n[Josie] Blueprint Approved. Waking C-Class Swarm (Horizontal Consensus Loop)...\n")

        construction_result = run_loop_c_sprint(
            task_description=f"Implement this Blueprint:\n{blueprint_context}"
        )

        return {"status": "COMPLETE", "artifact_log": construction_result}


# ==============================================================================
# 4. JOSIE ORCHESTRATOR (The Vertical Loop Manager)
# ==============================================================================

class Josie(JosieRole):
    name: str = "Josie"
    profile: str = "The Pragmatist"
    goal: str = "Ensure feasibility and Orchestrate Vertical Phase Transitions."
    
    current_phase: Phase = Phase.BEGINNING
    blueprint_context: Optional[str] = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_actions([DoctrineCheck, HandOffToBuilders])
        self._watch([Phase.BLUEPRINT])

    async def run(self, initial_task: str):
        """
        The main orchestration loop for the entire software construction process.
        Manages the sequential, vertical transitions.
        """
        print(f"\n--- JOSIEDESK VERTICAL ORCHESTRATION STARTED ---")
        print(f"Task: {initial_task[:50]}...")
        self.current_phase = Phase.BEGINNING
        
        self.current_phase = Phase.BLUEPRINT
        self.blueprint_context = f"TASK: {initial_task}\n\nBLUEPRINT:\n1. Prepare image by installing Python.\n2. Write 'main.py' file.\n3. Execute 'main.py' to verify." 
        print(f"\n[Josie] PHASE: {self.current_phase.name}. Roark delivered the blueprint.")
        
        doctrine_check_action = DoctrineCheck(name="DoctrineCheck", phase=Phase.DOCTRINE_CHECK)
        self.current_phase = Phase.DOCTRINE_CHECK
        print(f"\n[Josie] PHASE: {self.current_phase.name}. Starting doctrine audit...")
        
        doctrine_result = await doctrine_check_action.run(self.blueprint_context)
        
        if doctrine_result['status'] != 'APPROVED':
            print(f"[Josie] DOCTRINE FAIL: {doctrine_result['message']}. Halting construction.")
            self.current_phase = Phase.CONCLUSION
            return f"ORCHESTRATION HALTED: {doctrine_result['message']}"

        hand_off_action = HandOffToBuilders(name="HandOffToBuilders", phase=Phase.C_LOOP_SPRINT)
        self.current_phase = Phase.C_LOOP_SPRINT
        print(f"\n[Josie] PHASE: {self.current_phase.name}. Handoff to C-Class swarm...")

        handoff_result = await hand_off_action.run(self.blueprint_context)

        self.current_phase = Phase.CONCLUSION
        print(f"\n[Josie] PHASE: {self.current_phase.name}. Vertical loop completed.")
        return f"FINAL RESULT: {handoff_result['artifact_log']}. Status: {handoff_result['status']}"

# ==============================================================================
# 5. EXECUTION EXAMPLE
# ==============================================================================

if __name__ == "__main__":
    josie_orchestrator = Josie()
    task = "Build a simple Python script to calculate Fibonacci sequence up to 10."
    final_output = asyncio.run(josie_orchestrator.run(task))

    print(f"\n--- VERTICAL ORCHESTRATION SUMMARY ---")
    print(f"Task: {task}")
    print(f"Final Output: {final_output}")
    print(f"Final Phase: {josie_orchestrator.current_phase.name}")
