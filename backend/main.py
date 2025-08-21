from fastapi import FastAPI
from pydantic import BaseModel
import os
from crewai import Crew, Process, Task
from backend.core.agents import AiOrgAgents
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

# Initialize the FastAPI app
app = FastAPI(
    title="AI Organization API",
    description="An API for orchestrating a crew of AI agents to accomplish tasks.",
    version="0.1.0",
)

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

class TaskRequest(BaseModel):
    task: str

@app.get("/")
def read_root():
    return {"message": "AI Organization API is running."}

@app.post("/api/execute-task")
def execute_task(request: TaskRequest):
    try:
        # Define the task
        task = Task(
            description=request.task,
            expected_output="A comprehensive report detailing the findings, analysis, and final conclusion.",
            agent=coo  # Start with the COO
        )

        # Form the crew
        crew = Crew(
            agents=[ceo, coo, cto],
            tasks=[task],
            process=Process.hierarchical,
            manager_llm=llm,
            verbose=2
        )

        # Kick off the crew's work
        result = crew.kickoff()

        return {"result": result}
    except Exception as e:
        return {"error": str(e)}
