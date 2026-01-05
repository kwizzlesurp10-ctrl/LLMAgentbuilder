"""Database schema migration support."""
import sqlite3
from pathlib import Path
from typing import Optional, List, Callable
from datetime import datetime


class Migration:
    """Base class for database migrations."""
    
    def __init__(self, version: int, name: str):
        self.version = version
        self.name = name
    
    def up(self, conn: sqlite3.Connection):
        """Apply the migration."""
        raise NotImplementedError
    
    def down(self, conn: sqlite3.Connection):
        """Revert the migration."""
        raise NotImplementedError


class InitialMigration(Migration):
    """Initial database schema migration."""
    
    def __init__(self):
        super().__init__(version=1, name="initial_schema")
    
    def up(self, conn: sqlite3.Connection):
        """Create initial tables."""
        cursor = conn.cursor()
        
        # Articles table (existing)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS articles (
                id TEXT PRIMARY KEY,
                url TEXT NOT NULL,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        ''')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_articles_created_at ON articles(created_at)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_articles_url ON articles(url)')
        
        # Alerts table (existing)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                message TEXT NOT NULL,
                source_url TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        ''')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_alerts_created_at ON alerts(created_at)')
        
        # Workflow states table (new)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS workflow_states (
                id TEXT PRIMARY KEY,
                workflow_name TEXT NOT NULL,
                status TEXT NOT NULL,
                current_step TEXT,
                data TEXT,
                error_message TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                completed_at TEXT
            )
        ''')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_workflow_status ON workflow_states(status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_workflow_created_at ON workflow_states(created_at)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_workflow_name ON workflow_states(workflow_name)')
        
        # Workflow history table (new)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS workflow_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                workflow_id TEXT NOT NULL,
                status TEXT NOT NULL,
                step TEXT,
                message TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (workflow_id) REFERENCES workflow_states(id)
            )
        ''')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_history_workflow_id ON workflow_history(workflow_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_history_created_at ON workflow_history(created_at)')
        
        # Agent versions table (new)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS agent_versions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_name TEXT NOT NULL,
                version TEXT NOT NULL,
                code TEXT NOT NULL,
                description TEXT,
                created_at TEXT NOT NULL,
                created_by TEXT,
                is_active INTEGER DEFAULT 1
            )
        ''')
        cursor.execute('CREATE UNIQUE INDEX IF NOT EXISTS idx_agent_name_version ON agent_versions(agent_name, version)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_agent_active ON agent_versions(agent_name, is_active)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_agent_created_at ON agent_versions(created_at)')
        
        # Schema version table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS schema_version (
                version INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                applied_at TEXT NOT NULL
            )
        ''')
        
        conn.commit()
    
    def down(self, conn: sqlite3.Connection):
        """Drop all tables."""
        cursor = conn.cursor()
        cursor.execute('DROP TABLE IF EXISTS agent_versions')
        cursor.execute('DROP TABLE IF EXISTS workflow_history')
        cursor.execute('DROP TABLE IF EXISTS workflow_states')
        cursor.execute('DROP TABLE IF EXISTS alerts')
        cursor.execute('DROP TABLE IF EXISTS articles')
        cursor.execute('DROP TABLE IF EXISTS schema_version')
        conn.commit()


class MigrationManager:
    """Manages database schema migrations."""
    
    def __init__(self, db_path: str):
        self.db_path = Path(db_path)
        self.migrations: List[Migration] = [
            InitialMigration(),
        ]
    
    def get_current_version(self, conn: sqlite3.Connection) -> int:
        """Get the current schema version."""
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT MAX(version) FROM schema_version')
            result = cursor.fetchone()
            return result[0] if result[0] is not None else 0
        except sqlite3.OperationalError:
            # Table doesn't exist yet
            return 0
    
    def apply_migration(self, conn: sqlite3.Connection, migration: Migration):
        """Apply a single migration."""
        cursor = conn.cursor()
        
        try:
            # Apply the migration
            migration.up(conn)
            
            # Record it in schema_version
            cursor.execute('''
                INSERT INTO schema_version (version, name, applied_at)
                VALUES (?, ?, ?)
            ''', (migration.version, migration.name, datetime.now().isoformat()))
            
            conn.commit()
            print(f"Applied migration {migration.version}: {migration.name}")
        except Exception as e:
            conn.rollback()
            raise Exception(f"Failed to apply migration {migration.version}: {str(e)}")
    
    def migrate(self):
        """Apply all pending migrations."""
        # Ensure database directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Connect to database
        conn = sqlite3.connect(self.db_path)
        
        try:
            current_version = self.get_current_version(conn)
            
            # Apply pending migrations
            for migration in self.migrations:
                if migration.version > current_version:
                    self.apply_migration(conn, migration)
            
            print(f"Database schema up to date at version {self.get_current_version(conn)}")
        finally:
            conn.close()
    
    def rollback(self, target_version: int = 0):
        """Rollback migrations to a specific version."""
        conn = sqlite3.connect(self.db_path)
        
        try:
            current_version = self.get_current_version(conn)
            
            # Rollback migrations in reverse order
            for migration in reversed(self.migrations):
                if migration.version > target_version and migration.version <= current_version:
                    cursor = conn.cursor()
                    
                    try:
                        # Revert the migration
                        migration.down(conn)
                        
                        # Remove from schema_version
                        cursor.execute('DELETE FROM schema_version WHERE version = ?', (migration.version,))
                        conn.commit()
                        
                        print(f"Rolled back migration {migration.version}: {migration.name}")
                    except Exception as e:
                        conn.rollback()
                        raise Exception(f"Failed to rollback migration {migration.version}: {str(e)}")
        finally:
            conn.close()


def auto_migrate(db_path: str):
    """Automatically apply all pending migrations."""
    manager = MigrationManager(db_path)
    manager.migrate()
