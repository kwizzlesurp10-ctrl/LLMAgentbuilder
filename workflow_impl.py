import sqlite3
import requests
import re
import uuid
from datetime import datetime
from typing import Dict, List, Optional

# Import the new database infrastructure
from llm_agent_builder.database import DatabaseManager, get_pool_manager

DB_PATH = "workflow.db"


class DatabaseManagerLegacy:
    """Legacy DatabaseManager wrapper for backward compatibility."""
    
    def __init__(self, db_path: str = DB_PATH):
        # Get a pool from the pool manager
        pool_manager = get_pool_manager()
        pool = pool_manager.get_pool(db_path=db_path, pool_size=5, max_overflow=10)
        
        # Use the new DatabaseManager
        self._db_manager = DatabaseManager(pool)
    
    def create_tables(self):
        """Tables are created automatically via migrations."""
        pass
    
    def insert_article(self, article: Dict[str, str]):
        """Insert an article using the new manager."""
        self._db_manager.insert_article(article)
        print(f"Stored article: {article['title']}")
    
    def insert_alert(self, title: str, message: str, source_url: str):
        """Insert an alert using the new manager."""
        self._db_manager.insert_alert(title, message, source_url)
        print(f"ALERT: {title} - {message}")
    
    def close(self):
        """Close is handled by the pool manager."""
        pass

class Scraper:
    def scrape(self, url: str) -> Optional[Dict[str, str]]:
        print(f"Scraping {url}...")
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            html = response.text
            
            # Simple regex extraction since BeautifulSoup is not available
            title_match = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
            title = title_match.group(1).strip() if title_match else "No Title"
            
            # Very basic content extraction (removing tags)
            content = re.sub(r'<[^>]+>', ' ', html)
            content = re.sub(r'\s+', ' ', content).strip()
            
            return {
                "id": str(uuid.uuid4()),
                "url": url,
                "title": title,
                "content": content[:5000], # Limit content size
                "created_at": datetime.now().isoformat()
            }
        except Exception as e:
            print(f"Failed to scrape {url}: {e}")
            return None

class Analyzer:
    def __init__(self, keywords: List[str]):
        self.keywords = keywords

    def analyze(self, article: Dict[str, str]) -> List[str]:
        found_keywords = []
        content = article.get('content', '').lower()
        title = article.get('title', '').lower()
        
        for keyword in self.keywords:
            if keyword.lower() in content or keyword.lower() in title:
                found_keywords.append(keyword)
        
        return found_keywords

class WorkflowController:
    def __init__(self):
        self.db = DatabaseManagerLegacy()
        self.scraper = Scraper()
        self.analyzer = Analyzer(keywords=["Artificial Intelligence", "LLM", "Python", "Agent"])

    def run(self, urls: List[str]):
        print("Starting workflow...")
        for url in urls:
            article = self.scraper.scrape(url)
            if article:
                self.db.insert_article(article)
                
                keywords = self.analyzer.analyze(article)
                if keywords:
                    for keyword in keywords:
                        self.db.insert_alert(
                            title="Keyword Detected",
                            message=f"Keyword '{keyword}' detected in {article['title']}",
                            source_url=article['url']
                        )
        self.db.close()
        print("Workflow completed.")

if __name__ == "__main__":
    urls_to_monitor = [
        "https://www.python.org",
        "https://huggingface.co"
    ]
    
    controller = WorkflowController()
    controller.run(urls_to_monitor)
