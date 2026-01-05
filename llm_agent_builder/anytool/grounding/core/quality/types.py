"""
Data types for tool quality tracking.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import ClassVar, Dict, List, Optional, Any


@dataclass
class ExecutionRecord:
    """Single execution record."""
    timestamp: datetime
    success: bool
    execution_time_ms: float
    error_message: Optional[str] = None


@dataclass
class DescriptionQuality:
    """LLM-evaluated description quality."""
    clarity: float  # 0-1: Is the purpose and usage clear?
    completeness: float  # 0-1: Are inputs/outputs documented?
    evaluated_at: datetime
    reasoning: str = ""  # LLM's reasoning for the scores
    
    @property
    def overall_score(self) -> float:
        """Computed overall score (average of all dimensions)."""
        return (self.clarity + self.completeness) / 2


@dataclass
class ToolQualityRecord:
    """
    Complete quality record for a tool.
    
    Key: "{backend}:{server}:{tool_name}"
    """
    tool_key: str
    backend: str
    server: str
    tool_name: str
    
    # Execution stats
    total_calls: int = 0
    success_count: int = 0
    total_execution_time_ms: float = 0.0
    
    # Recent execution history (rolling window)
    recent_executions: List[ExecutionRecord] = field(default_factory=list)
    
    # Description quality (LLM-evaluated)
    description_quality: Optional[DescriptionQuality] = None
    
    # Metadata
    description_hash: Optional[str] = None
    first_seen: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    
    # Keep only recent N executions
    MAX_RECENT_EXECUTIONS: ClassVar[int] = 100
    
    @property
    def success_rate(self) -> float:
        """Overall success rate."""
        if self.total_calls == 0:
            return 0.0
        return self.success_count / self.total_calls
    
    @property
    def avg_execution_time_ms(self) -> float:
        """Average execution time."""
        if self.total_calls == 0:
            return 0.0
        return self.total_execution_time_ms / self.total_calls
    
    @property
    def recent_success_rate(self) -> float:
        """Success rate from recent executions."""
        if not self.recent_executions:
            return self.success_rate
        successes = sum(1 for e in self.recent_executions if e.success)
        return successes / len(self.recent_executions)
    
    @property
    def quality_score(self) -> float:
        """
        Adaptive quality score that balances success rate and description quality.
        
        As we gather more execution data, we trust actual performance more.
        - Few executions (< 3): Only use description quality
        - Some executions (3-10): Gradually increase weight of success rate
        - Many executions (>= 10): Heavily favor success rate (80%) over description (20%)
        
        Returns value between 0-1.
        """
        # Determine adaptive weights based on execution count
        if self.total_calls >= 10:
            # Sufficient data: trust actual performance
            success_weight = 0.8
            desc_weight = 0.2
        elif self.total_calls >= 3:
            # Partial data: gradually transition from description to performance
            # Linear interpolation from (3, 0.5) to (10, 0.8)
            ratio = (self.total_calls - 3) / 7.0
            success_weight = 0.5 + ratio * 0.3  # 0.5 → 0.8
            desc_weight = 0.5 - ratio * 0.3      # 0.5 → 0.2
        else:
            # Insufficient data: only use description quality
            success_weight = 0.0
            desc_weight = 1.0
        
        # Compute weighted score
        score = 0.0
        total_weight = 0.0
        
        if self.total_calls >= 3:
            score += self.recent_success_rate * success_weight
            total_weight += success_weight
        
        if self.description_quality:
            score += self.description_quality.overall_score * desc_weight
            total_weight += desc_weight
        
        if total_weight == 0:
            return 0.5  # Brand new tool with no data
        
        return score / total_weight
    
    def add_execution(self, record: ExecutionRecord) -> None:
        """Add execution record and update stats."""
        self.total_calls += 1
        self.total_execution_time_ms += record.execution_time_ms
        
        if record.success:
            self.success_count += 1
        
        self.recent_executions.append(record)
        
        # Trim to max size
        if len(self.recent_executions) > self.MAX_RECENT_EXECUTIONS:
            self.recent_executions = self.recent_executions[-self.MAX_RECENT_EXECUTIONS:]
        
        self.last_updated = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dict for persistence."""
        return {
            "tool_key": self.tool_key,
            "backend": self.backend,
            "server": self.server,
            "tool_name": self.tool_name,
            "total_calls": self.total_calls,
            "success_count": self.success_count,
            "total_execution_time_ms": self.total_execution_time_ms,
            "recent_executions": [
                {
                    "timestamp": e.timestamp.isoformat(),
                    "success": e.success,
                    "execution_time_ms": e.execution_time_ms,
                    "error_message": e.error_message,
                }
                for e in self.recent_executions
            ],
            "description_quality": {
                "clarity": self.description_quality.clarity,
                "completeness": self.description_quality.completeness,
                "evaluated_at": self.description_quality.evaluated_at.isoformat(),
                "reasoning": self.description_quality.reasoning,
            } if self.description_quality else None,
            "description_hash": self.description_hash,
            "first_seen": self.first_seen.isoformat(),
            "last_updated": self.last_updated.isoformat(),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ToolQualityRecord":
        """Deserialize from dict."""
        record = cls(
            tool_key=data["tool_key"],
            backend=data["backend"],
            server=data["server"],
            tool_name=data["tool_name"],
            total_calls=data.get("total_calls", 0),
            success_count=data.get("success_count", 0),
            total_execution_time_ms=data.get("total_execution_time_ms", 0.0),
            description_hash=data.get("description_hash"),
            first_seen=datetime.fromisoformat(data["first_seen"]),
            last_updated=datetime.fromisoformat(data["last_updated"]),
        )
        
        # Parse recent executions
        for e in data.get("recent_executions", []):
            record.recent_executions.append(ExecutionRecord(
                timestamp=datetime.fromisoformat(e["timestamp"]),
                success=e["success"],
                execution_time_ms=e["execution_time_ms"],
                error_message=e.get("error_message"),
            ))
        
        # Parse description quality
        dq = data.get("description_quality")
        if dq:
            record.description_quality = DescriptionQuality(
                clarity=dq.get("clarity", 0.5),  # Fallback for old data
                completeness=dq.get("completeness", 0.5),
                evaluated_at=datetime.fromisoformat(dq["evaluated_at"]),
                reasoning=dq.get("reasoning", ""),  # Optional field
            )
        
        return record
