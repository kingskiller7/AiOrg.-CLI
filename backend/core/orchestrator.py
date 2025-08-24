from typing import Dict, List
from .agent import AIAgent, Delegation, FinalAnswer, UseTool
from .task import Task
from .persona import Persona
from .tools import browser_tool, code_executor_tool, file_system_tool, tool_forge, file_processing_tool
from sentence_transformers import SentenceTransformer, util

class Organization:
    """The main orchestrator that manages the full, hierarchical workflow and dynamic tools."""
    def __init__(self, structure: Dict[str, Dict]):
        self.agents: Dict[str, AIAgent] = {}
        self.hierarchy: Dict[str, List[str]] = {}
        self.similarity_model = SentenceTransformer('all-MiniLM-L6-v2')

        # Load all available tools
        self.tool_forge = tool_forge
        custom_tools = self.tool_forge.load_custom_tools()
        self.available_tools = {
            "browser": browser_tool,
            "code_executor": code_executor_tool,
            "file_system": file_system_tool,
            "tool_forge": self.tool_forge,
            "file_processing": file_processing_tool,
            **custom_tools
        }

        # Create all agent instances and provide them with the full toolset
        for role, details in structure.items():
            self.add_agent(details["persona"])
            self.hierarchy[role] = details.get("subordinates", [])

        self.ceo = self.agents.get("CEO")
        if not self.ceo:
            raise ValueError("An Organization must have a CEO.")

    def add_agent(self, persona: Persona):
        """Adds a new agent to the organization."""
        new_agent = AIAgent(
            persona=persona,
            organization=self
        )
        self.agents[persona.role] = new_agent

    def get_subordinates(self, role: str) -> List[str]:
        return self.hierarchy.get(role, [])

    def get_manager(self, role: str) -> str | None:
        for manager, subordinates in self.hierarchy.items():
            if role in subordinates:
                return manager
        return None

    def kickoff(self, task: Task, max_delegations: int = 10) -> str:
        print("--- Organization Task Kickoff ---")
        
        # Find the best agent for the task
        best_agent = None
        best_similarity = -1
        
        for agent in self.agents.values():
            similarity = self._calculate_similarity(task.description, agent.persona.responsibilities)
            if similarity > best_similarity:
                best_similarity = similarity
                best_agent = agent
        
        if best_agent and best_similarity > 0.5:
            current_agent = best_agent
            print(f"Task assigned to {current_agent.persona.role} based on role similarity.")
        else:
            current_agent = self.ceo
            task.description = f"The following task could not be assigned to any existing agent: '{task.description}'. Please delegate to the CHRO to create a new agent for this task, or handle it yourself if it is within your capabilities."

        for i in range(max_delegations):
            action_result = current_agent.execute_task(task, current_agent)

            if action_result.action == 'execute':
                if isinstance(action_result.details, FinalAnswer):
                    final_response = action_result.details.response
                    manager_role = self.get_manager(current_agent.persona.role)
                    
                    if not manager_role:
                        print("--- Organization Task Complete (CEO Finalized) ---")
                        return final_response
                    
                    print(f"[{current_agent.persona.role}] is reporting results to manager [{manager_role}].")
                    task = Task(
                        description=f"Your subordinate, {current_agent.persona.role}, has completed their assigned task. Their report is below. Please review and decide the next action. Original goal: '{task.description}'\n\nSUBORDINATE'S REPORT:\n---\n{final_response}",
                        expected_output=task.expected_output,
                        assigned_to=manager_role,
                        history=task.history
                    )
                    current_agent = self.agents.get(manager_role)
                else:
                    return f"Error: Agent {current_agent.persona.role} tried to execute but provided invalid details."
            
            elif action_result.action == 'delegate':
                if isinstance(action_result.details, Delegation):
                    recipient_role = action_result.details.recipient_role
                    next_agent = self.agents.get(recipient_role)
                    
                    if not next_agent:
                        return f"Error: Agent {current_agent.persona.role} tried to delegate to non-existent role {recipient_role}."
                    
                    task.description = action_result.details.new_task_description
                    current_agent = next_agent
                else:
                    return f"Error: Agent {current_agent.persona.role} tried to delegate but provided invalid details."

            elif action_result.action == 'use_tool':
                if isinstance(action_result.details, UseTool):
                    tool_name = action_result.details.tool_name
                    method_name = action_result.details.method
                    arguments = action_result.details.arguments
                    
                    # Add the organization instance to the arguments if the tool needs it
                    if tool_name in ["tool_management", "agent_management"]:
                        arguments["organization"] = self

                    tool = self.available_tools.get(tool_name)
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
                    return f"Error: Agent {current_agent.persona.role} tried to use a tool but provided invalid details."
            else:
                return f"Error: Unknown action '{action_result.action}' decided by agent."

        return "Error: Maximum delegation depth reached. The task could not be completed."

    def _calculate_similarity(self, text1: str, text2: list[str]) -> float:
        """Calculates the similarity between a text and a list of texts."""
        embedding1 = self.similarity_model.encode(text1, convert_to_tensor=True)
        embedding2 = self.similarity_model.encode(text2, convert_to_tensor=True)
        
        cosine_scores = util.pytorch_cos_sim(embedding1, embedding2)
        
        return cosine_scores.max().item()