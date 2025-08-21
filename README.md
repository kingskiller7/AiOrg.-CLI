# AI Organization

This project creates a hierarchical crew of AI agents to accomplish tasks. It features a Python backend using FastAPI and CrewAI, and a modern web interface built with Next.js.

## Quick Start

This project includes scripts to automate the setup and execution process.

### Prerequisites

- Python 3.8+
- Node.js and pnpm

### 1. Add API Key

Before you begin, you must add your Google Gemini API key to the environment file:

1.  Open the file at `backend/.env`.
2.  Replace `YOUR_API_KEY_HERE` with your actual key.

### 2. Install Dependencies

Run the installation script from the project root directory. This will install all required Python and Node.js packages.

```bash
./install.sh
```

### 3. Run the Application

Once the installation is complete, you can start the application with a single command:

```bash
./start.sh
```

This will:
- Start the backend API server on `http://127.0.0.1:8000`.
- Start the frontend web interface on `http://localhost:3000`.

You can now open `http://localhost:3000` in your web browser to use the application.

---

### Manual CLI Usage

If you wish to use the command-line interface directly (after running the `./install.sh` script):

1.  Activate the Python virtual environment: `source backend/venv/bin/activate`
2.  Run the CLI script with a task: `python cli.py "Your task description here"`
