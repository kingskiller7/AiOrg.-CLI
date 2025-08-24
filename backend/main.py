from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import shutil
import os

from .core.persona import Persona
from .core.task import Task
from .core.orchestrator import Organization
from .core.config import WORKSPACE_DIR, UPLOAD_DIR

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
            "persona": Persona(role="CTO", responsibilities=["Developing the company's technology strategy to align with business goals", "Overseeing the development and implementation of new technologies", "Managing the technology team and technical architecture"], abilities=["browser", "code_executor", "file_system", "tool_forge", "file_processing"]),
            "subordinates": ["Technology / Engineering", "R&D"]
        },
        "CIO": {
            "persona": Persona(role="CIO", responsibilities=["Overseeing the company-wide data strategy and IT infrastructure", "Managing information security and risk management", "Ensuring data governance and compliance"]),
            "subordinates": ["Data Analyst Team", "Systems Administration Team"]
        },
        "CHRO": {
            "persona": Persona(role="CHRO", responsibilities=["Developing and executing HR strategy in support of the overall business plan", "Overseeing talent acquisition, development, and retention", "Managing compensation, benefits, and company culture"]),
            "subordinates": ["HR & Administration"]
        },
        "CMO": {
            "persona": Persona(role="CMO", responsibilities=["Developing and executing the overall marketing strategy", "Overseeing market research, branding, and advertising", "Driving revenue growth and customer acquisition"], abilities=["browser"]),
            "subordinates": ["Marketing & Sales"]
        },
        "CSO": {
            "persona": Persona(role="Chief Security Officer", responsibilities=["Developing and implementing the overall security strategy", "Managing cybersecurity and physical security", "Overseeing risk management and incident response"]),
            "subordinates": ["Security Operations Team", "Offensive Security Team"]
        },

        # 3. Middle Management (Functional Heads)
        "Security Operations Team": {
            "persona": Persona(role="Security Operations Team (Blue Team)", responsibilities=["Monitoring systems for threats and vulnerabilities", "Managing and responding to security incidents", "Maintaining security infrastructure"]),
            "subordinates": ["Security Analyst"]
        },
        "Offensive Security Team": {
            "persona": Persona(role="Offensive Security Team (Red Team)", responsibilities=["Conducting penetration tests on systems and applications", "Performing ethical hacking to identify vulnerabilities", "Simulating attack scenarios to test defenses"], abilities=["browser", "code_executor", "file_system"]),
            "subordinates": ["Penetration Tester"]
        },
        "Operations": {
            "persona": Persona(role="Operations", responsibilities=["Overseeing daily business operations", "Improving operational efficiency and processes", "Managing production, logistics, and supply chain"]),
            "subordinates": ["Logistics Coordinator"]
        },
        "Finance & Accounts": {
            "persona": Persona(role="Finance & Accounts", responsibilities=["Managing daily financial operations", "Preparing financial statements and reports", "Overseeing budgeting, forecasting, and cash flow"]),
            "subordinates": []
        },
        "Technology / Engineering": {
            "persona": Persona(role="Technology / Engineering", responsibilities=["Managing the software development lifecycle", "Ensuring the quality and stability of the technical architecture", "Leading and mentoring the engineering team"]),
            "subordinates": ["Senior Software Engineer"]
        },
        "HR & Administration": {
            "persona": Persona(role="HR & Administration", responsibilities=["Managing recruitment, onboarding, and employee relations", "Developing and enforcing HR policies and compliance", "Overseeing office administration and record-keeping"]),
            "subordinates": []
        },
        "Marketing & Sales": {
            "persona": Persona(role="Marketing & Sales", responsibilities=["Developing and implementing sales and marketing strategies", "Overseeing marketing campaigns and sales activities", "Analyzing market data and trends"]),
            "subordinates": ["Marketing Analyst", "Sales Representative"]
        },
        "Customer Service": {
            "persona": Persona(role="Customer Service", responsibilities=["Overseeing the customer service team", "Developing and implementing customer service policies", "Handling complex customer complaints and escalations"]),
            "subordinates": ["Support Specialist"]
        },
        "R&D": {
            "persona": Persona(role="R&D", responsibilities=["Developing and executing the R&D strategy", "Leading new product development and innovation", "Managing the R&D team and budget"]),
            "subordinates": ["Lead Researcher"]
        },
        "Procurement": {
            "persona": Persona(role="Procurement", responsibilities=["Developing and implementing procurement strategies", "Managing supplier and vendor relationships", "Negotiating contracts and optimizing costs"]),
            "subordinates": ["Purchasing Agent"]
        },

        # 4. CIO's Department
        "Data Analyst Team": {
            "persona": Persona(role="Data Analyst Team", responsibilities=["Collecting, cleaning, and analyzing data from various sources", "Identifying trends, patterns, and correlations in datasets", "Creating reports and visualizations to communicate findings"], abilities=["code_executor", "file_system", "file_processing"]),
            "subordinates": []
        },
        "Systems Administration Team": {
            "persona": Persona(role="Systems Administration Team", responsibilities=["Installing, configuring, and maintaining server and network infrastructure", "Managing user accounts and system permissions", "Monitoring system performance and security"], abilities=["file_system"]),
            "subordinates": []
        },

        # 5. Operational Staff
        "Senior Software Engineer": {
            "persona": Persona(role="Senior Software Engineer", responsibilities=["Writing complex code modules", "Debugging critical issues", "Implementing core application features"], abilities=["code_executor", "file_system"]),
            "subordinates": []
        },
        "Lead Researcher": {
            "persona": Persona(role="Lead Researcher", responsibilities=["Conducting in-depth technical research", "Analyzing emerging technologies", "Summarizing complex findings for leadership"], abilities=["browser"]),
            "subordinates": []
        },
        "Security Analyst": {
            "persona": Persona(role="Security Analyst", responsibilities=["Analyzing security logs and alerts", "Investigating potential security incidents", "Monitoring for suspicious activity"], abilities=["file_system", "browser"]),
            "subordinates": []
        },
        "Penetration Tester": {
            "persona": Persona(role="Penetration Tester", responsibilities=["Conducting authorized tests on computer systems to expose vulnerabilities", "Writing detailed reports on findings", "Simulating real-world attacks"], abilities=["code_executor", "file_system", "browser"]),
            "subordinates": []
        },
        "Logistics Coordinator": {
            "persona": Persona(role="Logistics Coordinator", responsibilities=["Coordinating and monitoring supply chain operations", "Managing inventory and logistics", "Ensuring timely delivery of goods"], abilities=["file_system"]),
            "subordinates": []
        },
        "Support Specialist": {
            "persona": Persona(role="Support Specialist", responsibilities=["Responding to customer inquiries and issues", "Providing product support and troubleshooting", "Documenting customer interactions"], abilities=["browser"]),
            "subordinates": []
        },
        "Purchasing Agent": {
            "persona": Persona(role="Purchasing Agent", responsibilities=["Sourcing and purchasing materials and services", "Evaluating vendors and negotiating prices", "Maintaining purchasing records"], abilities=["browser", "file_system"]),
            "subordinates": []
        },

        "Marketing Analyst": {
            "persona": Persona(role="Marketing Analyst", responsibilities=["Analyzing marketing campaign performance", "Conducting market research and competitor analysis", "Tracking and reporting on key metrics"], abilities=["browser"]),
            "subordinates": []
        },
        "Sales Representative": {
            "persona": Persona(role="Sales Representative", responsibilities=["Generating leads and contacting potential customers", "Presenting products and closing sales", "Maintaining customer relationships"], abilities=["browser"]),
            "subordinates": []
        }
    }
    return structure

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
