from fastapi import FastAPI
from pydantic import BaseModel

from ai_org_core.persona import Persona
from ai_org_core.task import Task
from ai_org_core.orchestrator import Organization

app = FastAPI(
    title="AiOrg Framework API",
    description="An API for orchestrating a custom AI agent organization.",
    version="1.1.0",
)

def define_organization_structure() -> dict:
    """Defines the agents, personas, and hierarchy of the organization."""
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
            "subordinates": []
        },
        "CTO": {
            "persona": Persona(
                role="CTO",
                responsibilities=["Oversee all technical aspects", "Manage technology development"],
                abilities=["browser"] # Granting the browser tool ability
            ),
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
def execute_task(request: TaskRequest):
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
        # In case of an error, return a JSON response
        return {"error": str(e)}
