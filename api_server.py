"""FastAPI bridge for LLM Edge Router frontend integration."""

from typing import Optional

from fastapi import FastAPI, HTTPException

from pydantic import BaseModel

from llm_edge_router import LLMEdgeRouter



from fastapi.responses import RedirectResponse, HTMLResponse


app = FastAPI(title="Edge LLM API", version="0.1.0")
router = LLMEdgeRouter()

# Serve static files (frontend) at root

# Enable CORS for separate frontend deployment
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://inspiring-elf-a080fa.netlify.app",
        "http://inspiring-elf-a080fa.netlify.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint: show a welcome message and link to docs
@app.get("/", response_class=HTMLResponse)
async def root():
        return """
        <h2>Edge LLM API is running 🚀</h2>
        <ul>
            <li>Try <a href='/docs'>Swagger UI</a> for interactive API docs.</li>
            <li>Health check: <a href='/api/health'>/api/health</a></li>
            <li>POST to <code>/api/route</code> or <code>/api/generate</code> with JSON.</li>
        </ul>
        """

# Redirect /docs to FastAPI docs (optional, but makes /docs always work)
@app.get("/docs", include_in_schema=False)
async def docs_redirect():
        return RedirectResponse("/redoc")


class RouteRequest(BaseModel):
    prompt: str
    context_length: int = 0
    task_type: str = "general"
    force_offline: bool = False
    max_latency_ms: Optional[int] = None


class GenerateRequest(BaseModel):
    prompt: str
    model_id: Optional[str] = None
    task_type: str = "general"
    context_length: int = 0
    force_offline: bool = False
    max_latency_ms: Optional[int] = None


@app.get("/api/health")
async def health() -> dict:
    return {"status": "ok"}


@app.post("/api/route")
async def route(req: RouteRequest) -> dict:
    try:
        decision = router.route_request(
            prompt=req.prompt,
            context_length=req.context_length,
            task_type=req.task_type,
            force_offline=req.force_offline,
            max_latency_ms=req.max_latency_ms,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {
        "selected_model": decision.selected_model,
        "reason": decision.reason,
        "tier": decision.tier.value,
        "estimated_cost": decision.estimated_cost,
        "estimated_latency_ms": decision.estimated_latency_ms,
    }


@app.post("/api/generate")
async def generate(req: GenerateRequest) -> dict:
    try:
        result = await router.generate(
            prompt=req.prompt,
            model_id=req.model_id,
            task_type=req.task_type,
            context_length=req.context_length,
            force_offline=req.force_offline,
            max_latency_ms=req.max_latency_ms,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return result
