from typing import Dict, List
from .agent import AIAgent, AgentAction
from .task import Task

class Organization:
    """The main orchestrator that manages the delegation workflow."""
    def __init__(self, structure: Dict[str, Dict]):
        self.agents: Dict[str, AIAgent] = {}
        self.hierarchy: Dict[str, List[str]] = {}

        # First, create all agent instances
        for role, details in structure.items():
            self.agents[role] = AIAgent(persona=details["persona"], organization=self)
            self.hierarchy[role] = details.get("subordinates", [])

        self.ceo = self.agents.get("CEO")
        if not self.ceo:
            raise ValueError("An Organization must have a CEO.")

    def get_subordinates(self, role: str) -> List[str]:
        return self.hierarchy.get(role, [])

    def kickoff(self, task: Task, max_delegations: int = 5) -> str:
        print("--- Organization Task Kickoff ---")
        
        current_agent = self.agents.get(task.assigned_to)
        if not current_agent:
            print(f"No agent found for role: {task.assigned_to}. Assigning to CEO.")
            current_agent = self.ceo

        for i in range(max_delegations):
            action_result = current_agent.execute_task(task, current_agent)

            if action_result.action == 'execute':
                final_response = action_result.details.response
                print("--- Organization Task Complete ---")
                return final_response
            
            elif action_result.action == 'delegate':
                recipient_role = action_result.details.recipient_role
                next_agent = self.agents.get(recipient_role)
                
                if not next_agent:
                    return f"Error: Agent {current_agent.persona.role} tried to delegate to non-existent role {recipient_role}."
                
                # Create the new sub-task
                task = Task(
                    description=action_result.details.new_task_description,
                    expected_output=task.expected_output, # The final output expectation remains the same
                    assigned_to=recipient_role,
                    history=task.history # Pass the history along
                )
                current_agent = next_agent
            else:
                return f"Error: Unknown action '{action_result.action}' decided by agent."

        return "Error: Maximum delegation depth reached. The task could not be completed."