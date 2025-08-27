import json
from default_api import google_web_search

class ResearchTool:
    """A tool for conducting research using Google Search."""

    def search(self, query: str) -> str:
        """
        Performs a web search using Google and returns the results in JSON format.
        Use this tool for any research or information gathering tasks.
        """
        print(f"[ResearchTool] Searching for: {query}...")
        try:
            result = google_web_search(query=query)
            return json.dumps({"result": result})
        except Exception as e:
            return json.dumps({"error": f"Error during web search: {e}"})

research_tool = ResearchTool()