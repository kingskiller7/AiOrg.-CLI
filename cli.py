import argparse

from ai_org_core.persona import Persona
from ai_org_core.task import Task
from ai_org_core.orchestrator import Organization

def define_organization_structure() -> dict:
    """Defines the agents, personas, and hierarchy of the organization."""
    
    structure = {
        # 1. Top Management
        "CEO": {
            "persona": Persona(role="CEO", responsibilities=["Setting the company's long-term vision and strategy", "Making major corporate and financial decisions", "Managing the overall operations and resources", "Acting as the main point of communication between the board of directors and the organization"]),
            "subordinates": ["COO", "CFO", "CTO", "CIO", "CHRO", "CMO", "CSO"]
        },

        # 2. Executive Leadership (C-Suite)
        "COO": {
            "persona": Persona(role="COO", responsibilities=["Overseeing the company's day-to-day administrative and operational functions", "Translating strategy into actionable plans", "Managing company resources and process improvement"]),
            "subordinates": ["Operations", "Customer Service", "Procurement"]
        },
        "CFO": {
            "persona": Persona(role="CFO", responsibilities=["Managing the company's financial planning and analysis", "Overseeing budgeting and cash flow", "Performing risk management", "Ensuring compliance with financial regulations"], abilities=["file_system"]),
            "subordinates": ["Finance & Accounts"]
        },
        "CTO": {
            "persona": Persona(role="CTO", responsibilities=["Developing the company's technology strategy to align with business goals", "Overseeing the development and implementation of new technologies", "Managing the technology team and technical architecture"], abilities=["browser", "code_executor", "file_system", "tool_forge"]),
            "subordinates": ["Technology / Engineering", "R&D"]
        },
        "CIO": {
            "persona": Persona(role="CIO", responsibilities=["Oversee the company-wide data strategy", "Ensure data integrity and governance", "Facilitate insights from data"]),
            "subordinates": ["Data Analyst Team", "Systems Administration Team"]
        },
        "CHRO": {
            "persona": Persona(role="CHRO", responsibilities=["Agent resources", "Culture", "Training"]),
            "subordinates": ["HR & Administration"]
        },
        "CMO": {
            "persona": Persona(role="CMO", responsibilities=["Brand", "Growth", "Customer acquisition"], abilities=["browser"]),
            "subordinates": ["Marketing & Sales"]
        },
        "CSO": {
            "persona": Persona(role="Chief Security Officer", responsibilities=["Oversee all security aspects", "Vulnerability management"]),
            "subordinates": ["Security Team"]
        },

        # 3. Middle Management (Functional Heads)
        "Security Team": {
            "persona": Persona(role="Security Team", responsibilities=["Cybersecurity analysis", "Ethical hacking", "Vulnerability assessment"], abilities=["browser", "code_executor", "file_system"]),
            "subordinates": []
        },
        "Operations": {
            "persona": Persona(role="Operations", responsibilities=["Production", "Logistics", "Supply chain"]),
            "subordinates": []
        },
        "Finance & Accounts": {
            "persona": Persona(role="Finance & Accounts", responsibilities=["Budgeting", "Reporting", "Investments"]),
            "subordinates": []
        },
        "Technology / Engineering": {
            "persona": Persona(role="Technology / Engineering", responsibilities=["Software development", "Hardware", "Innovation"]),
            "subordinates": []
        },
        "HR & Administration": {
            "persona": Persona(role="HR & Administration", responsibilities=["Recruitment", "Training", "Agent relations"]),
            "subordinates": []
        },
        "Marketing & Sales": {
            "persona": Persona(role="Marketing & Sales", responsibilities=["Market research", "Campaigns", "Customer relations"]),
            "subordinates": []
        },
        "Customer Service": {
            "persona": Persona(role="Customer Service", responsibilities=["After-sales", "Client success"]),
            "subordinates": []
        },
        "R&D": {
            "persona": Persona(role="R&D", responsibilities=["Innovation", "Product improvement"]),
            "subordinates": []
        },
        "Procurement": {
            "persona": Persona(role="Procurement", responsibilities=["Vendor management", "Purchasing"]),
            "subordinates": []
        },

        # 4. CIO's Department
        "Data Analyst Team": {
            "persona": Persona(role="Data Analyst Team", responsibilities=["Analyze datasets to extract insights", "Generate business intelligence reports", "Identify trends and patterns in data"], abilities=["code_executor", "file_system"]),
            "subordinates": []
        },
        "Systems Administration Team": {
            "persona": Persona(role="Systems Administration Team", responsibilities=["Manage and organize file storage", "Ensure data accessibility and system uptime", "Perform data archiving"], abilities=["file_system"]),
            "subordinates": []
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