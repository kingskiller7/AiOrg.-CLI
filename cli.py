import argparse
import os
from crewai import Crew, Process, Task
from backend.core.agents import AiOrgAgents
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

# Initialize the Gemini model
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env file. Please add it.")

llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    verbose=True,
    temperature=0.5,
    google_api_key=api_key,
)

# Initialize agents
agents = AiOrgAgents()
ceo = agents.ceo_agent()
coo = agents.coo_agent()
cto = agents.cto_agent()

def main(task: str):
    print(f"Starting task: {task}")

    # Define the task
    task = Task(
        description=task,
        expected_output="A comprehensive report detailing the findings, analysis, and final conclusion.",
        agent=coo  # Start with the COO to delegate
    )

    # Form the crew
    crew = Crew(
        agents=[ceo, coo, cto],
        tasks=[task],
        process=Process.hierarchical,
        manager_llm=llm,
        verbose=True
    )

    # Kick off the crew's work
    result = crew.kickoff()

    print("\n\n########################")
    print("## Crew Work Complete")
    print("########################\n")
    print("Final Result:")
    print(result)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the AiOrg crew with a specific task.")
    parser.add_argument("task", type=str, help="The task for the crew to execute.")
    args = parser.parse_args()

    main(args.task)
