import os
import json
from typing import Dict, List
from langchain_google_genai import ChatGoogleGenerativeAI
from sentence_transformers import SentenceTransformer, util

from .agent import AIAgent, AgentAction, Delegation, FinalAnswer, UseTool, RequestRevision
from .task import Task
from .persona import Persona
from .tools import browser_tool, code_executor_tool, file_system_tool, tool_forge, file_processing_tool

class Organization:
    """The main orchestrator that manages the full, hierarchical workflow and dynamic tools."""
    def __init__(self, structure: Dict[str, Dict]):
        self.agents: Dict[str, AIAgent] = {}
        self.hierarchy: Dict[str, List[str]] = {}
        self.similarity_model = SentenceTransformer('all-MiniLM-L6-v2')

        # Manually load the .env file from the backend directory
        backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        env_path = os.path.join(backend_dir, '.env')
        api_key = None
        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and line.startswith('GEMINI_API_KEY'):
                        key, value = line.split('=', 1)
                        api_key = value.strip().strip("'\"")
                        break

        if not api_key or api_key == "YOUR_API_KEY_HERE":
            raise ValueError("GEMINI_API_KEY not found or not set in .env file.")
        
        # Create a single, shared LLM instance
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            verbose=True,
            temperature=0,
            google_api_key=api_key,
        )

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
            organization=self,
            llm=self.llm
        )
        self.agents[persona.role] = new_agent

    def get_subordinates(self, role: str) -> List[str]:
        return self.hierarchy.get(role, [])

    def get_manager(self, role: str) -> str | None:
        for manager, subordinates in self.hierarchy.items():
            if role in subordinates:
                return manager
        return None

    def _determine_workflow(self, task_description: str) -> str:
        """Determines the primary department for a task based on keywords."""
        tech_keywords = ['code', 'script', 'develop', 'software', 'technical', 'database', 'server', 'bug']
        marketing_keywords = ['marketing', 'campaign', 'brand', 'advertising', 'social media', 'seo']
        security_keywords = ['security', 'vulnerability', 'penetration test', 'firewall', 'malware']
        finance_keywords = ['financial', 'budget', 'forecast', 'revenue', 'expense']

        description = task_description.lower()
        if any(keyword in description for keyword in tech_keywords):
            return "CTO"
        if any(keyword in description for keyword in marketing_keywords):
            return "CMO"
        if any(keyword in description for keyword in security_keywords):
            return "CSO"
        if any(keyword in description for keyword in finance_keywords):
            return "CFO"
        
        return "CEO" # Default to CEO if no specific department is identified

    def kickoff(self, task: Task, max_delegations: int = 10) -> str:
        print("--- Organization Task Kickoff ---")
        
        # Set the original description if it's not already set
        if task.original_description is None:
            task.original_description = task.description

        # Determine the initial agent based on the strategic workflow
        initial_agent_role = self._determine_workflow(task.description)
        current_agent = self.agents.get(initial_agent_role)
        print(f"Task initially routed to {current_agent.persona.role} based on strategic workflow analysis.")

        for i in range(max_delegations):
            action_result = current_agent.execute_task(task, current_agent)
            action_details = action_result.details

            if action_details.action == 'execute':
                if isinstance(action_details, FinalAnswer):
                    final_response = action_details.response
                    if isinstance(final_response, dict):
                        final_response = json.dumps(final_response, indent=2)
                    manager_role = self.get_manager(current_agent.persona.role)
                    
                    if not manager_role:
                        print("--- Organization Task Complete (CEO Finalized) ---")
                        return final_response
                    
                    # Append the report to the history and create a clean task for the manager
                    task.action_history.append(f"SUBORDINATE'S REPORT from {current_agent.persona.role}:\n---\n{final_response}")
                    task.description = f"Your subordinate, {current_agent.persona.role}, has completed their assigned task. Their report is in the action history. Please review their work and decide the next action to progress the original goal: '{task.original_description}'."
                    task.assigned_to = manager_role
                    current_agent = self.agents.get(manager_role)
                else:
                    return f"Error: Agent {current_agent.persona.role} tried to execute but provided invalid details."
            
            elif action_details.action == 'delegate':
                if isinstance(action_details, Delegation):
                    recipient_role = action_details.recipient
                    next_agent = self.agents.get(recipient_role)
                    
                    if not next_agent:
                        return f"Error: Agent {current_agent.persona.role} tried to delegate to non-existent role {recipient_role}."
                    
                    task.description = action_details.task_description
                    task.assigned_to = recipient_role
                    current_agent = next_agent
                else:
                    return f"Error: Agent {current_agent.persona.role} tried to delegate but provided invalid details."

            elif action_details.action == 'request_revision':
                if isinstance(action_details, RequestRevision):
                    recipient_role = action_details.subordinate_to_revise
                    next_agent = self.agents.get(recipient_role)
                    
                    if not next_agent:
                        return f"Error: Agent {current_agent.persona.role} tried to request a revision from a non-existent role {recipient_role}."
                    
                    # Append feedback to history and create a clean task for the subordinate
                    task.action_history.append(f"MANAGER'S FEEDBACK from {current_agent.persona.role}:\n---\n{action_details.revision_feedback}")
                    task.description = f"Your manager, {current_agent.persona.role}, has requested revisions for your work on the task: '{task.original_description}'. See the action history for their feedback and provide a new, complete response."
                    task.assigned_to = recipient_role
                    current_agent = next_agent
                else:
                    return f"Error: Agent {current_agent.persona.role} tried to request a revision but provided invalid details."

            elif action_details.action == 'use_tool':
                if isinstance(action_details, UseTool):
                    tool_name = action_details.tool_name
                    method_name = action_details.method
                    arguments = action_details.arguments
                    for key, value in arguments.items():
                        if not isinstance(value, str):
                            arguments[key] = str(value)

                    # Enforce agent abilities
                    if tool_name not in current_agent.persona.abilities:
                        rejection_reason = f"Attempt to use tool '{tool_name}' failed. It is not in your list of abilities."
                        task.description = f"Your attempt to use the '{tool_name}' tool failed because it is not in your list of abilities. You must formally request this ability from the CEO. Formulate a new task for the CEO explaining your role, the ability you need, and why you need it for your original task: '{task.original_description}'. Then, use the 'delegate' action to send this request to the CEO."
                        task.action_history.append(rejection_reason)
                        continue # End this turn and let the agent formulate the request

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
                        tool_result_json = method(**arguments)
                        tool_result = json.loads(tool_result_json)
                    except TypeError as e:
                        return f"Error: Invalid arguments for {tool_name}.{method_name}: {e}"
                    except json.JSONDecodeError as e:
                        return f"Error: Tool {tool_name}.{method_name} returned invalid JSON: {e}"

                    tool_output_string = f"The {tool_name} tool was used by calling '{method_name}'. The result was: {tool_result}"
                    task.action_history.append(tool_output_string)
                else:
                    return f"Error: Agent {current_agent.persona.role} tried to use a tool but provided invalid details."
            else:
                return f"Error: Unknown action '{action_details.action}' decided by agent."

        return "Error: Maximum delegation depth reached. The task could not be completed."

    def _calculate_similarity(self, text1: str, text2: list[str]) -> float:
        """Calculates the similarity between a text and a list of texts."""
        embedding1 = self.similarity_model.encode(text1, convert_to_tensor=True)
        embedding2 = self.similarity_model.encode(text2, convert_to_tensor=True)
        
        cosine_scores = util.pytorch_cos_sim(embedding1, embedding2)
        
        return cosine_scores.max().item()