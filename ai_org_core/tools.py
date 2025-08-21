from playwright.sync_api import sync_playwright

class BrowserTool:
    """A tool for browsing websites and scraping their content."""
    def __init__(self):
        # We can manage the playwright instance here
        pass

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
                # Limit the content to avoid overwhelming the LLM
                return content[:5000]
        except Exception as e:
            return f"Error browsing site: {e}"

# Instantiate a single browser tool for the application to use
browser_tool = BrowserTool()
