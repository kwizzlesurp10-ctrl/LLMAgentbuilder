"""Tests for concurrent database access."""
import pytest
import tempfile
import os
import threading
import time
from datetime import datetime

from llm_agent_builder.database.pool import DatabasePool
from llm_agent_builder.database.manager import DatabaseManager


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
def db_manager(temp_db):
    """Create a database manager with connection pool."""
    pool = DatabasePool(temp_db, pool_size=10, max_overflow=20)
    manager = DatabaseManager(pool)
    yield manager
    manager.close()


def test_concurrent_article_inserts(db_manager):
    """Test concurrent article insertions."""
    errors = []
    
    def insert_article(i):
        try:
            article = {
                "id": f"article-{i}",
                "url": f"https://example.com/{i}",
                "title": f"Article {i}",
                "content": f"Content {i}",
                "created_at": datetime.now().isoformat(),
            }
            db_manager.insert_article(article)
        except Exception as e:
            errors.append(e)
    
    # Create many threads inserting concurrently
    threads = [threading.Thread(target=insert_article, args=(i,)) for i in range(50)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    
    # No errors should occur
    assert len(errors) == 0
    
    # All articles should be inserted
    articles = db_manager.get_articles(limit=100)
    assert len(articles) == 50


def test_concurrent_alert_inserts(db_manager):
    """Test concurrent alert insertions."""
    errors = []
    
    def insert_alert(i):
        try:
            db_manager.insert_alert(
                title=f"Alert {i}",
                message=f"Message {i}",
                source_url=f"https://example.com/{i}"
            )
        except Exception as e:
            errors.append(e)
    
    threads = [threading.Thread(target=insert_alert, args=(i,)) for i in range(30)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    
    assert len(errors) == 0
    
    alerts = db_manager.get_alerts(limit=100)
    assert len(alerts) == 30


def test_concurrent_workflow_operations(db_manager):
    """Test concurrent workflow creation and updates."""
    errors = []
    workflow_ids = []
    
    def create_and_update_workflow(i):
        try:
            # Create workflow
            workflow_id = db_manager.create_workflow(
                workflow_name=f"workflow-{i}",
                initial_data={"index": i}
            )
            workflow_ids.append(workflow_id)
            
            # Update workflow
            db_manager.update_workflow_state(
                workflow_id=workflow_id,
                status="running",
                current_step=f"step-{i}"
            )
            
            # Update again
            db_manager.update_workflow_state(
                workflow_id=workflow_id,
                status="completed"
            )
        except Exception as e:
            errors.append(e)
    
    threads = [threading.Thread(target=create_and_update_workflow, args=(i,)) for i in range(20)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    
    assert len(errors) == 0
    assert len(workflow_ids) == 20
    
    # Verify all workflows are in completed state
    workflows = db_manager.list_workflows(status="completed")
    assert len(workflows) == 20


def test_concurrent_read_and_write(db_manager):
    """Test concurrent reads and writes."""
    errors = []
    
    # Insert initial data
    for i in range(10):
        article = {
            "id": f"init-{i}",
            "url": f"https://example.com/{i}",
            "title": f"Article {i}",
            "content": f"Content {i}",
            "created_at": datetime.now().isoformat(),
        }
        db_manager.insert_article(article)
    
    def read_articles():
        try:
            for _ in range(10):
                articles = db_manager.get_articles(limit=20)
                assert len(articles) >= 10
                time.sleep(0.01)
        except Exception as e:
            errors.append(e)
    
    def write_articles(start_idx):
        try:
            for i in range(5):
                article = {
                    "id": f"new-{start_idx}-{i}",
                    "url": f"https://example.com/{start_idx}/{i}",
                    "title": f"New Article {start_idx}-{i}",
                    "content": f"New Content {start_idx}-{i}",
                    "created_at": datetime.now().isoformat(),
                }
                db_manager.insert_article(article)
                time.sleep(0.01)
        except Exception as e:
            errors.append(e)
    
    # Mix of readers and writers
    readers = [threading.Thread(target=read_articles) for _ in range(5)]
    writers = [threading.Thread(target=write_articles, args=(i,)) for i in range(5)]
    
    all_threads = readers + writers
    for t in all_threads:
        t.start()
    for t in all_threads:
        t.join()
    
    assert len(errors) == 0


def test_concurrent_workflow_history_access(db_manager):
    """Test concurrent access to workflow history."""
    errors = []
    
    # Create a workflow
    workflow_id = db_manager.create_workflow(workflow_name="test_workflow")
    
    def update_workflow(step_num):
        try:
            for i in range(5):
                db_manager.update_workflow_state(
                    workflow_id=workflow_id,
                    status="running",
                    current_step=f"thread-{step_num}-step-{i}"
                )
                time.sleep(0.01)
        except Exception as e:
            errors.append(e)
    
    def read_workflow_history():
        try:
            for _ in range(10):
                history = db_manager.get_workflow_history(workflow_id)
                assert len(history) > 0
                time.sleep(0.01)
        except Exception as e:
            errors.append(e)
    
    # Mix of updaters and readers
    updaters = [threading.Thread(target=update_workflow, args=(i,)) for i in range(3)]
    readers = [threading.Thread(target=read_workflow_history) for _ in range(3)]
    
    all_threads = updaters + readers
    for t in all_threads:
        t.start()
    for t in all_threads:
        t.join()
    
    assert len(errors) == 0
    
    # Verify history was recorded
    history = db_manager.get_workflow_history(workflow_id)
    assert len(history) >= 15  # 3 threads * 5 updates + initial


def test_concurrent_batch_operations(db_manager):
    """Test concurrent batch operations."""
    errors = []
    
    def batch_insert_articles(batch_num):
        try:
            articles = [
                {
                    "id": f"batch-{batch_num}-{i}",
                    "url": f"https://example.com/{batch_num}/{i}",
                    "title": f"Batch {batch_num} Article {i}",
                    "content": f"Batch {batch_num} Content {i}",
                    "created_at": datetime.now().isoformat(),
                }
                for i in range(10)
            ]
            db_manager.insert_articles_batch(articles)
        except Exception as e:
            errors.append(e)
    
    threads = [threading.Thread(target=batch_insert_articles, args=(i,)) for i in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    
    assert len(errors) == 0
    
    # Should have 50 articles (5 batches * 10 articles)
    articles = db_manager.get_articles(limit=100)
    batch_articles = [a for a in articles if a["id"].startswith("batch-")]
    assert len(batch_articles) == 50


def test_connection_pool_stress(db_manager):
    """Stress test the connection pool with many concurrent operations."""
    errors = []
    operations_completed = []
    
    def mixed_operations(thread_id):
        try:
            # Insert article
            article = {
                "id": f"stress-{thread_id}",
                "url": f"https://example.com/{thread_id}",
                "title": f"Stress Article {thread_id}",
                "content": f"Stress Content {thread_id}",
                "created_at": datetime.now().isoformat(),
            }
            db_manager.insert_article(article)
            
            # Read articles
            articles = db_manager.get_articles(limit=10)
            
            # Create workflow
            workflow_id = db_manager.create_workflow(
                workflow_name=f"stress-workflow-{thread_id}"
            )
            
            # Update workflow
            db_manager.update_workflow_state(
                workflow_id=workflow_id,
                status="completed"
            )
            
            # Insert alert
            db_manager.insert_alert(
                title=f"Stress Alert {thread_id}",
                message=f"Stress Message {thread_id}",
                source_url=f"https://example.com/{thread_id}"
            )
            
            operations_completed.append(thread_id)
        except Exception as e:
            errors.append((thread_id, e))
    
    # Create many threads
    num_threads = 50
    threads = [threading.Thread(target=mixed_operations, args=(i,)) for i in range(num_threads)]
    
    start_time = time.time()
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    elapsed = time.time() - start_time
    
    print(f"\nStress test completed in {elapsed:.2f} seconds")
    print(f"Operations completed: {len(operations_completed)}/{num_threads}")
    print(f"Errors: {len(errors)}")
    
    # No errors should occur
    assert len(errors) == 0
    assert len(operations_completed) == num_threads
    
    # Verify data integrity
    articles = db_manager.get_articles(limit=100)
    stress_articles = [a for a in articles if a["id"].startswith("stress-")]
    assert len(stress_articles) == num_threads
    
    workflows = db_manager.list_workflows()
    stress_workflows = [w for w in workflows if w["workflow_name"].startswith("stress-workflow-")]
    assert len(stress_workflows) == num_threads


def test_long_running_concurrent_operations(db_manager):
    """Test long-running concurrent operations."""
    errors = []
    
    def long_running_operation(thread_id):
        try:
            for i in range(10):
                # Create workflow
                workflow_id = db_manager.create_workflow(
                    workflow_name=f"long-{thread_id}-{i}"
                )
                
                # Multiple updates
                for step in range(3):
                    db_manager.update_workflow_state(
                        workflow_id=workflow_id,
                        status="running",
                        current_step=f"step-{step}"
                    )
                    time.sleep(0.01)
                
                # Complete workflow
                db_manager.update_workflow_state(
                    workflow_id=workflow_id,
                    status="completed"
                )
        except Exception as e:
            errors.append((thread_id, e))
    
    threads = [threading.Thread(target=long_running_operation, args=(i,)) for i in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    
    assert len(errors) == 0
    
    # Should have 50 workflows (5 threads * 10 workflows)
    workflows = db_manager.list_workflows()
    long_workflows = [w for w in workflows if w["workflow_name"].startswith("long-")]
    assert len(long_workflows) == 50
