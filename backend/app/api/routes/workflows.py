import logging
from typing import List, Dict, Any
from fastapi import APIRouter
from app.orchestration.nodes import get_global_pattern_discovery

logger = logging.getLogger("ghosttrace.api.workflows")

router = APIRouter(prefix="/api/v1/workflows", tags=["Workflows & Candidates"])


@router.get("")
async def get_discovered_workflows() -> List[Dict[str, Any]]:
    """Returns discovered WorkflowCandidate records."""
    pattern_agent = get_global_pattern_discovery()
    candidates = pattern_agent.get_discovered_candidates()
    return [c.model_dump() for c in candidates]
