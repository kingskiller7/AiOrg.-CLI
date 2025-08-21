from fastapi import FastAPI
from pydantic import BaseModel

from ai_org_core.persona import Persona
from ai_org_core.task import Task
from ai_org_core.orchestrator import Organization

app = FastAPI(
    title="AiOrg Framework API",
    description="An API for orchestrating a custom AI agent organization.",
    version="1.2.0", # Version bump for new structure
)

def define_organization_structure() -> dict:
    """Defines the agents, personas, and hierarchy of the organization."""
    structure = {
        # 1. Top Management
        "CEO": {
            "persona": Persona(role="CEO", responsibilities=["Final decision-making", "Strategy execution"]),
            "subordinates": ["COO", "CFO", "CTO", "CIO", "CHRO", "CMO", "CSO"]
        },

        # 2. Executive Leadership (C-Suite)
        "COO": {
            "persona": Persona(role="COO", responsibilities=["Day-to-day operations", "Process efficiency"]),
            "subordinates": ["Operations", "Customer Service", "Procurement"]
        },
        "CFO": {
            "persona": Persona(role="CFO", responsibilities=["Financial planning", "Accounting"], abilities=["file_system"]),
            "subordinates": ["Finance & Accounts"]
        },
        "CTO": {
            "persona": Persona(role="CTO", responsibilities=["Tech strategy", "Product development"], abilities=["browser", "code_executor", "file_system", "tool_forge"]),
            "subordinates": ["Technology / Engineering", "R&D"]
        },
        "CIO": {
            "persona": Persona(role="CIO", responsibilities=["Data and information management", "Digital systems"]),
            "subordinates": []
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
            "persona": Persona(role="CSO", responsibilities=["Strategy alignment", "Sales oversight"]),
            "subordinates": []
        },

        # 3. Middle Management (Functional Heads)
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
        }
    }
    return structure

class TaskRequest(BaseModel):
    task: str

@app.get("/")
def read_root():
    return {"message": "AiOrg API is running."}

@app.post("/api/execute-task")
def execute__task(request: TaskRequest):
    try:
        structure = define_organization_structure()
        organization = Organization(structure)
        
        task = Task(
            description=request.task,
            expected_output="A comprehensive result based on the task description.",
            assigned_to="CEO"
        )

        result = organization.kickoff(task)

        return {"result": result}
    except Exception as e:
        return {"error": str(e)}