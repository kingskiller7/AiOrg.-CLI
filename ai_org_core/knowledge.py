class KnowledgeBase:
    """Manages an agent's memory and learned information."""
    def __init__(self, agent_role: str):
        self.agent_role = agent_role
        self.memory = [] # Simple list-based memory for now

    def add(self, info: str):
        print(f"[{self.agent_role}] Learning: {info}")
        self.memory.append(info)

    def query(self, question: str) -> str:
        # In the future, this will use vector search.
        # For now, it returns a summary.
        return f"Knowledge base for {self.agent_role} contains {len(self.memory)} items."
