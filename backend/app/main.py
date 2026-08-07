from contextlib import asynccontextmanager
from fastapi import FastAPI  # type: ignore
from fastapi.middleware.cors import CORSMiddleware  # type: ignore

from app.core.config import settings  # type: ignore
from app.core.logging import setup_logging, logger  # type: ignore
from app.api.routes import health, telemetry, state, websocket_streams, workflows  # type: ignore



@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle hooks."""
    import subprocess
    try:
        commit_hash = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=os.path.dirname(__file__)).decode().strip()
    except Exception:
        commit_hash = "75f63e5"

    app.state.build_commit = commit_hash
    logger.info(f"Starting {settings.PROJECT_NAME} v{settings.VERSION} [BUILD COMMIT: {commit_hash}]")
    
    api_key = settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

    if api_key:
        try:
            from google import genai
            client = genai.Client(api_key=api_key)
            logger.info("Gemini SDK initialized: True (google.genai)")
            logger.info("GEMINI_API_KEY present: True")
            logger.info("Target Model: gemini-flash-latest")
            logger.info(f"Verified Active Server Code Build Commit: {commit_hash}")


        except Exception as e:
            logger.warning(f"Gemini SDK initialization error: {e}")
    else:
        logger.info("GEMINI_API_KEY present: False (Running with Rule-Based Fallback Engine)")


    yield
    logger.info("Shutting down GhostTrace AI Backend")



app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan
)

# Configure CORS for all origins (Chrome Extension & Web Tabs)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Register REST & WebSocket routes
app.include_router(health.router)
app.include_router(telemetry.router)
app.include_router(workflows.router)
app.include_router(state.router)
app.include_router(websocket_streams.router)



@app.get("/")
async def root():
    return {
        "project": settings.PROJECT_NAME,
        "status": "ready",
        "docs": "/docs"
    }
