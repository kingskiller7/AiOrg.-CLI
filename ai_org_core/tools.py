from playwright.sync_api import sync_playwright
import subprocess
import os
from .config import WORKSPACE_DIR
from .tool_forge import ToolForge

class BrowserTool:
    """A tool for browsing websites and scraping their content."""
    def browse_and_scrape(self, url: str) -> str:
        """Visits a URL and returns the text content of the page."""
        print(f"[BrowserTool] Browsing {url}...")
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(url, timeout=15000)
                content = page.locator('body').inner_text()
                browser.close()
                return content[:5000]
        except Exception as e:
            return f"Error browsing site: {e}"

class CodeExecutionTool:
    """A tool for writing, linting, and executing Python code in a sandbox."""
    def __init__(self, work_dir = WORKSPACE_DIR):
        self.work_dir = work_dir
        if not os.path.exists(self.work_dir):
            os.makedirs(self.work_dir)

    def lint_code(self, code: str) -> str:
        """Checks code for syntax errors using ruff."""
        print(f"[CodeTool] Linting code...")
        try:
            result = subprocess.run(["ruff", "check", "--stdin-filename", "temp.py", "-"], input=code, text=True, capture_output=True)
            if result.returncode == 0:
                return "No linting errors found."
            else:
                return f"Linting errors found:\n{result.stderr}"
        except Exception as e:
            return f"Error during linting: {e}"

    def write_code(self, filename: str, code: str) -> str:
        """Writes code to a file in the workspace."""
        filepath = os.path.join(self.work_dir, filename)
        print(f"[CodeTool] Writing code to {filepath}...")
        try:
            with open(filepath, 'w') as f:
                f.write(code)
            return f"Successfully wrote code to {filename}."
        except Exception as e:
            return f"Error writing file: {e}"

    def execute_code(self, filename: str) -> str:
        """Executes a Python script in the workspace and captures its output."""
        filepath = os.path.join(self.work_dir, filename)
        print(f"[CodeTool] Executing {filepath}...")
        if not os.path.exists(filepath):
            return f"Error: File '{filename}' not found."
        try:
            result = subprocess.run(["python", filepath], text=True, capture_output=True, timeout=30)
            output = f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
            return output
        except Exception as e:
            return f"Error during execution: {e}"

class FileSystemTool:
    """A tool for interacting with the local file system in a sandboxed workspace."""
    def __init__(self, work_dir = WORKSPACE_DIR):
        self.work_dir = work_dir
        if not os.path.exists(self.work_dir):
            os.makedirs(self.work_dir)

    def list_directory(self, path: str = '.') -> str:
        """Lists the contents of a specified subdirectory within the workspace."""
        target_path = os.path.join(self.work_dir, path)
        print(f"[FileTool] Listing contents of {target_path}...")
        if not os.path.exists(target_path) or not os.path.isdir(target_path):
            return f"Error: Directory '{path}' not found."
        try:
            return "\n".join(os.listdir(target_path))
        except Exception as e:
            return f"Error listing directory: {e}"

    def read_file(self, filename: str) -> str:
        """Reads the content of a file from the workspace."""
        filepath = os.path.join(self.work_dir, filename)
        print(f"[FileTool] Reading file {filepath}...")
        if not os.path.exists(filepath):
            return f"Error: File '{filename}' not found."
        try:
            with open(filepath, 'r') as f:
                return f.read()
        except Exception as e:
            return f"Error reading file: {e}"

    def write_file(self, filename: str, content: str) -> str:
        """Writes content to a file in the workspace."""
        filepath = os.path.join(self.work_dir, filename)
        print(f"[FileTool] Writing to file {filepath}...")
        try:
            with open(filepath, 'w') as f:
                f.write(content)
            return f"Successfully wrote to {filename}."
        except Exception as e:
            return f"Error writing file: {e}"

# Instantiate tools for the application to use
browser_tool = BrowserTool()
code_executor_tool = CodeExecutionTool()
file_system_tool = FileSystemTool()
tool_forge = ToolForge()