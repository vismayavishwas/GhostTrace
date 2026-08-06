from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, Boolean, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.db.database import Base


class SessionRecord(Base):
    __tablename__ = "sessions"

    session_id = Column(String, primary_key=True)
    app_title = Column(String, default="Web Application")
    status = Column(String, default="ACTIVE")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    telemetry_events = relationship("TelemetryEventRecord", back_populates="session", cascade="all, delete-orphan")
    replay_frames = relationship("ReplayFrameRecord", back_populates="session", cascade="all, delete-orphan")


class TelemetryEventRecord(Base):
    __tablename__ = "telemetry_events"

    event_id = Column(String, primary_key=True)
    session_id = Column(String, ForeignKey("sessions.session_id"), nullable=False)
    event_type = Column(String, nullable=False)
    active_tab = Column(String, nullable=True)
    url = Column(String, nullable=True)
    target_selector = Column(String, nullable=True)
    xpath = Column(String, nullable=True)
    bounding_box = Column(JSON, nullable=True)
    scroll_pos = Column(JSON, nullable=True)
    input_masked = Column(String, nullable=True)
    coordinates_x = Column(Float, default=0.0)
    coordinates_y = Column(Float, default=0.0)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    session = relationship("SessionRecord", back_populates="telemetry_events")


class WorkflowCandidateRecord(Base):
    __tablename__ = "workflow_candidates"

    candidate_id = Column(String, primary_key=True)
    session_id = Column(String, nullable=True)
    name = Column(String, nullable=False)
    observed_steps = Column(JSON, nullable=False)
    occurrence_count = Column(Integer, default=1)
    confidence_score = Column(Float, default=0.5)
    success_rate = Column(Float, default=1.0)
    discovered_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class WorkflowDNARecord(Base):
    __tablename__ = "workflow_dna"

    workflow_id = Column(String, primary_key=True)
    candidate_id = Column(String, nullable=True)
    name = Column(String, nullable=False)
    steps_json = Column(JSON, nullable=False)
    applications = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class ReplayFrameRecord(Base):
    __tablename__ = "replay_frames"

    frame_id = Column(String, primary_key=True)
    session_id = Column(String, ForeignKey("sessions.session_id"), nullable=False)
    timestamp_ms = Column(Integer, nullable=False)
    x = Column(Float, nullable=False)
    y = Column(Float, nullable=False)
    viewport_width = Column(Integer, default=1920)
    viewport_height = Column(Integer, default=1080)
    scroll_x = Column(Integer, default=0)
    scroll_y = Column(Integer, default=0)
    target_selector = Column(String, nullable=True)
    is_click = Column(Boolean, default=False)

    session = relationship("SessionRecord", back_populates="replay_frames")


class CodeArtifactRecord(Base):
    __tablename__ = "code_artifacts"

    artifact_id = Column(String, primary_key=True)
    workflow_id = Column(String, nullable=False)
    source_code = Column(Text, nullable=False)
    step_map_json = Column(JSON, nullable=False)
    version = Column(Integer, default=1)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class PatchHistoryRecord(Base):
    __tablename__ = "patch_history"

    patch_id = Column(String, primary_key=True)
    artifact_id = Column(String, nullable=False)
    attempt_number = Column(Integer, nullable=False)
    failing_line = Column(Integer, nullable=True)
    repair_prompt = Column(Text, nullable=True)
    patched_code = Column(Text, nullable=False)
    status = Column(String, default="PASS")
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class ApprovalRecord(Base):
    __tablename__ = "approvals"

    approval_id = Column(String, primary_key=True)
    workflow_id = Column(String, nullable=False)
    approved_by = Column(String, default="Manager")
    status = Column(String, default="APPROVED")
    estimated_time_saved = Column(String, default="4.2 hrs/wk")
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
