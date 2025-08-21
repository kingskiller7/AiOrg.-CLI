from typing import Dict, List
from .agent import AIAgent
from .task import Task

class Organization:
    """The main orchestrator that manages the full, hierarchical workflow."""
    def __init__(self, structure: Dict[str, Dict]):
        self.agents: Dict[str, AIAgent] = {}
        self.hierarchy: Dict[str, List[str]] = {}

        for role, details in structure.items():
            self.agents[role] = AIAgent(persona=details["persona"], organization=self)
            self.hierarchy[role] = details.get("subordinates", [])

        self.ceo = self.agents.get("CEO")
        if not self.ceo:
            raise ValueError("An Organization must have a CEO.")

    def get_subordinates(self, role: str) -> List[str]:
        return self.hierarchy.get(role, [])

    def get_manager(self, role: str) -> str | None:
        for manager, subordinates in self.hierarchy.items():
            if role in subordinates:
                return manager
        return None

    def kickoff(self, task: Task, max_delegations: int = 10) -> str:
        print("--- Organization Task Kickoff ---")
        
        current_agent = self.agents.get(task.assigned_to)
        if not current_agent:
            print(f"No agent found for role: {task.assigned_to}. Assigning to CEO.")
            current_agent = self.ceo

        for i in range(max_delegations):
            action_result = current_agent.execute_task(task, current_agent)

            if action_result.action == 'execute':
                final_response = action_result.details.response
                manager_role = self.get_manager(current_agent.persona.role)
                
                # If the agent has no manager (i.e., it's the CEO), the work is done.
                if not manager_role:
                    print("--- Organization Task Complete (CEO Finalized) ---")
                    return final_response
                
                # --- Upward Reporting Logic ---
                print(f"[{current_agent.persona.role}] is reporting results to manager [{manager_role}].")
                # Formulate a new task for the manager to review the subordinate's work
                task = Task(
                    description=f"Your subordinate, {current_agent.persona.role}, has completed their assigned task. Their report is below. Please review, consolidate it with any other information, and decide on the next action to fulfill our original goal: '{task.description}'\n\nSUBORDINATE'S REPORT:\n---\n{final_response}",
                    expected_output=task.expected_output,
                    assigned_to=manager_role,
                    history=task.history
                )
                current_agent = self.agents.get(manager_role)
            
            elif action_result.action == 'delegate':
                recipient_role = action_result.details.recipient_role
                next_agent = self.agents.get(recipient_role)
                
                if not next_agent:
                    return f"Error: Agent {current_agent.persona.role} tried to delegate to non-existent role {recipient_role}."
                
                task.description = action_result.details.new_task_description
                current_agent = next_agent

            elif action_result.action == 'use_tool':
                tool_name = action_result.details.tool_name
                method_name = action_result.details.method
                arguments = action_result.details.arguments
                
                tool = current_agent.tools.get(tool_name)
                if not tool:
                    return f"Error: Agent {current_agent.persona.role} tried to use a non-existent tool: {tool_name}"
                
                method = getattr(tool, method_name, None)
                if not method:
                    return f"Error: Tool '{tool_name}' does not have a method '{method_name}'"

                try:
                    tool_result = method(**arguments)
                except TypeError as e:
                    return f"Error: Invalid arguments for {tool_name}.{method_name}: {e}"

                task.description = f"You just used the {tool_name} tool by calling the '{method_name}' method. The result was: \n\n{tool_result}\n\nNow, using this new information, complete your original task: {task.description}"
            else:
                return f"Error: Unknown action '{action_result.action}' decided by agent."

        return "Error: Maximum delegation depth reached. The task could not be completed."