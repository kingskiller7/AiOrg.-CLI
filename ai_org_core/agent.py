import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field
import json

from .persona import Persona
from .knowledge import KnowledgeBase
from .task import Task

load_dotenv()

# Pydantic models for structured LLM output
class Delegation(BaseModel):
    recipient_role: str = Field(description="The role of the agent to delegate the task to.")
    new_task_description: str = Field(description="A new, specific task description for the subordinate.")

class FinalAnswer(BaseModel):
    response: str = Field(description="The final, complete answer to the task.")

class AgentAction(BaseModel):
    action: str = Field(description="Either 'delegate' or 'execute'.")
    details: Delegation | FinalAnswer

class AIAgent:
    """Represents a custom AI agent that can execute or delegate tasks."""
    def __init__(self, persona: Persona, organization=None):
        self.persona = persona
        self.organization = organization
        self.knowledge = KnowledgeBase(agent_role=persona.role)
        
        api_key = os.getenv("GEMINI_API_KEY")
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
        prompt = f"""
        You are an AI agent, **{self.persona.role}**, within a larger organization.

        **Your Persona:**
        - Responsibilities: {', '.join(self.persona.responsibilities)}
        - Core Views: {', '.join(self.persona.views)}

        **Organizational Context:**
        - The task was delegated to you by: **{delegator_role}**.
        - Your direct subordinates are: **{subordinate_roles}**.
        - Task History (Chain of Command): {' -> '.join(task.history)}

        **Your Task:**
        - Description: {task.description}
        - Expected Output: {task.expected_output}

        **Your Decision:**
        Based on the task and your role, you must decide on one of two actions:
        1. **delegate**: If the task is too broad for you and is better suited for one of your subordinates, delegate it. Choose the best subordinate and write a new, more specific task description for them.
        2. **execute**: If the task is within your direct responsibilities and you can complete it yourself, provide the final, complete response.

        You must format your response as a JSON object matching the required schema.
        """
        return prompt

    def execute_task(self, task: Task, delegator=None) -> AgentAction:
        delegator_role = delegator.persona.role if delegator else "The User"
        task.history.append(self.persona.role)
        print(f"[{self.persona.role}] received task '{task.description}' from [{delegator_role}].")

        prompt = self._create_prompt(task, delegator_role)

        print(f"[{self.persona.role}] is thinking...")
        response = self.llm.invoke(prompt)

        if response.action == 'execute':
            self.knowledge.add(f"Completed task '{task.description}' with result: {response.details.response[:100]}...")
            print(f"[{self.persona.role}] has executed the task.")
        else:
            print(f"[{self.persona.role}] has decided to delegate the task to [{response.details.recipient_role}].")
        
        return response
