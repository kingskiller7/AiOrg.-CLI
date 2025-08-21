import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

from .persona import Persona
from .knowledge import KnowledgeBase
from .task import Task

# Load environment variables from .env file
load_dotenv()

class AIAgent:
    """Represents a custom AI agent within the organization, powered by an LLM."""
    def __init__(self, persona: Persona):
        self.persona = persona
        self.knowledge = KnowledgeBase(agent_role=persona.role)
        
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key or api_key == "YOUR_API_KEY_HERE":
            raise ValueError("GEMINI_API_KEY not found or not set in .env file.")
        
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            verbose=True,
            temperature=0.7,
            google_api_key=api_key,
        )

    def __repr__(self):
        return f"AIAgent(role={self.persona.role})"

    def _create_prompt(self, task: Task, delegator_role: str) -> str:
        """Creates a detailed, persona-driven prompt for the LLM."""
        prompt = f"""
        You are an AI agent within a larger organization.
        
        **Your Persona:**
        - Role: {self.persona.role}
        - Responsibilities: {', '.join(self.persona.responsibilities)}
        - Core Views: {', '.join(self.persona.views)}

        **Your Task:**
        This task was delegated to you by the **{delegator_role}**.
        - Task Description: {task.description}
        - Expected Output: {task.expected_output}

        **Instructions:**
        1. Fulfill the task to the best of your ability, adhering strictly to your role and persona.
        2. Your response should be a direct and complete execution of the expected output.
        3. Do not explain your actions, just provide the final output.
        """
        return prompt

    def execute_task(self, task: Task, delegator=None) -> str:
        """Executes a task using the agent's persona and the LLM."""
        delegator_role = delegator.persona.role if delegator else "The User"
        print(f"[{self.persona.role}] received task '{task.description}' from [{delegator_role}].")

        # 1. Create a prompt based on the persona and task
        prompt = self._create_prompt(task, delegator_role)

        # 2. Invoke the LLM with the prompt
        print(f"[{self.persona.role}] is thinking...")
        response = self.llm.invoke(prompt)
        result = response.content

        # 3. Learn from the experience
        self.knowledge.add(f"Completed task '{task.description}' with result: {result[:100]}...")

        print(f"[{self.persona.role}] has completed the task.")
        return result