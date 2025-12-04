import sqlite3
import requests
import re
import uuid
from datetime import datetime
from typing import Dict, List, Optional

DB_PATH = "workflow.db"

class DatabaseManager:
    def __init__(self, db_path: str = DB_PATH):
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS articles (
                id TEXT PRIMARY KEY,
                url TEXT,
                title TEXT,
                content TEXT,
                created_at TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                message TEXT,
                source_url TEXT,
                created_at TEXT
            )
        ''')
        self.conn.commit()

    def insert_article(self, article: Dict[str, str]):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR IGNORE INTO articles (id, url, title, content, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (article['id'], article['url'], article['title'], article['content'], article['created_at']))
        self.conn.commit()
        print(f"Stored article: {article['title']}")

    def insert_alert(self, title: str, message: str, source_url: str):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO alerts (title, message, source_url, created_at)
            VALUES (?, ?, ?, ?)
        ''', (title, message, source_url, datetime.now().isoformat()))
        self.conn.commit()
        print(f"ALERT: {title} - {message}")

    def close(self):
        self.conn.close()

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
        self.db = DatabaseManager()
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
