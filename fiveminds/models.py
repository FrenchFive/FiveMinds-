"""
Data models for the Five Minds system
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum


class TicketStatus(Enum):
    """Status of a ticket in the system"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    NEEDS_REVIEW = "needs_review"


class TicketPriority(Enum):
    """Priority level for tickets"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class AcceptanceCriteria:
    """Acceptance criteria for a ticket"""
    description: str
    met: bool = False
    evidence: Optional[str] = None


@dataclass
class Ticket:
    """
    A ticket represents a single unit of work to be implemented by a Runner.
    """
    id: str
    title: str
    description: str
    acceptance_criteria: List[AcceptanceCriteria]
    status: TicketStatus = TicketStatus.PENDING
    priority: TicketPriority = TicketPriority.MEDIUM
    dependencies: List[str] = field(default_factory=list)
    assigned_runner: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RunnerResult:
    """
    Results from a Runner's execution of a ticket.
    """
    ticket_id: str
    success: bool
    diff: str
    logs: List[str]
    test_results: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    execution_time: float = 0.0


@dataclass
class ReviewResult:
    """
    Results from a Reviewer's analysis of Runner outputs.
    """
    ticket_id: str
    approved: bool
    feedback: str
    alignment_score: float  # 0.0 to 1.0
    follow_up_tickets: List[Ticket] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)


@dataclass
class RepositoryContext:
    """
    Context information about a repository.
    """
    path: str
    files: List[str]
    structure: Dict[str, Any]
    languages: List[str]
    frameworks: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Objective:
    """
    User's objective for the system to accomplish.
    """
    description: str
    requirements: List[str]
    constraints: List[str] = field(default_factory=list)
    success_metrics: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
