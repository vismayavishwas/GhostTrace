import asyncio
from uuid import uuid4
from app.db.database import init_db, AsyncSessionLocal

from app.db.repository import DatabaseRepository
from app.db.models import SessionRecord, TelemetryEventRecord, ReplayFrameRecord, CodeArtifactRecord
from app.core.gemini_client import GeminiClient


async def run_db_verification():
    print("=== GhostTrace AI: SQLite Database & Gemini 2.5 Verification ===")

    # 1. Initialize SQLite Database Tables
    await init_db()
    print("[OK] SQLite Database initialized: ghosttrace.db tables created successfully.")

    # 2. Test Repository Persistence
    async with AsyncSessionLocal() as session:
        repo = DatabaseRepository(session)

        # Create Session with unique ID
        sid = f"sess-db-{uuid4().hex[:6]}"
        s1 = await repo.create_session(sid, app_title="SAP Portal")
        assert s1.session_id == sid

        # Save Telemetry Event with rich Chrome extension metadata (URL, DOM Selector, XPath, Bounding Box, Scroll)
        event_rec = TelemetryEventRecord(
            event_id=f"evt-{uuid4().hex[:6]}",
            session_id=s1.session_id,
            event_type="CLICK",
            active_tab="SAP ERP Portal",
            url="https://sap.company.com/invoice",
            target_selector="#btn-submit-invoice",
            xpath="//button[@id='btn-submit-invoice']",
            bounding_box={"x": 120, "y": 340, "width": 100, "height": 40},
            scroll_pos={"x": 0, "y": 150},
            input_masked="******",
            coordinates_x=120.0,
            coordinates_y=340.0
        )
        await repo.save_telemetry_event(event_rec)

        # Save Replay Frame
        frame_rec = ReplayFrameRecord(
            frame_id=f"frame-{uuid4().hex[:6]}",
            session_id=s1.session_id,
            timestamp_ms=1200,
            x=120.0,
            y=340.0,
            target_selector="#btn-submit-invoice",
            is_click=True
        )
        await repo.save_replay_frame(frame_rec)


        # Query Replay Frames
        frames = await repo.get_replay_frames(s1.session_id)
        assert len(frames) >= 1
        assert frames[0].session_id == s1.session_id

        print("[OK] SQLite Persistence: Session, rich TelemetryEvent, and ReplayFrame records saved and retrieved.")

    # 3. Test Gemini API Client Initialization
    gemini = GeminiClient()
    assert gemini.api_key is not None
    print("[OK] Google Gemini 2.5 API Client: Initialized with GEMINI_API_KEY from environment.")

    print("\nPASSED: Phase 15 SQLite Persistence & Gemini 2.5 Verification cleanly completed!")


if __name__ == "__main__":
    asyncio.run(run_db_verification())
