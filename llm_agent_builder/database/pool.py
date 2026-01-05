"""Database connection pooling implementation using SQLAlchemy."""
import sqlite3
import threading
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Optional, Dict, Any
from sqlalchemy import create_engine, pool, event
from sqlalchemy.engine import Engine


class DatabasePool:
    """Thread-safe database connection pool using SQLAlchemy QueuePool."""
    
    def __init__(
        self,
        db_path: str,
        pool_size: int = 10,
        max_overflow: int = 20,
        pool_timeout: int = 30,
        pool_recycle: int = 3600,
    ):
        """
        Initialize database connection pool.
        
        Args:
            db_path: Path to SQLite database file
            pool_size: Number of connections to maintain in the pool
            max_overflow: Maximum number of connections to create beyond pool_size
            pool_timeout: Timeout in seconds when getting a connection from the pool
            pool_recycle: Time in seconds to recycle connections (prevents stale connections)
        """
        self.db_path = Path(db_path)
        self.pool_size = pool_size
        self.max_overflow = max_overflow
        self.pool_timeout = pool_timeout
        self.pool_recycle = pool_recycle
        
        # Ensure directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create SQLAlchemy engine with QueuePool
        self.engine = create_engine(
            f"sqlite:///{self.db_path}",
            poolclass=pool.QueuePool,
            pool_size=self.pool_size,
            max_overflow=self.max_overflow,
            pool_timeout=self.pool_timeout,
            pool_recycle=self.pool_recycle,
            connect_args={"check_same_thread": False},
            echo=False,
        )
        
        # Enable WAL mode for better concurrent access
        @event.listens_for(Engine, "connect")
        def set_sqlite_pragma(dbapi_conn, connection_record):
            # Set row factory
            dbapi_conn.row_factory = sqlite3.Row
            cursor = dbapi_conn.cursor()
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA synchronous=NORMAL")
            cursor.execute("PRAGMA busy_timeout=5000")
            cursor.close()
        
        self._lock = threading.Lock()
        self._stats: Dict[str, Any] = {
            "connections_created": 0,
            "connections_acquired": 0,
            "connections_released": 0,
            "errors": 0,
        }
    
    @contextmanager
    def acquire(self):
        """
        Acquire a connection from the pool.
        
        Yields:
            sqlite3.Connection: A database connection from the pool
            
        Raises:
            TimeoutError: If unable to acquire connection within pool_timeout
        """
        raw_conn = None
        try:
            # Get raw connection from pool
            raw_conn = self.engine.raw_connection()
            
            # Get underlying DBAPI connection
            dbapi_conn = raw_conn.driver_connection
            
            with self._lock:
                self._stats["connections_acquired"] += 1
            
            yield dbapi_conn
            
        except Exception as e:
            with self._lock:
                self._stats["errors"] += 1
            if raw_conn:
                try:
                    raw_conn.rollback()
                except:
                    pass
            raise
        finally:
            if raw_conn:
                try:
                    raw_conn.close()  # Returns connection to pool
                    with self._lock:
                        self._stats["connections_released"] += 1
                except Exception as e:
                    with self._lock:
                        self._stats["errors"] += 1
    
    def health_check(self) -> bool:
        """
        Check if the pool is healthy and can provide connections.
        
        Returns:
            bool: True if pool is healthy, False otherwise
        """
        try:
            with self.acquire() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                cursor.fetchone()
                return True
        except Exception:
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get connection pool statistics.
        
        Returns:
            dict: Statistics including connections created, acquired, released, and errors
        """
        with self._lock:
            stats = self._stats.copy()
        
        # Add pool info
        pool_info = self.engine.pool.status()
        stats["pool_status"] = pool_info
        stats["db_path"] = str(self.db_path)
        stats["pool_size"] = self.pool_size
        stats["max_overflow"] = self.max_overflow
        
        return stats
    
    def close(self):
        """Close all connections in the pool."""
        try:
            self.engine.dispose()
        except Exception:
            pass


class PoolManager:
    """Manages multiple database pools for different database files."""
    
    def __init__(self):
        self._pools: Dict[str, DatabasePool] = {}
        self._lock = threading.Lock()
    
    def get_pool(
        self,
        db_path: str,
        pool_size: int = 10,
        max_overflow: int = 20,
        pool_timeout: int = 30,
        pool_recycle: int = 3600,
    ) -> DatabasePool:
        """
        Get or create a pool for the specified database.
        
        Args:
            db_path: Path to database file
            pool_size: Number of connections in pool
            max_overflow: Maximum overflow connections
            pool_timeout: Connection acquisition timeout
            pool_recycle: Connection recycle time
            
        Returns:
            DatabasePool: The connection pool for the database
        """
        db_path = str(Path(db_path).resolve())
        
        with self._lock:
            if db_path not in self._pools:
                self._pools[db_path] = DatabasePool(
                    db_path=db_path,
                    pool_size=pool_size,
                    max_overflow=max_overflow,
                    pool_timeout=pool_timeout,
                    pool_recycle=pool_recycle,
                )
        
        return self._pools[db_path]
    
    def close_all(self):
        """Close all managed pools."""
        with self._lock:
            for pool in self._pools.values():
                pool.close()
            self._pools.clear()
    
    def health_check_all(self) -> Dict[str, bool]:
        """
        Check health of all managed pools.
        
        Returns:
            dict: Mapping of database path to health status
        """
        with self._lock:
            return {db_path: pool.health_check() for db_path, pool in self._pools.items()}


# Global pool manager instance
_pool_manager: Optional[PoolManager] = None


def get_pool_manager() -> PoolManager:
    """Get the global pool manager instance."""
    global _pool_manager
    if _pool_manager is None:
        _pool_manager = PoolManager()
    return _pool_manager
