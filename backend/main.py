from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import shutil
import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from .core.persona import Persona
from .core.task import Task
from .core.orchestrator import Organization
from .core.config import WORKSPACE_DIR, UPLOAD_DIR
from cli import define_organization_structure

app = FastAPI(
    title="AiOrg Framework API",
    description="An API for orchestrating a custom AI agent organization.",
    version="1.3.0",
)

url = os.getenv("FRONTEND_API_URL", "http://localhost:3000")

# Add CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["url"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure the workspace and upload directories exist
os.makedirs(WORKSPACE_DIR, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)



class TaskRequest(BaseModel):
    task: str
    file_path: Optional[str] = None

@app.get("/")
def read_root():
    return {"message": "AiOrg API is running."}

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        return {"file_path": file_path}
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/execute-task")
def execute_task(request: TaskRequest):
    try:
        structure = define_organization_structure()
        organization = Organization(structure)
        
        task_description = request.task
        if request.file_path:
            task_description += f"\n\nFile attached: {request.file_path}"

        task = Task(
            description=task_description,
            expected_output="A comprehensive result based on the task description.",
            assigned_to="CEO"
        )

        result = organization.kickoff(task)

        return {"result": result}
    except Exception as e:
        return {"error": str(e)}