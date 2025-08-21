import argparse

# Import the new AiOrg framework components
from ai_org_core.agent import AIAgent
from ai_org_core.persona import Persona
from ai_org_core.task import Task
from ai_org_core.orchestrator import Organization

def define_organization_structure() -> dict:
    """Defines the agents and their personas that form the organization."""
    
    ceo_persona = Persona(
        role="CEO",
        responsibilities=["Final decision-making", "Strategy execution"],
        views=["Focus on long-term value", "Maintain high quality standards"]
    )
    ceo = AIAgent(ceo_persona)

    coo_persona = Persona(
        role="COO",
        responsibilities=["Day-to-day operations", "Process efficiency"],
        views=["Efficiency is key", "Standardize processes"]
    )
    coo = AIAgent(coo_persona)

    cto_persona = Persona(
        role="CTO",
        responsibilities=["Technology strategy", "Product development"],
        views=["Embrace cutting-edge technology", "Build scalable systems"]
    )
    cto = AIAgent(cto_persona)

    # The organizational chart
    structure = {
        "CEO": ceo,
        "COO": coo,
        "CTO": cto,
    }
    return structure

def main(task_description: str):
    print(f"Initializing AI Organization for task: '{task_description}'")

    # 1. Define the Organization
    structure = define_organization_structure()
    organization = Organization(structure)

    # 2. Define the Task
    # For now, we'll assign all tasks to the COO to start the delegation chain.
    task = Task(
        description=task_description,
        expected_output="A comprehensive result based on the task description.",
        assigned_to="COO"
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