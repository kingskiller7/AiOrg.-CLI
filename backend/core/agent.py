import os
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field, ValidationError
from typing import List, Dict, Union, Literal
import json
import re

from .persona import Persona
from .knowledge import KnowledgeBase
from .task import Task
from .tools import browser_tool, code_executor_tool, file_system_tool
from .text_to_image_tool import text_to_image
from .image_to_video_tool import image_to_video
from .text_to_speech_tool import text_to_speech
from .text_to_video_tool import text_to_video

class Delegation(BaseModel):
    action: Literal["delegate"] = "delegate"
    recipient: str = Field(description="The role of the agent to delegate the task to.")
    task_description: str = Field(description="A new, specific task description for the subordinate.")

class UseTool(BaseModel):
    action: Literal["use_tool"] = "use_tool"
    tool_name: str = Field(description="The name of the tool to use.")
    method: str = Field(description="The method of the tool to call.")
    arguments: Dict[str, str] = Field(description="The arguments for the tool method.")

class FinalAnswer(BaseModel):
    action: Literal["execute"] = "execute"
    response: str = Field(description="The final, complete answer to the task.")

class RequestRevision(BaseModel):
    action: Literal["request_revision"] = "request_revision"
    subordinate_to_revise: str = Field(description="The role of the subordinate to whom the task is being sent back for revision.")
    revision_feedback: str = Field(description="Constructive feedback and explicit instructions for what needs to be revised.")

class AgentAction(BaseModel):
    plan: List[str] = Field(description="A step-by-step plan of what the agent intends to do.")
    details: Union[Delegation, UseTool, FinalAnswer, RequestRevision] = Field(..., discriminator="action")

class AIAgent:
    """Represents a custom AI agent that can execute, delegate, or use tools."""
    def __init__(self, persona: Persona, organization=None, llm=None):
        self.persona = persona
        self.organization = organization
        self.knowledge = KnowledgeBase(agent_role=persona.role)
        self.tools = {}
        self.llm = llm

    def __repr__(self):
        return f"AIAgent(role={self.persona.role})"

    def _clean_json_output(self, raw_output: str) -> str:
        """Cleans the raw string output from the LLM to extract a valid JSON object."""
        # Use regex to find the JSON block within markdown fences
        match = re.search(r"```json\n(.*?)\n```", raw_output, re.DOTALL)
        if match:
            return match.group(1).strip()
        # Fallback for cases where the fences are missing
        return raw_output.strip()

    def _create_prompt(self, task: Task, delegator_role: str) -> str:
        subordinate_roles = ", ".join(self.organization.get_subordinates(self.persona.role)) or "None"
        available_abilities = ", ".join(self.persona.abilities) or "None"
        
        relevant_experience = self.knowledge.query(task.description)
        action_history = "\n".join(f"- {item}" for item in task.action_history) or "No actions taken yet."

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
        - Delegation History (Chain of Command): {" -> ".join(task.history)}

        **Action History:**
        {action_history}

        **Your Task:**
        - Description: {task.description}
        - Expected Output: {task.expected_output}

        **Your Decision Process:**
        1. Formulate a step-by-step plan.
        2. Choose your single next action from the Action Reference below.
        3. Your entire response MUST be a single JSON object containing a `plan` key and a `details` key.

        **Action Reference:**

        1.  If you need to delegate, the `details` object in your JSON response must be:
            `{{"action": "delegate", "recipient": "<role>", "task_description": "<new task>"}}`

        2.  If you need to use a tool, the `details` object in your JSON response must be:
            `{{"action": "use_tool", "tool_name": "<tool>", "method": "<method>", "arguments": {{...}} }}`

        3.  If you have the final answer, the `details` object in your JSON response must be:
            `{{"action": "execute", "response": "<final answer>"}}`

        4.  If you are a manager requesting a revision, the `details` object in your JSON response must be:
            `{{"action": "request_revision", "subordinate_to_revise": "<role>", "revision_feedback": "<feedback>"}}`


        **Example of a GOOD and COMPLETE response:**
        ```json
        {{
          "plan": [
            "First, I need to delegate the creative portion of this task to the CMO.",
            "Then, I will review the CMO\'s work."
          ],
          "details": {{
            "action": "delegate",
            "recipient": "CMO",
            "task_description": "Please generate a compelling story about nature."
          }}
        }}
        ```

        **Example of a BAD response (missing the `details` object):
        ```json
        {{
          "plan": [
            "I will delegate this to the CMO."
          ]
        }}
        ```
        """
        return prompt

    def execute_task(self, task: Task, delegator=None) -> AgentAction:
        delegator_role = delegator.persona.role if delegator else "The User"
        if self.persona.role not in task.history:
            task.history.append(self.persona.role)
        print(f"[{self.persona.role}] received task '{task.description}' from [{delegator_role}].")

        prompt = self._create_prompt(task, delegator_role)

        for i in range(3): # Retry loop
            try:
                print(f"[{self.persona.role}] is thinking... (Attempt {i+1})")
                raw_response = self.llm.invoke(prompt).content
                clean_response = self._clean_json_output(raw_response)
                response_dict = json.loads(clean_response)
                response = AgentAction.model_validate(response_dict)

                # If parsing and validation succeed, log and return.
                if response.plan:
                    print(f"[{self.persona.role}] has formulated a plan:")
                    for i, step in enumerate(response.plan, 1):
                        print(f"  Step {i}: {step}")

                action_name = response.details.action
                if action_name == 'execute':
                    print(f"[{self.persona.role}] has executed the task.")
                elif action_name == 'delegate':
                    print(f"[{self.persona.role}] has decided to delegate the task to [{response.details.recipient}].")
                elif action_name == 'use_tool':
                    print(f"[{self.persona.role}] has decided to use the '{response.details.tool_name}' tool.")
                
                return response # Success, exit the loop

            except (json.JSONDecodeError, ValidationError) as e:
                print(f"[{self.persona.role}] encountered a parsing/validation error on attempt {i+1}: {e}")
                error_feedback = f"Your previous attempt failed with an error: {e}. Please review the required JSON schema and your plan, then try again. Ensure your entire response is a single, valid JSON object with 'plan' and 'details' keys, and that the `details` object has the correct `action` field and structure."
                prompt = self._create_prompt(task, delegator_role) + f"\n\n**IMPORTANT CORRECTION:**\n{error_feedback}"
                task.action_history.append(f"Attempt {i+1} failed with parsing/validation error: {e}")
            except Exception as e:
                print(f"[{self.persona.role}] encountered an unexpected error on attempt {i+1}: {e}")
                # For unexpected errors, use a more generic correction prompt
                error_feedback = f"Your previous attempt failed with an unexpected error: {e}. Please try again, adhering strictly to the output format."
                prompt = self._create_prompt(task, delegator_role) + f"\n\n**IMPORTANT CORRECTION:**\n{error_feedback}"
                task.action_history.append(f"Attempt {i+1} failed with unexpected error: {e}")

        # If all retries fail, return a final error action
        print(f"[{self.persona.role}] failed to generate a valid action after multiple attempts.")
        return AgentAction(
            plan=["Failed to generate a valid action after multiple attempts."],
            details=FinalAnswer(action="execute", response="Error: I was unable to formulate a valid action to complete the task after multiple retries.")
        )