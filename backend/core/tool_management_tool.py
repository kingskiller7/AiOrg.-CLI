def assign_tool(agent_role: str, tool_name: str, organization) -> str:
    """Assigns a tool to an agent."""
    if agent_role not in organization.agents:
        return f"Agent {agent_role} not found."
    
    if tool_name not in organization.tools:
        return f"Tool {tool_name} not found."

    organization.agents[agent_role].tools[tool_name] = organization.tools[tool_name]
    return f"Tool {tool_name} assigned to agent {agent_role}."
