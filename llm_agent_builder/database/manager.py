"""Database manager with connection pooling support."""
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from contextlib import contextmanager

from .pool import DatabasePool
from .migrations import auto_migrate


class DatabaseManager:
    """
    Database manager using connection pooling.
    
    This class implements the repository pattern and uses a connection pool
    for thread-safe, efficient database access.
    """
    
    def __init__(self, pool: DatabasePool):
        """
        Initialize database manager with a connection pool.
        
        Args:
            pool: DatabasePool instance to use for connections
        """
        self.pool = pool
        # Ensure schema is up to date
        auto_migrate(str(self.pool.db_path))
    
    @contextmanager
    def _transaction(self):
        """Context manager for database transactions."""
        with self.pool.acquire() as conn:
            try:
                yield conn
                conn.commit()
            except Exception:
                conn.rollback()
                raise
    
    # Article operations
    
    def insert_article(self, article: Dict[str, str]) -> str:
        """
        Insert an article into the database.
        
        Args:
            article: Dictionary with keys: id, url, title, content, created_at
            
        Returns:
            str: The article ID
        """
        with self._transaction() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR IGNORE INTO articles (id, url, title, content, created_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                article['id'],
                article['url'],
                article['title'],
                article['content'],
                article['created_at']
            ))
            return article['id']
    
    def get_article(self, article_id: str) -> Optional[Dict[str, Any]]:
        """
        Get an article by ID.
        
        Args:
            article_id: The article ID
            
        Returns:
            Optional[Dict]: Article data or None if not found
        """
        with self.pool.acquire() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM articles WHERE id = ?', (article_id,))
            row = cursor.fetchone()
            
            if row:
                return {
                    "id": row["id"],
                    "url": row["url"],
                    "title": row["title"],
                    "content": row["content"],
                    "created_at": row["created_at"],
                }
            return None
    
    def get_articles(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Get a list of articles.
        
        Args:
            limit: Maximum number of articles to return
            offset: Number of articles to skip
            
        Returns:
            List[Dict]: List of article dictionaries
        """
        with self.pool.acquire() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT * FROM articles ORDER BY created_at DESC LIMIT ? OFFSET ?',
                (limit, offset)
            )
            rows = cursor.fetchall()
            
            return [
                {
                    "id": row["id"],
                    "url": row["url"],
                    "title": row["title"],
                    "content": row["content"],
                    "created_at": row["created_at"],
                }
                for row in rows
            ]
    
    # Alert operations
    
    def insert_alert(self, title: str, message: str, source_url: str) -> int:
        """
        Insert an alert into the database.
        
        Args:
            title: Alert title
            message: Alert message
            source_url: Source URL for the alert
            
        Returns:
            int: The alert ID
        """
        with self._transaction() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO alerts (title, message, source_url, created_at)
                VALUES (?, ?, ?, ?)
            ''', (title, message, source_url, datetime.now().isoformat()))
            return cursor.lastrowid
    
    def get_alert(self, alert_id: int) -> Optional[Dict[str, Any]]:
        """
        Get an alert by ID.
        
        Args:
            alert_id: The alert ID
            
        Returns:
            Optional[Dict]: Alert data or None if not found
        """
        with self.pool.acquire() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM alerts WHERE id = ?', (alert_id,))
            row = cursor.fetchone()
            
            if row:
                return {
                    "id": row["id"],
                    "title": row["title"],
                    "message": row["message"],
                    "source_url": row["source_url"],
                    "created_at": row["created_at"],
                }
            return None
    
    def get_alerts(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Get a list of alerts.
        
        Args:
            limit: Maximum number of alerts to return
            offset: Number of alerts to skip
            
        Returns:
            List[Dict]: List of alert dictionaries
        """
        with self.pool.acquire() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT * FROM alerts ORDER BY created_at DESC LIMIT ? OFFSET ?',
                (limit, offset)
            )
            rows = cursor.fetchall()
            
            return [
                {
                    "id": row["id"],
                    "title": row["title"],
                    "message": row["message"],
                    "source_url": row["source_url"],
                    "created_at": row["created_at"],
                }
                for row in rows
            ]
    
    # Workflow operations
    
    def create_workflow(
        self,
        workflow_name: str,
        workflow_id: Optional[str] = None,
        initial_data: Optional[Dict] = None
    ) -> str:
        """
        Create a new workflow.
        
        Args:
            workflow_name: Name of the workflow
            workflow_id: Optional workflow ID (generated if not provided)
            initial_data: Optional initial workflow data
            
        Returns:
            str: The workflow ID
        """
        if workflow_id is None:
            workflow_id = str(uuid.uuid4())
        
        now = datetime.now().isoformat()
        data_json = json.dumps(initial_data) if initial_data else None
        
        with self._transaction() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO workflow_states 
                (id, workflow_name, status, current_step, data, error_message, created_at, updated_at, completed_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (workflow_id, workflow_name, "pending", None, data_json, None, now, now, None))
            
            # Add initial history entry
            cursor.execute('''
                INSERT INTO workflow_history (workflow_id, status, step, message, created_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (workflow_id, "pending", None, "Workflow created", now))
            
        return workflow_id
    
    def get_workflow_state(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """
        Get workflow state by ID.
        
        Args:
            workflow_id: The workflow ID
            
        Returns:
            Optional[Dict]: Workflow state or None if not found
        """
        with self.pool.acquire() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM workflow_states WHERE id = ?', (workflow_id,))
            row = cursor.fetchone()
            
            if row:
                return {
                    "id": row["id"],
                    "workflow_name": row["workflow_name"],
                    "status": row["status"],
                    "current_step": row["current_step"],
                    "data": json.loads(row["data"]) if row["data"] else None,
                    "error_message": row["error_message"],
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"],
                    "completed_at": row["completed_at"],
                }
            return None
    
    def update_workflow_state(
        self,
        workflow_id: str,
        status: Optional[str] = None,
        current_step: Optional[str] = None,
        data: Optional[Dict] = None,
        error_message: Optional[str] = None,
        add_history: bool = True
    ):
        """
        Update workflow state.
        
        Args:
            workflow_id: The workflow ID
            status: New status (optional)
            current_step: New current step (optional)
            data: New data (optional)
            error_message: Error message (optional)
            add_history: Whether to add a history entry
        """
        now = datetime.now().isoformat()
        
        with self._transaction() as conn:
            cursor = conn.cursor()
            
            # Build update query dynamically
            updates = []
            params = []
            
            if status is not None:
                updates.append("status = ?")
                params.append(status)
            
            if current_step is not None:
                updates.append("current_step = ?")
                params.append(current_step)
            
            if data is not None:
                updates.append("data = ?")
                params.append(json.dumps(data))
            
            if error_message is not None:
                updates.append("error_message = ?")
                params.append(error_message)
            
            # Always update updated_at
            updates.append("updated_at = ?")
            params.append(now)
            
            # Set completed_at if status is completed or failed
            if status in ("completed", "failed"):
                updates.append("completed_at = ?")
                params.append(now)
            
            params.append(workflow_id)
            
            query = f"UPDATE workflow_states SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, params)
            
            # Add history entry if requested
            if add_history:
                message = error_message if error_message else f"Updated to {status}" if status else "State updated"
                cursor.execute('''
                    INSERT INTO workflow_history (workflow_id, status, step, message, created_at)
                    VALUES (?, ?, ?, ?, ?)
                ''', (workflow_id, status or "unknown", current_step, message, now))
    
    def get_workflow_history(self, workflow_id: str) -> List[Dict[str, Any]]:
        """
        Get workflow history.
        
        Args:
            workflow_id: The workflow ID
            
        Returns:
            List[Dict]: List of history entries
        """
        with self.pool.acquire() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT * FROM workflow_history WHERE workflow_id = ? ORDER BY created_at ASC',
                (workflow_id,)
            )
            rows = cursor.fetchall()
            
            return [
                {
                    "id": row["id"],
                    "workflow_id": row["workflow_id"],
                    "status": row["status"],
                    "step": row["step"],
                    "message": row["message"],
                    "created_at": row["created_at"],
                }
                for row in rows
            ]
    
    def list_workflows(
        self,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        List workflows with optional filtering.
        
        Args:
            status: Filter by status (optional)
            limit: Maximum number of workflows to return
            offset: Number of workflows to skip
            
        Returns:
            List[Dict]: List of workflow states
        """
        with self.pool.acquire() as conn:
            cursor = conn.cursor()
            
            if status:
                cursor.execute(
                    'SELECT * FROM workflow_states WHERE status = ? ORDER BY created_at DESC LIMIT ? OFFSET ?',
                    (status, limit, offset)
                )
            else:
                cursor.execute(
                    'SELECT * FROM workflow_states ORDER BY created_at DESC LIMIT ? OFFSET ?',
                    (limit, offset)
                )
            
            rows = cursor.fetchall()
            
            return [
                {
                    "id": row["id"],
                    "workflow_name": row["workflow_name"],
                    "status": row["status"],
                    "current_step": row["current_step"],
                    "data": json.loads(row["data"]) if row["data"] else None,
                    "error_message": row["error_message"],
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"],
                    "completed_at": row["completed_at"],
                }
                for row in rows
            ]
    
    # Agent version operations
    
    def save_agent_version(
        self,
        agent_name: str,
        version: str,
        code: str,
        description: Optional[str] = None,
        created_by: Optional[str] = None
    ) -> int:
        """
        Save an agent version.
        
        Args:
            agent_name: Name of the agent
            version: Version string
            code: Agent code
            description: Optional description
            created_by: Optional creator identifier
            
        Returns:
            int: The agent version ID
        """
        with self._transaction() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO agent_versions 
                (agent_name, version, code, description, created_at, created_by, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                agent_name,
                version,
                code,
                description,
                datetime.now().isoformat(),
                created_by,
                1
            ))
            return cursor.lastrowid
    
    def get_agent_version(
        self,
        agent_name: str,
        version: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get an agent version.
        
        Args:
            agent_name: Name of the agent
            version: Version string (if None, returns latest active version)
            
        Returns:
            Optional[Dict]: Agent version data or None if not found
        """
        with self.pool.acquire() as conn:
            cursor = conn.cursor()
            
            if version:
                cursor.execute(
                    'SELECT * FROM agent_versions WHERE agent_name = ? AND version = ?',
                    (agent_name, version)
                )
            else:
                cursor.execute(
                    'SELECT * FROM agent_versions WHERE agent_name = ? AND is_active = 1 ORDER BY created_at DESC LIMIT 1',
                    (agent_name,)
                )
            
            row = cursor.fetchone()
            
            if row:
                return {
                    "id": row["id"],
                    "agent_name": row["agent_name"],
                    "version": row["version"],
                    "code": row["code"],
                    "description": row["description"],
                    "created_at": row["created_at"],
                    "created_by": row["created_by"],
                    "is_active": bool(row["is_active"]),
                }
            return None
    
    # Batch operations
    
    def insert_articles_batch(self, articles: List[Dict[str, str]]):
        """
        Insert multiple articles in a batch.
        
        Args:
            articles: List of article dictionaries
        """
        with self._transaction() as conn:
            cursor = conn.cursor()
            cursor.executemany('''
                INSERT OR IGNORE INTO articles (id, url, title, content, created_at)
                VALUES (?, ?, ?, ?, ?)
            ''', [
                (a['id'], a['url'], a['title'], a['content'], a['created_at'])
                for a in articles
            ])
    
    def insert_alerts_batch(self, alerts: List[Dict[str, str]]):
        """
        Insert multiple alerts in a batch.
        
        Args:
            alerts: List of alert dictionaries with keys: title, message, source_url
        """
        now = datetime.now().isoformat()
        with self._transaction() as conn:
            cursor = conn.cursor()
            cursor.executemany('''
                INSERT INTO alerts (title, message, source_url, created_at)
                VALUES (?, ?, ?, ?)
            ''', [
                (a['title'], a['message'], a['source_url'], now)
                for a in alerts
            ])
    
    def close(self):
        """Close the connection pool."""
        self.pool.close()
