import os
import json
import importlib.util

from .config import CUSTOM_TOOLS_DIR

class ToolForge:
    """Manages the creation and loading of custom, agent-created tools."""
    def __init__(self, custom_tools_dir = CUSTOM_TOOLS_DIR):
        self.custom_tools_dir = custom_tools_dir
        self.manifest_path = os.path.join(self.custom_tools_dir, "manifest.json")
        
        if not os.path.exists(self.custom_tools_dir):
            os.makedirs(self.custom_tools_dir)
        if not os.path.exists(self.manifest_path):
            with open(self.manifest_path, 'w') as f:
                json.dump({}, f)

    def create_tool(self, tool_name: str, description: str, code: str) -> str:
        """Creates a new tool by saving its code and updating the manifest."""
        if not tool_name.isidentifier():
            return f"Error: '{tool_name}' is not a valid Python identifier."

        filepath = os.path.join(self.custom_tools_dir, f"{tool_name}.py")
        print(f"[ToolForge] Creating new tool: {tool_name}")

        try:
            with open(filepath, 'w') as f:
                f.write(code)
            
            with open(self.manifest_path, 'r+') as f:
                manifest = json.load(f)
                manifest[tool_name] = {
                    "description": description,
                    "filepath": filepath
                }
                f.seek(0)
                json.dump(manifest, f, indent=4)
            
            return f"Successfully created new tool: {tool_name}. It is now available for use."
        except Exception as e:
            return f"Error creating tool: {e}"

    def load_custom_tools(self) -> dict:
        """Loads all custom tools from the manifest."""
        print("[ToolForge] Loading custom tools...")
        custom_tools = {}
        try:
            with open(self.manifest_path, 'r') as f:
                manifest = json.load(f)
            
            for tool_name, info in manifest.items():
                spec = importlib.util.spec_from_file_location(tool_name, info["filepath"])
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                # Assuming the tool is an instantiated class in the module
                custom_tools[tool_name] = getattr(module, tool_name)()
                print(f"  - Loaded tool: {tool_name}")
        except Exception as e:
            print(f"Error loading custom tools: {e}")
        return custom_tools
