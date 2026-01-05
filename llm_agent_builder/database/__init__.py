"""Database package for LLM Agent Builder."""
from contextlib import contextmanager
from typing import Optional, Generator

from .pool import DatabasePool, PoolManager, get_pool_manager
from .manager import DatabaseManager
from .models import Base, Article, Alert, WorkflowState, WorkflowHistory, AgentVersion
from .migrations import auto_migrate, MigrationManager

__all__ = [
    "DatabasePool",
    "PoolManager",
    "DatabaseManager",
    "get_pool_manager",
    "get_db",
    "auto_migrate",
    "MigrationManager",
    "Base",
    "Article",
    "Alert",
    "WorkflowState",
    "WorkflowHistory",
    "AgentVersion",
]

# Global database manager instance (for backward compatibility)
_global_db_manager: Optional[DatabaseManager] = None


def initialize_database(
    db_path: str = "workflow.db",
    pool_size: int = 10,
    max_overflow: int = 20,
    pool_timeout: int = 30,
    pool_recycle: int = 3600,
) -> DatabaseManager:
    """
    Initialize the global database manager.
    
    Args:
        db_path: Path to database file
        pool_size: Number of connections in pool
        max_overflow: Maximum overflow connections
        pool_timeout: Connection acquisition timeout
        pool_recycle: Connection recycle time
        
    Returns:
        DatabaseManager: The initialized database manager
    """
    global _global_db_manager
    
    pool_manager = get_pool_manager()
    pool = pool_manager.get_pool(
        db_path=db_path,
        pool_size=pool_size,
        max_overflow=max_overflow,
        pool_timeout=pool_timeout,
        pool_recycle=pool_recycle,
    )
    
    _global_db_manager = DatabaseManager(pool)
    return _global_db_manager


def get_global_db() -> Optional[DatabaseManager]:
    """
    Get the global database manager instance.
    
    Returns:
        Optional[DatabaseManager]: The global database manager or None if not initialized
    """
    return _global_db_manager


@contextmanager
def get_db(
    db_path: str = "workflow.db",
    pool_size: int = 10,
    max_overflow: int = 20,
    pool_timeout: int = 30,
    pool_recycle: int = 3600,
) -> Generator[DatabaseManager, None, None]:
    """
    Context manager for database access with dependency injection support.
    
    This is the recommended way to access the database in FastAPI endpoints.
    
    Usage:
        ```python
        from llm_agent_builder.database import get_db
        
        @app.post("/api/workflows")
        async def create_workflow(
            workflow: WorkflowCreate,
            db: DatabaseManager = Depends(get_db)
        ):
            workflow_id = db.create_workflow(workflow.name)
            return {"id": workflow_id}
        ```
    
    Args:
        db_path: Path to database file
        pool_size: Number of connections in pool
        max_overflow: Maximum overflow connections
        pool_timeout: Connection acquisition timeout
        pool_recycle: Connection recycle time
        
    Yields:
        DatabaseManager: A database manager instance
    """
    # Use global instance if available
    if _global_db_manager is not None:
        yield _global_db_manager
    else:
        # Create a new manager for this request
        pool_manager = get_pool_manager()
        pool = pool_manager.get_pool(
            db_path=db_path,
            pool_size=pool_size,
            max_overflow=max_overflow,
            pool_timeout=pool_timeout,
            pool_recycle=pool_recycle,
        )
        
        db_manager = DatabaseManager(pool)
        try:
            yield db_manager
        finally:
            # Don't close the pool, it's managed by the pool manager
            pass
