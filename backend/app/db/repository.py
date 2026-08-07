from typing import List, Optional
from sqlalchemy import select, delete  # type: ignore
from sqlalchemy.ext.asyncio import AsyncSession  # type: ignore
from app.db.models import (
    SessionRecord,
    TelemetryEventRecord,
    WorkflowCandidateRecord,
    WorkflowDNARecord,
    ReplayFrameRecord,
    CodeArtifactRecord,
    PatchHistoryRecord,
    ApprovalRecord,
)


class DatabaseRepository:
    """Async repository managing SQLite persistence for GhostTrace AI."""
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_session(self, session_id: str, app_title: str = "Web App") -> SessionRecord:
        existing = await self.session.execute(
            select(SessionRecord).where(SessionRecord.session_id == session_id)
        )
        found = existing.scalar_one_or_none()
        if found:
            return found

        rec = SessionRecord(session_id=session_id, app_title=app_title)
        self.session.add(rec)
        await self.session.commit()
        return rec


    async def save_telemetry_event(self, rec: TelemetryEventRecord) -> TelemetryEventRecord:
        self.session.add(rec)
        await self.session.commit()
        return rec

    async def save_candidate(self, rec: WorkflowCandidateRecord) -> WorkflowCandidateRecord:
        self.session.add(rec)
        await self.session.commit()
        return rec

    async def save_replay_frame(self, rec: ReplayFrameRecord) -> ReplayFrameRecord:
        self.session.add(rec)
        await self.session.commit()
        return rec

    async def get_replay_frames(self, session_id: str) -> List[ReplayFrameRecord]:
        result = await self.session.execute(
            select(ReplayFrameRecord).where(ReplayFrameRecord.session_id == session_id).order_by(ReplayFrameRecord.timestamp_ms)
        )
        return list(result.scalars().all())

    async def save_code_artifact(self, rec: CodeArtifactRecord) -> CodeArtifactRecord:
        self.session.add(rec)
        await self.session.commit()
        return rec

    async def save_patch_history(self, rec: PatchHistoryRecord) -> PatchHistoryRecord:
        self.session.add(rec)
        await self.session.commit()
        return rec

    async def save_approval(self, rec: ApprovalRecord) -> ApprovalRecord:
        self.session.add(rec)
        await self.session.commit()
        return rec

    async def clear_all_telemetry_and_candidates(self) -> None:
        await self.session.execute(delete(TelemetryEventRecord))
        await self.session.execute(delete(WorkflowCandidateRecord))
        await self.session.commit()
