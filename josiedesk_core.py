"""
JosieDesk Core - Multi-Agent Software Construction Swarm
Foundational orchestration layer for phase-based agent coordination
"""

import json
import asyncio
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable, Any
from pathlib import Path
from enum import Enum
import httpx


class Phase(Enum):
    """Feedback loop phases - strictly ordered"""
    BEGINNING = "beginning"
    BLUEPRINT = "blueprint"
    SELECTION = "selection"
    LOOP_A = "loop_a"  # Code & Audit
    LOOP_B = "loop_b"  # Ideation & Direction
    LOOP_C = "loop_c"  # Skeleton Building
    SUPERVISION = "supervision"
    CONCLUSION = "conclusion"


class ModelClass(Enum):
    """Model hierarchy for cost and capability management"""
    A = "70B+"      # Strategic, synthesis, blueprinting
    B = "15-60B"    # Ideation, planning, auditing, process
    C = "3.5-13B"   # Code generation, refactors, scripts
    D = "<3B"       # Embeddings, tooling, execution, routing


@dataclass
class Agent:
    """Agent definition with identity, constraints, and capabilities"""
    name: str
    codename: str
    model_class: ModelClass
    model_endpoint: str  # vLLM endpoint
    role: str
    persona: str

    # Behavioral constraints
    temporal_scope: str  # past/present/near-future/far-future
    authority_type: str  # positive/negative/observational/operational
    irreversibility_level: str  # none/low/guards_surface/high
    modality: List[str]  # textual/structural/procedural/evaluative/meta

    # File system
    base_path: Path = field(default_factory=Path)
    context: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        self.base_path = Path(f"./josiedesk/{self.model_class.name}_agents/{self.name}")
        self.base_path.mkdir(parents=True, exist_ok=True)

    def load_profile(self) -> Dict:
        """Load agent profile from profile.md"""
        profile_path = self.base_path / "profile.md"
        if profile_path.exists():
            return {"profile": profile_path.read_text()}
        return {}

    def load_exemplars(self) -> List[str]:
        """Load historical excellent prompts"""
        exemplar_path = self.base_path / "exemplar"
        if exemplar_path.exists():
            return [f.read_text() for f in exemplar_path.glob("*.md")]
        return []


class SwarmState:
    """Global state manager for the swarm"""
    def __init__(self):
        self.current_phase: Phase = Phase.BEGINNING
        self.logs: List[Dict] = []
        self.frozen_data: Dict = {}  # For phase transitions
        self.user_input: Dict = {}
        self.git_state: Dict = {}

    def log(self, agent: str, phase: Phase, content: Any):
        """Log agent output with metadata"""
        entry = {
            "timestamp": asyncio.get_event_loop().time(),
            "agent": agent,
            "phase": phase.value,
            "content": content
        }
        self.logs.append(entry)

    def freeze_phase(self, phase: Phase) -> Dict:
        """Freeze and serialize phase data for handoff"""
        phase_logs = [l for l in self.logs if l["phase"] == phase.value]
        frozen = {
            "phase": phase.value,
            "logs": phase_logs,
            "user_input": self.user_input.copy()
        }
        self.frozen_data[phase.value] = frozen
        return frozen

    def export_logs(self, path: Path):
        """Export logs to JSON"""
        path.write_text(json.dumps(self.logs, indent=2))


class ModelClient:
    """vLLM HTTP client for model inference"""
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=300.0)

    async def generate(self,
                      endpoint: str,
                      prompt: str,
                      system: str = "",
                      max_tokens: int = 2000,
                      temperature: float = 0.7) -> str:
        """Call vLLM completion endpoint"""
        url = f"{self.base_url}/v1/completions"

        # Build full prompt with system
        full_prompt = f"{system}\n\n{prompt}" if system else prompt

        payload = {
            "model": endpoint,
            "prompt": full_prompt,
            "max_tokens": max_tokens,
            "temperature": temperature
        }

        response = await self.client.post(url, json=payload)
        response.raise_for_status()

        data = response.json()
        return data["choices"][0]["text"]

    async def close(self):
        await self.client.aclose()


class SwarmOrchestrator:
    """SWARM-PRIME: Main orchestration intelligence"""

    def __init__(self, model_client: ModelClient):
        self.client = model_client
        self.state = SwarmState()
        self.agents: Dict[str, Agent] = {}
        self._init_agents()

    def _init_agents(self):
        """Initialize all 11 agents with their configurations"""

        # A-CLASS
        self.agents["roark"] = Agent(
            name="Roark", codename="A1", model_class=ModelClass.A,
            model_endpoint="roark-70b",
            role="Alpha Architect, Final Synthesist",
            persona="Howard Roark - expert software engineer",
            temporal_scope="far-future",
            authority_type="framing+critique",
            irreversibility_level="observes",
            modality=["textual", "evaluative"]
        )

        self.agents["josie"] = Agent(
            name="Josie", codename="A2", model_class=ModelClass.A,
            model_endpoint="josie-70b",
            role="Primary Builder, Morning Star",
            persona="Marisa Tomei cyborg with sass and progressive heat",
            temporal_scope="present-to-near-future",
            authority_type="negative-by-consensus",
            irreversibility_level="guards_surface",
            modality=["textual", "structural"]
        )

        # B-CLASS
        self.agents["raw"] = Agent(
            name="Raw", codename="B1", model_class=ModelClass.B,
            model_endpoint="raw-30b",
            role="Unfiltered Ideation Generator",
            persona="No personality - pure possibility",
            temporal_scope="early-exploration",
            authority_type="none",
            irreversibility_level="none",
            modality=["textual"]
        )

        self.agents["vision"] = Agent(
            name="Vision", codename="B2", model_class=ModelClass.B,
            model_endpoint="vision-30b",
            role="Conceptual Synthesist",
            persona="Wise hippy, ayahuasca calm",
            temporal_scope="early-to-mid",
            authority_type="observational",
            irreversibility_level="advisory",
            modality=["textual", "evaluative"]
        )

        self.agents["concrete"] = Agent(
            name="Concrete", codename="B3", model_class=ModelClass.B,
            model_endpoint="concrete-30b",
            role="Grounding Auditor",
            persona="Retired German war veteran",
            temporal_scope="present+past",
            authority_type="audit-veto",
            irreversibility_level="flags-before-crossing",
            modality=["evaluative"]
        )

        self.agents["waria"] = Agent(
            name="Waria", codename="B4", model_class=ModelClass.B,
            model_endpoint="waria-15b",
            role="Reasoning Horizon Sentinel",
            persona="Quiet, patient, essential",
            temporal_scope="meta-temporal",
            authority_type="observational",
            irreversibility_level="none",
            modality=["meta"]
        )

        # C-CLASS
        self.agents["clash"] = Agent(
            name="Clash", codename="C1", model_class=ModelClass.C,
            model_endpoint="clash-13b",
            role="Primary Code Implementer",
            persona="Wade from Kim Possible + OCD",
            temporal_scope="present",
            authority_type="subordinate",
            irreversibility_level="below-surface",
            modality=["procedural"]
        )

        self.agents["bash"] = Agent(
            name="Bash", codename="C2", model_class=ModelClass.C,
            model_endpoint="bash-13b",
            role="Automation Script Specialist",
            persona="Retired Hells Angels grey-hat hacker",
            temporal_scope="present",
            authority_type="subordinate",
            irreversibility_level="low",
            modality=["procedural"]
        )

        self.agents["gunash"] = Agent(
            name="Gunash", codename="C3", model_class=ModelClass.C,
            model_endpoint="gunash-13b",
            role="Structural Guardian",
            persona="Indian chess grandmaster + DevOps Scrum Master",
            temporal_scope="near-future",
            authority_type="negative-over-structure",
            irreversibility_level="guards_surface",
            modality=["structural"]
        )

        # D-CLASS
        self.agents["puckfairy"] = Agent(
            name="Puckfairy", codename="D1", model_class=ModelClass.D,
            model_endpoint="puckfairy-3b",
            role="Execution Trickster",
            persona="Puck from Midsummer Night's Dream",
            temporal_scope="immediate",
            authority_type="operational",
            irreversibility_level="low",
            modality=["procedural"]
        )

        self.agents["diplo"] = Agent(
            name="Diplo", codename="D2", model_class=ModelClass.D,
            model_endpoint="diplo-3b",
            role="Mediator and Interpreter",
            persona="Patient, kind, encouraging",
            temporal_scope="present",
            authority_type="supportive",
            irreversibility_level="none",
            modality=["textual"]
        )

        self.agents["kirktower"] = Agent(
            name="Kirktower", codename="D3", model_class=ModelClass.D,
            model_endpoint="kirktower-3b",
            role="Process Control Authority",
            persona="Air Force air traffic control",
            temporal_scope="real-time",
            authority_type="operational-override",
            irreversibility_level="emergency-only",
            modality=["meta"]
        )

    async def invoke_agent(self,
                          agent_name: str,
                          prompt: str,
                          system_override: str = "") -> str:
        """Invoke a single agent with context"""
        agent = self.agents[agent_name]

        # Build system prompt from profile
        profile = agent.load_profile()
        system = system_override or f"""You are {agent.name} ({agent.codename}).

Role: {agent.role}
Persona: {agent.persona}

Temporal Scope: {agent.temporal_scope}
Authority: {agent.authority_type}
Irreversibility Level: {agent.irreversibility_level}

{profile.get('profile', '')}
"""

        result = await self.client.generate(
            endpoint=agent.model_endpoint,
            prompt=prompt,
            system=system
        )

        self.state.log(agent.name, self.state.current_phase, result)
        return result

    async def phase_beginning(self, raw_prompt: str, vision_prompt: str, concrete_prompt: str):
        """FEEDBACK: BEGINNING - Route to B1, B2, B3"""
        self.state.current_phase = Phase.BEGINNING

        results = await asyncio.gather(
            self.invoke_agent("raw", raw_prompt),
            self.invoke_agent("vision", vision_prompt),
            self.invoke_agent("concrete", concrete_prompt)
        )

        return {
            "raw": results[0],
            "vision": results[1],
            "concrete": results[2]
        }

    async def phase_blueprint(self, b_outputs: Dict) -> Dict:
        """FEEDBACK: BLUEPRINT - Roark synthesizes and asks 4 questions"""
        self.state.current_phase = Phase.BLUEPRINT

        prompt = f"""Synthesize these three perspectives into a Master Blueprint:

RAW OUTPUT:
{b_outputs['raw']}

VISION OUTPUT:
{b_outputs['vision']}

CONCRETE OUTPUT:
{b_outputs['concrete']}

You must:
1. Summarize without dilution
2. Reflect on internal consistency
3. Produce a Master Blueprint (main quest, side quests, optional quests)
4. Ask exactly FOUR future-shaping questions

Deliver the blueprint and questions now.
"""

        blueprint = await self.invoke_agent("roark", prompt)
        return {"blueprint": blueprint}

    async def phase_selection(self, user_answers: Dict):
        """FEEDBACK: SELECTION - Freeze and hand to Josie"""
        self.state.current_phase = Phase.SELECTION
        self.state.user_input = user_answers

        frozen = self.state.freeze_phase(Phase.BLUEPRINT)

        # Hand frozen bundle to Josie
        prompt = f"""Here is the frozen blueprint phase and user answers:

{json.dumps(frozen, indent=2)}

Begin building the primary skeleton for the first component.
"""

        skeleton = await self.invoke_agent("josie", prompt)
        return {"skeleton": skeleton}

    async def seek_consensus(self, josie_concern: str) -> bool:
        """Josie seeks consensus with C3, D2, B2 when blocking"""
        results = await asyncio.gather(
            self.invoke_agent("gunash", f"Josie has a concern: {josie_concern}\nDo you agree?"),
            self.invoke_agent("diplo", f"Mediate this concern: {josie_concern}"),
            self.invoke_agent("vision", f"Rate confidence on this concern: {josie_concern}")
        )

        # Simple consensus: if 2/3 agree, block
        # In practice, parse their responses more carefully
        return True  # Placeholder

    async def run_sprint(self,
                        raw_prompt: str,
                        vision_prompt: str,
                        concrete_prompt: str,
                        user_answers_callback: Callable):
        """Execute a full sprint from BEGINNING to CONCLUSION"""

        # Phase 1: Beginning
        print("=== PHASE: BEGINNING ===")
        b_outputs = await self.phase_beginning(raw_prompt, vision_prompt, concrete_prompt)

        # Phase 2: Blueprint
        print("=== PHASE: BLUEPRINT ===")
        blueprint_result = await self.phase_blueprint(b_outputs)

        # Get user answers to Roark's questions
        user_answers = await user_answers_callback(blueprint_result["blueprint"])

        # Phase 3: Selection
        print("=== PHASE: SELECTION ===")
        selection_result = await self.phase_selection(user_answers)

        # Concurrency loops would continue here...
        # Loop A: B3+C1+D1+C2
        # Loop B: B1+B2
        # Loop C: A2+C3+D2

        print("=== SPRINT COMPLETE ===")
        return selection_result


# Example usage
async def main():
    """Example sprint execution"""
    client = ModelClient("http://localhost:8000")
    orchestrator = SwarmOrchestrator(client)

    async def get_user_answers(blueprint: str) -> Dict:
        """Simulate user answering Roark's questions"""
        print(f"\n{blueprint}\n")
        # In practice, get real user input
        return {
            "q1": "Answer 1",
            "q2": "Answer 2",
            "q3": "Answer 3",
            "q4": "Answer 4"
        }

    result = await orchestrator.run_sprint(
        raw_prompt="Build a process manager CLI with GPU awareness",
        vision_prompt="Reframe the process manager concept",
        concrete_prompt="List minimum viable commands and constraints",
        user_answers_callback=get_user_answers
    )

    # Export logs
    orchestrator.state.export_logs(Path("./sprint_logs.json"))

    await client.close()


if __name__ == "__main__":
    asyncio.run(main())
"""
JosieDesk Core - MetaGPT Architecture for A & B Class Agents
Orchestrates the Strategic (A) and Ideation (B) layers using Standardized Operating Procedures.
"""

import asyncio
import json
import httpx
from typing import Dict, Any, List
from dataclasses import dataclass

from metagpt.actions import Action
from metagpt.roles import Role
from metagpt.team import Team
from metagpt.schema import Message
from metagpt.logs import logger

# ==============================================================================
# 1. INFRASTRUCTURE & CONTROL PLANE (Kirktower Link)
# ==============================================================================

KIRKTOWER_API = "http://localhost:9090/api"

async def report_waria(agent_name: str, content: str, token_count: int):
    """
    Reports cognitive load and token usage to the Go Control Tower.
    Waria (B4) resides in the Tower, monitoring this stream.
    """
    try:
        async with httpx.AsyncClient() as client:
            await client.post(
                f"{KIRKTOWER_API}/waria",
                json={
                    "agent": agent_name,
                    "output": content,
                    "token_count": token_count
                },
                timeout=2.0
            )
    except Exception as e:
        logger.warning(f"Failed to report to Kirktower: {e}")

async def report_state_change(phase: str, active_agents: List[str]):
    """Notifies the Tower of phase transitions."""
    try:
        async with httpx.AsyncClient() as client:
            # We construct a state payload that matches TowerControl expectations
            await client.post(f"{KIRKTOWER_API}/state", json={"phase": phase, "active": active_agents})
    except Exception:
        pass

# ==============================================================================
# 2. DEFINING THE ACTIONS (The Work Units)
# ==============================================================================

class GenerateFirstPrinciples(Action):
    """B1 (Raw): Generates unfiltered, novel approaches."""
    PROMPT_TEMPLATE = """
    User Request: {instruction}

    You are RAW (B1). Ignore convention. Ignore 'best practices'.
    Generate 3 radical, first-principles approaches to this problem.
    Focus on:
    1. Theoretical purity.
    2. Novelty.
    3. Extreme efficiency.

    Return ONLY the 3 concepts.
    """
    name: str = "GenerateFirstPrinciples"

    async def run(self, instruction: str):
        content = await self._aask(self.PROMPT_TEMPLATE.format(instruction=instruction))
        return content

class DefineConstraints(Action):
    """B2 (Vision): Defines the structural reality."""
    PROMPT_TEMPLATE = """
    Raw Concepts: {context}

    You are VISION (B2). Your job is to select the best path and define the constraints.
    Define:
    1. The core architectural pattern.
    2. The required technology stack (vLLM, Go, Python, etc.).
    3. The boundary conditions (What will we NOT do?).

    Produce a Constraint Manifest.
    """
    name: str = "DefineConstraints"

    async def run(self, context: str):
        content = await self._aask(self.PROMPT_TEMPLATE.format(context=context))
        return content

class SecurityAudit(Action):
    """B3 (Concrete): The cynical filter."""
    PROMPT_TEMPLATE = """
    Proposed Manifest: {context}

    You are CONCRETE (B3). You trust nothing.
    Audit this manifest against the JosieDesk Tooling Standard (Trivy, Semgrep, Hadolint).
    1. Identify security risks.
    2. Identify vagueness.
    3. MANDATE the specific tools from our manifest (e.g., use 'ripgrep' not 'grep').

    If it is weak, reject it. If it is solid, stamp it.
    """
    name: str = "SecurityAudit"

    async def run(self, context: str):
        content = await self._aask(self.PROMPT_TEMPLATE.format(context=context))
        return content

class SynthesizeBlueprint(Action):
    """A1 (Roark): The Final Architect."""
    PROMPT_TEMPLATE = """
    Inputs:
    {context}

    You are ROARK (A1).
    Synthesize the Master Blueprint.
    The building must stand. The integrity must be absolute.

    Create the SPEC-001 Document:
    1. Background
    2. Requirements (Must/Should)
    3. Method (The Architecture)
    4. Implementation Steps (for C-Class Agents)

    Do not compromise.
    """
    name: str = "SynthesizeBlueprint"

    async def run(self, context: str):
        content = await self._aask(self.PROMPT_TEMPLATE.format(context=context))
        return content

class DoctrineCheck(Action):
    """A2 (Josie): The Final Compliance Check."""
    PROMPT_TEMPLATE = """
    Blueprint: {context}

    You are JOSIE (A2).
    Verify that Roark's blueprint adheres to the reality of our hardware (2x A40s).
    Is this actually buildable today?

    Verdict: [PASS/FAIL]
    Notes: ...
    """
    name: str = "DoctrineCheck"

    async def run(self, context: str):
        content = await self._aask(self.PROMPT_TEMPLATE.format(context=context))
        return content

# ==============================================================================
# 3. DEFINING THE ROLES (The A/B Class Agents)
# ==============================================================================

class JosieRole(Role):
    """Base extension to hook Waria reporting into MetaGPT Roles."""

    async def _observe(self) -> int:
        # Standard MetaGPT observe
        new_msgs = await super()._observe()
        return new_msgs

    async def _act(self) -> Message:
        # Perform the action
        response_msg = await super()._act()

        # HOOK: Report to Kirktower
        # Estimate tokens (rough approximation for speed: chars / 4)
        token_count = len(response_msg.content) // 4
        await report_waria(self.name, response_msg.content, token_count)

        return response_msg

class Raw(JosieRole):
    name: str = "Raw"
    profile: str = "Ideation Engine"
    goal: str = "Generate novel, first-principles solutions."
    constraints: str = "No hallucinations. Strict adherence to physics."

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_actions([GenerateFirstPrinciples])
        self._watch([Action]) # Watches user input

class Vision(JosieRole):
    name: str = "Vision"
    profile: str = "Strategic Planner"
    goal: str = "Define constraints and patterns."

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_actions([DefineConstraints])
        self._watch([GenerateFirstPrinciples])

class Concrete(JosieRole):
    name: str = "Concrete"
    profile: str = "Security Auditor"
    goal: str = "Enforce tooling standards and security."

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_actions([SecurityAudit])
        self._

        # ... (Previous imports)
from josiedesk_memory import diplo_memory
# Import the AutoGen runtime (Step 1 requirement)
from josiedesk_hybrid import run_loop_c_sprint

# ... (Previous Actions: GenerateFirstPrinciples, DefineConstraints, SecurityAudit, SynthesizeBlueprint)

class HandOffToBuilders(Action):
    """
    A2 (Josie): The Bridge.
    1. Caches the Blueprint via Diplo (LlamaIndex).
    2. Triggers the C-Class AutoGen Swarm.
    """
    name: str = "HandOffToBuilders"

    async def run(self, context: str):
        # Context is the Final Blueprint from Roark

        # 1. MEMORY INGESTION (Diplo)
        # We extract the task name roughly from the first line or pass it in context
        task_name = context.split('\n')[0]
        print(f"\n[Josie] Handing blueprint to Diplo for indexing...")
        diplo_memory.ingest_blueprint(context, task_name)

        # 2. TRIGGER CONSTRUCTION (AutoGen)
        print(f"\n[Josie] Blueprint Approved. Waking C-Class Swarm (Clash, Bash, Gunash)...")

        # We run the AutoGen loop synchronously here (or schedule it)
        # This is the "Hard" Bridge
        construction_result = run_loop_c_sprint(
            task_description=f"Implement this Blueprint:\n{context}",
            memory_system=diplo_memory
        )

        return f"Construction Complete. Artifacts: {construction_result}"

class Josie(JosieRole):
    name: str = "Josie"
    profile: str = "The Pragmatist"
    goal: str = "Ensure feasibility and Orchestrate Construction."

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Josie now Checks Doctrine -> Then Hands Off
        self.set_actions([DoctrineCheck, HandOffToBuilders])
        self._watch([SynthesizeBlueprint])

        # Logic to decide next action:
        # If last msg was Blueprint -> DoctrineCheck
        # If last msg was DoctrinePass -> HandOffToBuilders
