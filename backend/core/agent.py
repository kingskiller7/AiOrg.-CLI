import os
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field
from typing import List, Dict
import json

from .persona import Persona
from .knowledge import KnowledgeBase
from .task import Task
from .tools import browser_tool, code_executor_tool, file_system_tool
from .text_to_image_tool import text_to_image
from .image_to_video_tool import image_to_video



# --- Pydantic models for structured LLM output ---
class Delegation(BaseModel):
    recipient_role: str = Field(description="The role of the agent to delegate the task to.")
    new_task_description: str = Field(description="A new, specific task description for the subordinate.")

class UseTool(BaseModel):
    tool_name: str = Field(description="The name of the tool to use, e.g., 'browser' or 'code_executor'.")
    method: str = Field(description="The method of the tool to call, e.g., 'browse_and_scrape' or 'write_code'.")
    arguments: Dict[str, str] = Field(description=("""The arguments for the tool method, e.g., {'url': 'https://example.com'} or {'filename': 'script.py', 'code': 'print("Hello")'}."""))

class FinalAnswer(BaseModel):
    response: str = Field(description="The final, complete answer to the task.")

class AgentAction(BaseModel):
    plan: List[str] = Field(description="A step-by-step plan of what the agent intends to do.")
    action: str = Field(description="Either 'delegate', 'use_tool', or 'execute'.")
    details: Delegation | UseTool | FinalAnswer

class AIAgent:
    """Represents a custom AI agent that can execute, delegate, or use tools."""
    def __init__(self, persona: Persona, organization=None, all_tools=None):
        self.persona = persona
        self.organization = organization
        self.knowledge = KnowledgeBase(agent_role=persona.role)
        
        if all_tools is None:
            all_tools = {
                "browser": browser_tool,
                "code_executor": code_executor_tool,
                "file_system": file_system_tool,
                "text_to_image": text_to_image,
                "image_to_video": image_to_video,
            }
        self.tools = all_tools
        
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
                        api_key = value.strip().strip("'"")
                        break

        if not api_key or api_key == "YOUR_API_KEY_HERE":
            raise ValueError("GEMINI_API_KEY not found or not set in .env file.")
        
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            verbose=True,
            temperature=0.7,
            google_api_key=api_key,
        ).with_structured_output(AgentAction)

    def __repr__(self):
        return f"AIAgent(role={self.persona.role})"

    def _create_prompt(self, task: Task, delegator_role: str) -> str:
        subordinate_roles = ", ".join(self.organization.get_subordinates(self.persona.role)) or "None"
        available_abilities = ", ".join(self.persona.abilities) or "None"
        
        relevant_experience = self.knowledge.query(task.description)

        prompt = f"""
        You are an AI agent, **{self.persona.role}**, within a larger organization.

        **Your Persona:**
        - Responsibilities: {', '.join(self.persona.responsibilities)}
        - Your Abilities: **{available_abilities}**

        **Relevant Past Experience (from your memory):**
        {relevant_experience}

        **Organizational Context:**
        - The task was delegated to you by: **{delegator_role}**.
        - Your direct subordinates are: **{subordinate_roles}**.
        - Task History (Chain of Command): {' -> '.join(task.history)}

        **Your Task:**
        - Description: {task.description}
        - Expected Output: {task.expected_output}

        **Your Decision Process:**
        1. First, think step-by-step. Formulate a plan to address the task.
        2. Based on the first step of your plan, decide on your immediate next action.
        3. You have three possible actions: `delegate`, `use_tool`, or `execute`.

        **Tool Usage Guide:**
        - To create a new, permanent ability, use the 'tool_forge' tool with the 'create_tool' method. You must provide a unique 'tool_name', a clear 'description', and the complete Python 'code' for the new tool.
        - To search the web, use the 'browser' tool with the 'browse_and_scrape' method by formulating a search engine URL.
        - For file system operations, use the 'file_system' tool with methods like 'list_directory', 'read_file', and 'write_file'.
        - For code-related tasks, use the 'code_executor' tool with methods like 'lint_code', 'write_code', and 'execute_code'.

        You must format your response as a JSON object matching the required schema, including your plan and your chosen next action.
        """
        return prompt

    def execute_task(self, task: Task, delegator=None) -> AgentAction:
        delegator_role = delegator.persona.role if delegator else "The User"
        if self.persona.role not in task.history:
            task.history.append(self.persona.role)
        print(f"[{self.persona.role}] received task '{task.description}' from [{delegator_role}].")

        prompt = self._create_prompt(task, delegator_role)

        print(f"[{self.persona.role}] is thinking...")
        response = self.llm.invoke(prompt)

        # Print the agent's plan
        if response.plan:
            print(f"[{self.persona.role}] has formulated a plan:")
            for i, step in enumerate(response.plan, 1):
                print(f"  Step {i}: {step}")

        if response.action == 'execute':
            self.knowledge.add(f"Completed task '{task.description}' with result: {response.details.response[:100]}...")
            print(f"[{self.persona.role}] has executed the task.")
        elif response.action == 'delegate':
            print(f"[{self.persona.role}] has decided to delegate the task to [{response.details.recipient_role}].")
        elif response.action == 'use_tool':
            print(f"[{self.persona.role}] has decided to use the '{response.details.tool_name}' tool.")
        
        return response