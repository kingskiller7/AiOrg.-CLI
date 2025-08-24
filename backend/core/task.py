from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class Task:
    """A structure to define a task, its requirements, and its history."""
    description: str
    expected_output: str
    assigned_to: str # Role of the agent it should be assigned to
    history: List[str] = field(default_factory=list)
    action_history: List[str] = field(default_factory=list)
    original_description: Optional[str] = None
