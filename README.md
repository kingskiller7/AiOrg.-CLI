# AI Organization

This project implements a hierarchical organization of AI agents designed to accomplish complex tasks. The system is built with a Python backend using FastAPI, and a modern web interface developed with Next.js. This allows for a powerful and flexible way to automate and delegate complex workflows.

## Key Features

*   **Hierarchical AI Agent System:** A virtual company of AI agents with a full C-suite, management, and specialized employees.
*   **Strategic Task Routing:** Instead of simple delegation, the system uses a strategic controller to analyze incoming tasks and route them to the correct department head (e.g., CTO, CMO), ensuring tasks are handled by the right team from the start.
*   **Managerial Feedback Loop:** Managers can review the work of their subordinates and, if it's unsatisfactory, send it back down with specific feedback for revision. This creates a realistic and iterative workflow.
*   **Dynamic Role Evolution:** Agents that lack the necessary tools to perform their duties can automatically request new abilities from leadership, creating a self-improving and adaptable organization.
*   **Extensible Agent Personas:** Easily define and customize the roles, responsibilities, and starting abilities of each AI agent.
*   **Deterministic & Efficient Core:** The underlying agent architecture has been refactored to be deterministic (temperature=0) and highly efficient (using a single, shared language model).
*   **Dual Interface:** Interact with the AI organization through a user-friendly web interface or a powerful command-line interface (CLI).

## Advanced Workflows

The orchestration engine supports several advanced, true-to-life workflows:

1.  **Standard Operating Procedures:** When a task is submitted, it is first analyzed and routed to the correct department (e.g., tech tasks to the CTO). This ensures efficiency and proper oversight.
2.  **Iterative Improvement:** A manager can review a subordinate's work and send it back with feedback using the `request_revision` action, ensuring quality control.
3.  **Permission Requests:** If an agent tries to use a tool it doesn't have, the system guides the agent to delegate a request to the CEO to formally ask for that new ability.

## Technology Stack

*   **Backend:**
    *   Python
    *   FastAPI
    *   LangChain
    *   Google Gemini
    *   Pydantic
*   **Frontend:**
    *   Next.js
    *   React
    *   TypeScript
    *   Tailwind CSS
*   **Tooling:**
    *   pnpm
    *   Ruff (linter)
    *   Playwright (for browser automation capabilities)

## Project Structure

```
AiOrg.-CLI/
├── backend/
│   ├── core/
│   │   ├── agent.py
│   │   ├── orchestrator.py
│   │   ├── persona.py
│   │   └── task.py
│   ├── main.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   └── app/
│   │       ├── page.tsx
│   │       └── layout.tsx
│   ├── package.json
│   └── ...
├── cli.py
├── README.md
└── ...
```

## Prerequisites

Before you begin, ensure you have the following installed:

*   Python 3.8+
*   Node.js (which includes npm)
*   pnpm (you can install it with `npm install -g pnpm`)

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/kingskiller7/AiOrg.-CLI.git
    cd AiOrg.-CLI
    ```

2.  **Install backend dependencies:**
    *   Create a virtual environment:
        ```bash
        python3 -m venv backend/venv
        ```
    *   Activate the virtual environment:
        ```bash
        source backend/venv/bin/activate
        ```
    *   Install the required packages:
        ```bash
        pip install -r backend/requirements.txt
        ```

3.  **Install frontend dependencies:**
    ```bash
    cd frontend
    pnpm install
    cd ..
    ```

## Configuration

Before running the application, you must add your Google Gemini API key to the `backend/.env` file.

1.  Create a `.env` file in the `backend` directory:
    ```bash
    touch backend/.env
    ```
2.  Add your API key to the file:
    ```
    GOOGLE_API_KEY="YOUR_API_KEY_HERE"
    ```

## Usage

### Running the Web Application

1.  **Start the backend server:**
    *   Activate the virtual environment:
        ```bash
        source backend/venv/bin/activate
        ```
    *   Start the FastAPI server:
        ```bash
        uvicorn backend.main:app --reload
        ```
    The backend will be running at `http://127.0.0.1:8000`.

2.  **Start the frontend server:**
    *   In a new terminal, navigate to the `frontend` directory:
        ```bash
        cd frontend
        ```
    *   Start the Next.js development server:
        ```bash
        pnpm run dev
        ```
    The frontend will be accessible at `http://localhost:3000`.

### Using the Command-Line Interface (CLI)

1.  **Activate the virtual environment:**
    ```bash
    source backend/venv/bin/activate
    ```
2.  **Run the CLI with your task:**
    ```bash
    python cli.py "Your task description here"
    ```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
