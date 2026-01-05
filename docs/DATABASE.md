# Database Architecture

## Overview

LLM Agent Builder uses a production-ready database layer with connection pooling, transaction management, and thread-safe operations. The implementation is built on SQLAlchemy for connection pooling and SQLite for data storage.

## Architecture Components

### 1. Connection Pooling (`pool.py`)

The connection pool manages database connections efficiently:

- **DatabasePool**: Main connection pool class using SQLAlchemy's QueuePool
- **PoolManager**: Manages multiple pools for different database files
- **Features**:
  - Thread-safe connection management
  - Connection lifecycle management (acquire, release, close)
  - Health checks and monitoring
  - Configurable pool size and timeouts
  - WAL (Write-Ahead Logging) mode for better concurrency

#### Configuration Options

```python
pool = DatabasePool(
    db_path="workflow.db",
    pool_size=10,           # Base number of connections
    max_overflow=20,        # Additional connections beyond pool_size
    pool_timeout=30,        # Seconds to wait for connection
    pool_recycle=3600       # Recycle connections after 1 hour
)
```

### 2. ORM Models (`models.py`)

SQLAlchemy ORM models define the database schema:

#### Article
Stores scraped web articles.

```python
- id: TEXT PRIMARY KEY
- url: TEXT
- title: TEXT
- content: TEXT
- created_at: TEXT
```

Indexes: `created_at`, `url`

#### Alert
Stores keyword detection alerts.

```python
- id: INTEGER PRIMARY KEY AUTOINCREMENT
- title: TEXT
- message: TEXT
- source_url: TEXT
- created_at: TEXT
```

Indexes: `created_at`

#### WorkflowState
Tracks workflow execution state (NEW).

```python
- id: TEXT PRIMARY KEY
- workflow_name: TEXT
- status: TEXT (pending, running, completed, failed)
- current_step: TEXT
- data: TEXT (JSON-encoded)
- error_message: TEXT
- created_at: TEXT
- updated_at: TEXT
- completed_at: TEXT
```

Indexes: `status`, `created_at`, `workflow_name`

#### WorkflowHistory
Tracks workflow state changes.

```python
- id: INTEGER PRIMARY KEY AUTOINCREMENT
- workflow_id: TEXT (FOREIGN KEY)
- status: TEXT
- step: TEXT
- message: TEXT
- created_at: TEXT
```

Indexes: `workflow_id`, `created_at`

#### AgentVersion
Stores agent code versions.

```python
- id: INTEGER PRIMARY KEY AUTOINCREMENT
- agent_name: TEXT
- version: TEXT
- code: TEXT
- description: TEXT
- created_at: TEXT
- created_by: TEXT
- is_active: INTEGER (0/1)
```

Indexes: `agent_name + version` (unique), `agent_name + is_active`, `created_at`

### 3. Database Manager (`manager.py`)

The DatabaseManager implements the repository pattern with connection pooling.

For detailed API documentation, see the inline documentation in the source files.

## Usage Examples

### Basic Usage

```python
from llm_agent_builder.database import DatabasePool, DatabaseManager

# Create pool
pool = DatabasePool("workflow.db", pool_size=10)

# Create manager
manager = DatabaseManager(pool)

# Insert article
article = {
    "id": "123",
    "url": "https://example.com",
    "title": "Example",
    "content": "Content",
    "created_at": datetime.now().isoformat()
}
manager.insert_article(article)

# Get article
article = manager.get_article("123")
```

### FastAPI Integration

```python
from fastapi import FastAPI, Depends
from llm_agent_builder.database import get_db, DatabaseManager, initialize_database

app = FastAPI()

@app.on_event("startup")
async def startup():
    initialize_database("workflow.db", pool_size=10)

@app.on_event("shutdown")
async def shutdown():
    from llm_agent_builder.database import get_pool_manager
    get_pool_manager().close_all()

@app.post("/api/workflows")
async def create_workflow(
    workflow_name: str,
    db: DatabaseManager = Depends(get_db)
):
    workflow_id = db.create_workflow(workflow_name)
    return {"id": workflow_id}
```

## Connection Pool Tuning

### Pool Size Recommendations

**Small Applications (< 10 concurrent users):**
```yaml
pool_size: 5
max_overflow: 10
```

**Medium Applications (10-50 concurrent users):**
```yaml
pool_size: 10
max_overflow: 20
```

**Large Applications (50+ concurrent users):**
```yaml
pool_size: 20
max_overflow: 40
```

## Best Practices

1. **Use context managers**: Always use `with pool.acquire()` or `get_db()`
2. **Close resources**: Let the pool manager handle cleanup
3. **Batch operations**: Use batch methods for bulk inserts
4. **Proper indexing**: Query using indexed columns
5. **Error handling**: Catch and handle database exceptions
6. **Monitor stats**: Check pool statistics regularly
7. **Tune pool size**: Based on your application's needs

## Testing

Comprehensive test suite included:

- **test_database_pool.py**: Connection pooling (14 tests)
- **test_database_manager.py**: Manager operations (19 tests)
- **test_database_concurrent.py**: Concurrent access (8 tests)
- **test_database_transactions.py**: Transaction handling (13 tests)

Run tests:
```bash
pytest tests/test_database*.py -v
```
