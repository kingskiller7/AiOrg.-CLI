from typing import Dict
from .agent import AIAgent
from .task import Task

class Organization:
    """The main orchestrator that manages the workflow of the AI organization."""
    def __init__(self, structure: Dict[str, AIAgent]):
        self.structure = structure
        self.ceo = self.structure.get("CEO")
        if not self.ceo:
            raise ValueError("An Organization must have a CEO.")

    def kickoff(self, task: Task):
        print("--- Organization Task Kickoff ---")
        # Find the initial agent to assign the task to
        initial_agent = self.structure.get(task.assigned_to)
        if not initial_agent:
            print(f"No agent found for role: {task.assigned_to}. Assigning to CEO.")
            initial_agent = self.ceo
        
        result = initial_agent.execute_task(task)
        print("--- Organization Task Complete ---")
        return result
