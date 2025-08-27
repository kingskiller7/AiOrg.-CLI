from .persona import Persona
import json

def create_agent(role: str, responsibilities: list[str], abilities: list[str], organization) -> str:
    """Creates a new agent in the organization."""
    if role in organization.agents:
        return json.dumps({"error": f"Agent {role} already exists."})

    new_persona = Persona(role=role, responsibilities=responsibilities, abilities=abilities)
    organization.add_agent(new_persona)
    
    return json.dumps({"status": f"Agent {role} created successfully."})
