from fastapi import FastAPI
from pydantic import BaseModel

# Import the new AiOrg framework components
from ai_org_core.agent import AIAgent
from ai_org_core.persona import Persona
from ai_org_core.task import Task
from ai_org_core.orchestrator import Organization

# Initialize the FastAPI app
app = FastAPI(
    title="AiOrg Framework API",
    description="An API for orchestrating a custom AI agent organization.",
    version="1.0.0",
)

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

    structure = {
        "CEO": ceo,
        "COO": coo,
        "CTO": cto,
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
            assigned_to="COO"
        )

        result = organization.kickoff(task)

        return {"result": result}
    except Exception as e:
        return {"error": str(e)}