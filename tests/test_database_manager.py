"""Tests for database manager operations."""
import pytest
import tempfile
import os
import json
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
    except (OSError, FileNotFoundError):
        pass


@pytest.fixture
def db_manager(temp_db):
    """Create a database manager."""
    pool = DatabasePool(temp_db, pool_size=5)
    manager = DatabaseManager(pool)
    yield manager
    manager.close()


def test_manager_initialization(temp_db):
    """Test manager initialization."""
    pool = DatabasePool(temp_db, pool_size=5)
    manager = DatabaseManager(pool)
    assert manager.pool is not None
    manager.close()


def test_insert_and_get_article(db_manager):
    """Test inserting and retrieving an article."""
    article = {
        "id": "test-123",
        "url": "https://example.com",
        "title": "Test Article",
        "content": "Test content",
        "created_at": datetime.now().isoformat(),
    }
    
    article_id = db_manager.insert_article(article)
    assert article_id == "test-123"
    
    retrieved = db_manager.get_article("test-123")
    assert retrieved is not None
    assert retrieved["id"] == "test-123"
    assert retrieved["title"] == "Test Article"


def test_get_nonexistent_article(db_manager):
    """Test retrieving a non-existent article."""
    result = db_manager.get_article("nonexistent")
    assert result is None


def test_get_articles_list(db_manager):
    """Test getting a list of articles."""
    # Insert multiple articles
    for i in range(5):
        article = {
            "id": f"test-{i}",
            "url": f"https://example.com/{i}",
            "title": f"Article {i}",
            "content": f"Content {i}",
            "created_at": datetime.now().isoformat(),
        }
        db_manager.insert_article(article)
    
    articles = db_manager.get_articles(limit=10)
    assert len(articles) == 5


def test_insert_and_get_alert(db_manager):
    """Test inserting and retrieving an alert."""
    alert_id = db_manager.insert_alert(
        title="Test Alert",
        message="Test message",
        source_url="https://example.com"
    )
    
    assert alert_id > 0
    
    alert = db_manager.get_alert(alert_id)
    assert alert is not None
    assert alert["title"] == "Test Alert"
    assert alert["message"] == "Test message"


def test_get_alerts_list(db_manager):
    """Test getting a list of alerts."""
    # Insert multiple alerts
    for i in range(3):
        db_manager.insert_alert(
            title=f"Alert {i}",
            message=f"Message {i}",
            source_url=f"https://example.com/{i}"
        )
    
    alerts = db_manager.get_alerts(limit=10)
    assert len(alerts) == 3


def test_create_workflow(db_manager):
    """Test creating a workflow."""
    workflow_id = db_manager.create_workflow(
        workflow_name="test_workflow",
        initial_data={"key": "value"}
    )
    
    assert workflow_id is not None
    
    workflow = db_manager.get_workflow_state(workflow_id)
    assert workflow is not None
    assert workflow["workflow_name"] == "test_workflow"
    assert workflow["status"] == "pending"
    assert workflow["data"]["key"] == "value"


def test_update_workflow_state(db_manager):
    """Test updating workflow state."""
    workflow_id = db_manager.create_workflow(workflow_name="test_workflow")
    
    db_manager.update_workflow_state(
        workflow_id=workflow_id,
        status="running",
        current_step="step1",
        data={"progress": 50}
    )
    
    workflow = db_manager.get_workflow_state(workflow_id)
    assert workflow["status"] == "running"
    assert workflow["current_step"] == "step1"
    assert workflow["data"]["progress"] == 50


def test_workflow_history(db_manager):
    """Test workflow history tracking."""
    workflow_id = db_manager.create_workflow(workflow_name="test_workflow")
    
    # Update workflow multiple times
    db_manager.update_workflow_state(workflow_id, status="running", current_step="step1")
    db_manager.update_workflow_state(workflow_id, status="running", current_step="step2")
    db_manager.update_workflow_state(workflow_id, status="completed")
    
    history = db_manager.get_workflow_history(workflow_id)
    assert len(history) >= 4  # Created + 3 updates
    assert history[0]["status"] == "pending"  # First entry is creation


def test_list_workflows(db_manager):
    """Test listing workflows."""
    # Create multiple workflows
    db_manager.create_workflow(workflow_name="workflow1")
    db_manager.create_workflow(workflow_name="workflow2")
    db_manager.create_workflow(workflow_name="workflow3")
    
    workflows = db_manager.list_workflows()
    assert len(workflows) == 3


def test_list_workflows_by_status(db_manager):
    """Test filtering workflows by status."""
    wf1 = db_manager.create_workflow(workflow_name="workflow1")
    wf2 = db_manager.create_workflow(workflow_name="workflow2")
    
    db_manager.update_workflow_state(wf1, status="completed")
    
    completed = db_manager.list_workflows(status="completed")
    pending = db_manager.list_workflows(status="pending")
    
    assert len(completed) == 1
    assert len(pending) == 1


def test_save_and_get_agent_version(db_manager):
    """Test saving and retrieving agent versions."""
    version_id = db_manager.save_agent_version(
        agent_name="TestAgent",
        version="1.0.0",
        code="print('hello')",
        description="Test agent",
        created_by="test_user"
    )
    
    assert version_id > 0
    
    version = db_manager.get_agent_version("TestAgent", "1.0.0")
    assert version is not None
    assert version["agent_name"] == "TestAgent"
    assert version["version"] == "1.0.0"
    assert version["code"] == "print('hello')"


def test_get_latest_agent_version(db_manager):
    """Test getting the latest active agent version."""
    # Save multiple versions
    db_manager.save_agent_version("TestAgent", "1.0.0", "code1")
    db_manager.save_agent_version("TestAgent", "1.1.0", "code2")
    db_manager.save_agent_version("TestAgent", "2.0.0", "code3")
    
    # Get latest version (no version specified)
    latest = db_manager.get_agent_version("TestAgent")
    assert latest is not None
    assert latest["version"] == "2.0.0"
    assert latest["code"] == "code3"


def test_batch_insert_articles(db_manager):
    """Test batch inserting articles."""
    articles = [
        {
            "id": f"batch-{i}",
            "url": f"https://example.com/{i}",
            "title": f"Batch Article {i}",
            "content": f"Batch content {i}",
            "created_at": datetime.now().isoformat(),
        }
        for i in range(10)
    ]
    
    db_manager.insert_articles_batch(articles)
    
    retrieved_articles = db_manager.get_articles(limit=20)
    batch_articles = [a for a in retrieved_articles if a["id"].startswith("batch-")]
    assert len(batch_articles) == 10


def test_batch_insert_alerts(db_manager):
    """Test batch inserting alerts."""
    alerts = [
        {
            "title": f"Batch Alert {i}",
            "message": f"Batch message {i}",
            "source_url": f"https://example.com/{i}"
        }
        for i in range(5)
    ]
    
    db_manager.insert_alerts_batch(alerts)
    
    retrieved_alerts = db_manager.get_alerts(limit=20)
    assert len(retrieved_alerts) >= 5


def test_workflow_error_handling(db_manager):
    """Test workflow error handling."""
    workflow_id = db_manager.create_workflow(workflow_name="test_workflow")
    
    db_manager.update_workflow_state(
        workflow_id=workflow_id,
        status="failed",
        error_message="Something went wrong"
    )
    
    workflow = db_manager.get_workflow_state(workflow_id)
    assert workflow["status"] == "failed"
    assert workflow["error_message"] == "Something went wrong"
    assert workflow["completed_at"] is not None


def test_transaction_isolation(db_manager):
    """Test transaction isolation."""
    article = {
        "id": "trans-test",
        "url": "https://example.com",
        "title": "Transaction Test",
        "content": "Test content",
        "created_at": datetime.now().isoformat(),
    }
    
    # Insert article
    db_manager.insert_article(article)
    
    # Article should be retrievable
    retrieved = db_manager.get_article("trans-test")
    assert retrieved is not None


def test_workflow_pagination(db_manager):
    """Test workflow pagination."""
    # Create many workflows
    for i in range(15):
        db_manager.create_workflow(workflow_name=f"workflow{i}")
    
    # Get first page
    page1 = db_manager.list_workflows(limit=5, offset=0)
    assert len(page1) == 5
    
    # Get second page
    page2 = db_manager.list_workflows(limit=5, offset=5)
    assert len(page2) == 5
    
    # Workflows should be different
    page1_ids = {w["id"] for w in page1}
    page2_ids = {w["id"] for w in page2}
    assert len(page1_ids.intersection(page2_ids)) == 0


def test_article_duplicate_handling(db_manager):
    """Test handling of duplicate article IDs."""
    article = {
        "id": "dup-test",
        "url": "https://example.com",
        "title": "Original",
        "content": "Original content",
        "created_at": datetime.now().isoformat(),
    }
    
    db_manager.insert_article(article)
    
    # Try to insert duplicate (should be ignored)
    duplicate = article.copy()
    duplicate["title"] = "Modified"
    db_manager.insert_article(duplicate)
    
    # Should still have original
    retrieved = db_manager.get_article("dup-test")
    assert retrieved["title"] == "Original"
