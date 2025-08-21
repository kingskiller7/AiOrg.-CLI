from dataclasses import dataclass

@dataclass
class Task:
    """A structure to define a task and its requirements."""
    description: str
    expected_output: str
    assigned_to: str # Role of the agent it should be assigned to
