"""Tests for database connection pooling."""
import pytest
import tempfile
import os
from pathlib import Path
import threading
import time

from llm_agent_builder.database.pool import DatabasePool, PoolManager, get_pool_manager


@pytest.fixture
def temp_db():
    """Create a temporary database file."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    yield db_path
    # Cleanup
    try:
        os.unlink(db_path)
    except:
        pass


@pytest.fixture
def pool(temp_db):
    """Create a database pool."""
    pool = DatabasePool(temp_db, pool_size=5, max_overflow=10)
    yield pool
    pool.close()


def test_pool_initialization(temp_db):
    """Test pool initialization."""
    pool = DatabasePool(temp_db, pool_size=5, max_overflow=10)
    assert pool.db_path == Path(temp_db)
    assert pool.pool_size == 5
    assert pool.max_overflow == 10
    pool.close()


def test_pool_acquire_connection(pool):
    """Test acquiring a connection from the pool."""
    with pool.acquire() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        assert result[0] == 1


def test_pool_connection_reuse(pool):
    """Test that connections are reused."""
    # Acquire and release a connection
    with pool.acquire() as conn1:
        conn1.execute("CREATE TABLE test (id INTEGER)")
    
    # Acquire another connection and verify table exists
    with pool.acquire() as conn2:
        cursor = conn2.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='test'")
        result = cursor.fetchone()
        assert result is not None


def test_pool_multiple_connections(pool):
    """Test acquiring multiple connections concurrently."""
    connections = []
    
    def acquire_connection():
        with pool.acquire() as conn:
            connections.append(conn)
            time.sleep(0.1)  # Hold the connection briefly
    
    threads = [threading.Thread(target=acquire_connection) for _ in range(3)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    
    assert len(connections) == 3


def test_pool_health_check(pool):
    """Test pool health check."""
    assert pool.health_check() is True


def test_pool_statistics(pool):
    """Test pool statistics."""
    # Acquire and release a connection
    with pool.acquire() as conn:
        pass
    
    stats = pool.get_stats()
    assert "connections_acquired" in stats
    assert "connections_released" in stats
    assert stats["connections_acquired"] > 0
    assert stats["connections_released"] > 0


def test_pool_connection_error_handling(pool):
    """Test error handling in connection acquisition."""
    try:
        with pool.acquire() as conn:
            # Simulate an error
            raise ValueError("Test error")
    except ValueError:
        pass
    
    # Pool should still be functional
    assert pool.health_check() is True


def test_pool_manager_get_pool(temp_db):
    """Test pool manager."""
    manager = PoolManager()
    
    pool1 = manager.get_pool(temp_db)
    pool2 = manager.get_pool(temp_db)
    
    # Should return the same pool instance
    assert pool1 is pool2
    
    manager.close_all()


def test_pool_manager_multiple_databases():
    """Test pool manager with multiple databases."""
    manager = PoolManager()
    
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f1:
        db1 = f1.name
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f2:
        db2 = f2.name
    
    try:
        pool1 = manager.get_pool(db1)
        pool2 = manager.get_pool(db2)
        
        # Should be different pools
        assert pool1 is not pool2
        
        # Both should be healthy
        health = manager.health_check_all()
        assert len(health) == 2
        assert all(health.values())
        
    finally:
        manager.close_all()
        try:
            os.unlink(db1)
            os.unlink(db2)
        except:
            pass


def test_global_pool_manager():
    """Test global pool manager singleton."""
    manager1 = get_pool_manager()
    manager2 = get_pool_manager()
    
    # Should be the same instance
    assert manager1 is manager2


def test_pool_concurrent_access(pool):
    """Test concurrent access to the pool."""
    errors = []
    
    def worker():
        try:
            with pool.acquire() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                assert result[0] == 1
                time.sleep(0.01)  # Simulate work
        except Exception as e:
            errors.append(e)
    
    # Create many threads to stress test the pool
    threads = [threading.Thread(target=worker) for _ in range(20)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    
    # No errors should occur
    assert len(errors) == 0
    
    # Check statistics
    stats = pool.get_stats()
    assert stats["connections_acquired"] >= 20
    assert stats["errors"] == 0


def test_pool_row_factory(pool):
    """Test that row_factory is set correctly."""
    with pool.acquire() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 as num")
        row = cursor.fetchone()
        # Should be able to access by name
        assert row["num"] == 1


def test_pool_transaction_rollback(pool):
    """Test transaction rollback on error."""
    with pool.acquire() as conn:
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE test (id INTEGER)")
        conn.commit()
    
    try:
        with pool.acquire() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO test (id) VALUES (1)")
            # Simulate an error before commit
            raise ValueError("Test error")
    except ValueError:
        pass
    
    # Check that the insert was rolled back
    with pool.acquire() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM test")
        count = cursor.fetchone()[0]
        assert count == 0


def test_pool_wal_mode(pool):
    """Test that WAL mode is enabled."""
    with pool.acquire() as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA journal_mode")
        mode = cursor.fetchone()[0]
        assert mode.upper() == "WAL"
