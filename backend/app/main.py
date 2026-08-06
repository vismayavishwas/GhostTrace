from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import setup_logging, logger
from app.api.routes import health, telemetry, state, websocket_streams, workflows



@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle hooks."""
    setup_logging()
    logger.info(f"Starting {settings.PROJECT_NAME} v{settings.VERSION}")
    
    import os
    api_key = settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

    if api_key:
        try:
            from google import genai
            client = genai.Client(api_key=api_key)
            logger.info("Gemini SDK initialized: True (google.genai)")
            logger.info("GEMINI_API_KEY present: True")
            logger.info("Target Model: gemini-flash-latest")

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
