from dataclasses import dataclass, field
from typing import List, Dict

@dataclass
class Persona:
    """Defines the identity, character, and capabilities of an AI Agent."""
    role: str
    responsibilities: List[str]
    views: List[str] = field(default_factory=list)
    emotions: List[str] = field(default_factory=list)
    abilities: List[str] = field(default_factory=list) # e.g., tool names
    knowledge_summary: str = ""
