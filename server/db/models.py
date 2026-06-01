import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Integer, Float, Text, Enum, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import declarative_base, Mapped, mapped_column, relationship
import enum

Base = declarative_base()

class SessionStatus(str, enum.Enum):
    running = "running"
    completed = "completed"
    failed = "failed"

class ResearchSession(Base):
    __tablename__ = "research_sessions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    query: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[SessionStatus] = mapped_column(Enum(SessionStatus), nullable=False)
    
    sub_questions: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    findings: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    critique: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    
    retry_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    final_report: Mapped[str | None] = mapped_column(Text, nullable=True)
    confidence_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    
    follow_up_questions: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    sources: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    steps = relationship("ResearchStep", back_populates="session", cascade="all, delete-orphan")

class ResearchStep(Base):
    __tablename__ = "research_steps"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("research_sessions.id"), nullable=False)
    
    step_number: Mapped[int] = mapped_column(Integer, nullable=False)
    node_name: Mapped[str] = mapped_column(Text, nullable=False)
    sub_question: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    input_data: Mapped[dict] = mapped_column(JSONB, nullable=False)
    output_data: Mapped[dict] = mapped_column(JSONB, nullable=False)
    duration_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    session = relationship("ResearchSession", back_populates="steps")
