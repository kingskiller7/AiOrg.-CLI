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
            "subordinates": []
        },
        "Offensive Security Team": {
            "persona": Persona(role="Offensive Security Team (Red Team)", responsibilities=["Conducting penetration tests on systems and applications", "Performing ethical hacking to identify vulnerabilities", "Simulating attack scenarios to test defenses"], abilities=["browser", "code_executor", "file_system"]),
            "subordinates": []
        },
        "Operations": {
            "persona": Persona(role="Operations", responsibilities=["Overseeing daily business operations", "Improving operational efficiency and processes", "Managing production, logistics, and supply chain"]),
            "subordinates": []
        },
        "Finance & Accounts": {
            "persona": Persona(role="Finance & Accounts", responsibilities=["Managing daily financial operations", "Preparing financial statements and reports", "Overseeing budgeting, forecasting, and cash flow"]),
            "subordinates": []
        },
        "Technology / Engineering": {
            "persona": Persona(role="Technology / Engineering", responsibilities=["Managing the software development lifecycle", "Ensuring the quality and stability of the technical architecture", "Leading and mentoring the engineering team"]),
            "subordinates": []
        },
        "HR & Administration": {
            "persona": Persona(role="HR & Administration", responsibilities=["Managing recruitment, onboarding, and employee relations", "Developing and enforcing HR policies and compliance", "Overseeing office administration and record-keeping"]),
            "subordinates": []
        },
        "Marketing & Sales": {
            "persona": Persona(role="Marketing & Sales", responsibilities=["Developing and implementing sales and marketing strategies", "Overseeing marketing campaigns and sales activities", "Analyzing market data and trends"]),
            "subordinates": []
        },
        "Customer Service": {
            "persona": Persona(role="Customer Service", responsibilities=["Overseeing the customer service team", "Developing and implementing customer service policies", "Handling complex customer complaints and escalations"]),
            "subordinates": []
        },
        "R&D": {
            "persona": Persona(role="R&D", responsibilities=["Developing and executing the R&D strategy", "Leading new product development and innovation", "Managing the R&D team and budget"]),
            "subordinates": []
        },
        "Procurement": {
            "persona": Persona(role="Procurement", responsibilities=["Developing and implementing procurement strategies", "Managing supplier and vendor relationships", "Negotiating contracts and optimizing costs"]),
            "subordinates": []
        },

        # 4. CIO's Department
        "Data Analyst Team": {
            "persona": Persona(role="Data Analyst Team", responsibilities=["Collecting, cleaning, and analyzing data from various sources", "Identifying trends, patterns, and correlations in datasets", "Creating reports and visualizations to communicate findings"], abilities=["code_executor", "file_system"]),
            "subordinates": []
        },
        "Systems Administration Team": {
            "persona": Persona(role="Systems Administration Team", responsibilities=["Installing, configuring, and maintaining server and network infrastructure", "Managing user accounts and system permissions", "Monitoring system performance and security"], abilities=["file_system"]),
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