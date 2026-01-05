"""SQLAlchemy ORM models for the database."""
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey, Index
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Article(Base):
    """Article model matching existing schema."""
    
    __tablename__ = "articles"
    
    id = Column(String, primary_key=True)
    url = Column(Text, nullable=False)
    title = Column(Text, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(String, nullable=False)
    
    # Index for faster lookups
    __table_args__ = (
        Index("idx_articles_created_at", "created_at"),
        Index("idx_articles_url", "url"),
    )
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            "id": self.id,
            "url": self.url,
            "title": self.title,
            "content": self.content,
            "created_at": self.created_at,
        }


class Alert(Base):
    """Alert model matching existing schema."""
    
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(Text, nullable=False)
    message = Column(Text, nullable=False)
    source_url = Column(Text, nullable=False)
    created_at = Column(String, nullable=False)
    
    # Index for faster lookups
    __table_args__ = (
        Index("idx_alerts_created_at", "created_at"),
    )
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "message": self.message,
            "source_url": self.source_url,
            "created_at": self.created_at,
        }


class WorkflowState(Base):
    """Workflow state model for tracking workflow execution."""
    
    __tablename__ = "workflow_states"
    
    id = Column(String, primary_key=True)
    workflow_name = Column(String, nullable=False)
    status = Column(String, nullable=False)  # pending, running, completed, failed
    current_step = Column(String, nullable=True)
    data = Column(Text, nullable=True)  # JSON-encoded state data
    error_message = Column(Text, nullable=True)
    created_at = Column(String, nullable=False)
    updated_at = Column(String, nullable=False)
    completed_at = Column(String, nullable=True)
    
    # Relationship to history
    history_entries = relationship("WorkflowHistory", back_populates="workflow", cascade="all, delete-orphan")
    
    # Indexes for performance
    __table_args__ = (
        Index("idx_workflow_status", "status"),
        Index("idx_workflow_created_at", "created_at"),
        Index("idx_workflow_name", "workflow_name"),
    )
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            "id": self.id,
            "workflow_name": self.workflow_name,
            "status": self.status,
            "current_step": self.current_step,
            "data": self.data,
            "error_message": self.error_message,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "completed_at": self.completed_at,
        }


class WorkflowHistory(Base):
    """Workflow history for tracking state changes."""
    
    __tablename__ = "workflow_history"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    workflow_id = Column(String, ForeignKey("workflow_states.id"), nullable=False)
    status = Column(String, nullable=False)
    step = Column(String, nullable=True)
    message = Column(Text, nullable=True)
    created_at = Column(String, nullable=False)
    
    # Relationship to workflow
    workflow = relationship("WorkflowState", back_populates="history_entries")
    
    # Index for faster lookups
    __table_args__ = (
        Index("idx_history_workflow_id", "workflow_id"),
        Index("idx_history_created_at", "created_at"),
    )
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            "id": self.id,
            "workflow_id": self.workflow_id,
            "status": self.status,
            "step": self.step,
            "message": self.message,
            "created_at": self.created_at,
        }


class AgentVersion(Base):
    """Agent version model for versioning support."""
    
    __tablename__ = "agent_versions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_name = Column(String, nullable=False)
    version = Column(String, nullable=False)
    code = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(String, nullable=False)
    created_by = Column(String, nullable=True)
    is_active = Column(Integer, default=1)  # SQLite doesn't have boolean, use 0/1
    
    # Indexes for performance
    __table_args__ = (
        Index("idx_agent_name_version", "agent_name", "version", unique=True),
        Index("idx_agent_active", "agent_name", "is_active"),
        Index("idx_agent_created_at", "created_at"),
    )
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            "id": self.id,
            "agent_name": self.agent_name,
            "version": self.version,
            "code": self.code,
            "description": self.description,
            "created_at": self.created_at,
            "created_by": self.created_by,
            "is_active": bool(self.is_active),
        }
