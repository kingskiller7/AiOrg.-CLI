import lancedb
from sentence_transformers import SentenceTransformer
import os

from .config import MEMORY_DIR

class KnowledgeBase:
    """Manages an agent's memory using a LanceDB vector store."""
    def __init__(self, agent_role: str, db_path: str = MEMORY_DIR):
        self.agent_role = agent_role
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        
        if not os.path.exists(db_path):
            os.makedirs(db_path)
            
        db = lancedb.connect(db_path)
        table_name = self.agent_role.lower().replace(' ', '_')
        
        try:
            self.table = db.open_table(table_name)
        except (FileNotFoundError, ValueError):
            # Table does not exist, create it
            schema = self.model.encode("").tolist()
            self.table = db.create_table(table_name, data=[{"vector": schema, "text": ""}])

    def add(self, info: str):
        """Adds a new piece of information to the knowledge base."""
        print(f"[{self.agent_role}] Learning: {info[:80]}...")
        vector = self.model.encode(info).tolist()
        self.table.add([{"vector": vector, "text": info}])

    def query(self, question: str, limit: int = 3) -> str:
        """Queries the knowledge base for relevant information."""
        print(f"[{self.agent_role}] Searching memory for: '{question[:80]}...'")
        query_vector = self.model.encode(question).tolist()
        results = self.table.search(query_vector).limit(limit).to_df()
        
        if results.empty:
            return "No relevant information found in memory."
        
        # Format results for the prompt
        formatted_results = "\n".join([f"- {row['text']}" for index, row in results.iterrows()])
        return formatted_results