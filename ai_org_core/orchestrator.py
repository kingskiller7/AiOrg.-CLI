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
                
                task.description = action_result.details.new_task_description
                current_agent = next_agent

            elif action_result.action == 'use_tool':
                tool_name = action_result.details.tool_name
                tool_argument = action_result.details.argument
                
                tool = current_agent.tools.get(tool_name)
                if not tool:
                    return f"Error: Agent {current_agent.persona.role} tried to use a non-existent tool: {tool_name}"
                
                # For now, we only have the browser tool with one method
                if tool_name == "browser":
                    tool_result = tool.browse_and_scrape(tool_argument)
                else:
                    return f"Error: Unknown tool method for {tool_name}"

                # The task description is updated with the result, and given back to the same agent
                task.description = f"You just used the {tool_name} tool with the argument '{tool_argument}'. The result was: \n\n{tool_result}\n\nNow, using this new information, complete your original task: {task.description}"
                # The current_agent remains the same for the next loop iteration
            else:
                return f"Error: Unknown action '{action_result.action}' decided by agent."

        return "Error: Maximum delegation depth reached. The task could not be completed."