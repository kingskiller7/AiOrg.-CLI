from .persona import Persona
from .knowledge import KnowledgeBase

class AIAgent:
    """Represents a custom AI agent within the organization."""
    def __init__(self, persona: Persona):
        self.persona = persona
        self.knowledge = KnowledgeBase(agent_role=persona.role)
        # TODO: Add LLM and tool integrations

    def __repr__(self):
        return f"AIAgent(role={self.persona.role})"

    def execute_task(self, task, delegator=None):
        print(f"[{self.persona.role}] is executing task: '{task.description}' delegated by [{delegator.persona.role if delegator else 'Origin'}]")
        # Future logic for task execution will go here
        result = f"Task '{task.description}' completed by {self.persona.role}."
        self.knowledge.add(f"Successfully completed task: {task.description}")
        return result
