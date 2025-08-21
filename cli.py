import argparse

from ai_org_core.persona import Persona
from ai_org_core.task import Task
from ai_org_core.orchestrator import Organization

def define_organization_structure() -> dict:
    """Defines the agents, personas, and hierarchy of the organization."""
    
    # Note: In a real system, these personas would be loaded from a config file.
    structure = {
        "CEO": {
            "persona": Persona(
                role="CEO",
                responsibilities=["Set overall strategy", "Make final decisions"],
            ),
            "subordinates": ["COO", "CTO"]
        },
        "COO": {
            "persona": Persona(
                role="COO",
                responsibilities=["Manage day-to-day operations", "Ensure operational efficiency"],
            ),
            "subordinates": [] # The COO executes tasks directly in this simple setup
        },
        "CTO": {
            "persona": Persona(
                role="CTO",
                responsibilities=["Oversee all technical aspects", "Manage technology development"],
                abilities=["browser"] # Granting the browser tool ability
            ),
            "subordinates": [] # The CTO executes tasks directly
        }
    }
    return structure

def main(task_description: str):
    print(f"Initializing AI Organization for task: '{task_description}'")

    # 1. Define the Organization
    structure = define_organization_structure()
    organization = Organization(structure)

    # 2. Define the Task
    # The initial task is always assigned to the CEO to start the delegation chain.
    task = Task(
        description=task_description,
        expected_output="A comprehensive result based on the task description.",
        assigned_to="CEO"
    )

    # 3. Kick off the work
    result = organization.kickoff(task)

    print("\n########################")
    print("## Work Complete")
    print("########################\n")
    print("Final Result:")
    print(result)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the AiOrg with a specific task.")
    parser.add_argument("task", type=str, help="The task for the organization to execute.")
    args = parser.parse_args()

    main(args.task)
