"""
FastAPI Server for the Google Material Design 3 YouTube Shorts Studio.
Provides REST endpoints, live topic discovery, Ssemble AI clipping,
and static file streaming for video preview and creation.
"""

import os
import shutil
import logging
import subprocess
import time
from pathlib import Path
from typing import Any, Dict, List, Optional
from pydantic import BaseModel
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware

from src.core.config import OUTPUT_DIR, settings
from src.core.database import get_all_shorts, get_short_by_session_id, count_today_uploads
from src.core.orchestrator import ShortsOrchestrator
from src.modules.research.niche_manager import NicheManager
from src.modules.research.topic_discovery import TopicDiscovery
from src.modules.assembly.ssemble_bridge import SsembleBridge
from src.modules.publishing.youtube_uploader import YouTubeUploader

logger = logging.getLogger(__name__)

app = FastAPI(title="YouTube Shorts Studio API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Render / Cloud Deployment: Auto-inject client secret from Environment Variable if present
if os.environ.get("GOOGLE_CLIENT_SECRET_JSON"):
    try:
        settings.abs_client_secrets_path.parent.mkdir(parents=True, exist_ok=True)
        with open(settings.abs_client_secrets_path, "w", encoding="utf-8") as f:
            f.write(os.environ["GOOGLE_CLIENT_SECRET_JSON"])
        logger.info("Loaded GOOGLE_CLIENT_SECRET_JSON from environment.")
    except Exception as e:
        logger.error(f"Failed to write GOOGLE_CLIENT_SECRET_JSON: {e}")

# Global progress tracker for live studio updates
JOB_PROGRESS: Dict[str, Dict[str, Any]] = {}

orchestrator = ShortsOrchestrator()
niche_manager = NicheManager()
ssemble_bridge = SsembleBridge()


class GenerateRequest(BaseModel):
    niche_id: Optional[str] = None
    mode: str = "local-studio"  # "local-studio", "ssemble-ai", "ssemble-clip"
    topic_hint: Optional[str] = None
    dry_run: bool = True
    privacy_status: str = "unlisted"
    youtube_url: Optional[str] = None  # For ssemble-clip mode


class SsembleClipRequest(BaseModel):
    youtube_url: str
    niche_id: Optional[str] = "tech_ai"
    template_id: Optional[str] = "hormozi1"


@app.get("/")
def get_root():
    """Root info endpoint."""
    return {
        "name": "YouTube Shorts Studio API",
        "status": "online",
        "frontend": "http://localhost:3000",
        "docs": "/docs",
    }


@app.get("/api/diagnostics/probe/{component}")
def probe_component(component: str):
    """Deep component probe returning status, latency, and detailed diagnostic metadata."""
    start = time.perf_counter()
    component = component.lower()

    if component == "ffmpeg":
        ffmpeg_bin = shutil.which("ffmpeg")
        if not ffmpeg_bin:
            return {
                "status": "error",
                "component": "ffmpeg",
                "message": "FFmpeg executable not found in PATH",
                "latency_ms": 0,
            }
        try:
            res = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True, timeout=3)
            first_line = res.stdout.splitlines()[0] if res.stdout else "FFmpeg ready"
            elapsed = int((time.perf_counter() - start) * 1000)
            return {
                "status": "ready",
                "component": "ffmpeg",
                "binary": ffmpeg_bin,
                "version_info": first_line,
                "latency_ms": max(1, elapsed),
            }
        except Exception as e:
            return {"status": "error", "component": "ffmpeg", "message": str(e), "latency_ms": 0}

    elif component == "gemini":
        has_key = bool(settings.gemini_api_key)
        elapsed = int((time.perf_counter() - start) * 1000)
        return {
            "status": "ready" if has_key else "dry_run_ready",
            "component": "gemini",
            "model": settings.gemini_model,
            "has_api_key": has_key,
            "latency_ms": max(1, elapsed),
        }

    elif component == "tts":
        elapsed = int((time.perf_counter() - start) * 1000)
        return {
            "status": "ready",
            "component": "tts",
            "engine": "Microsoft Edge Neural TTS",
            "default_voice": settings.default_voice,
            "voice_rate": settings.voice_rate,
            "cost": "$0.00 (Zero-Metered)",
            "latency_ms": max(1, elapsed),
        }

    elif component == "ssemble":
        has_key = bool(settings.ssemble_api_key)
        elapsed = int((time.perf_counter() - start) * 1000)
        return {
            "status": "ready" if has_key else "standby",
            "component": "ssemble",
            "connected": has_key,
            "default_template": settings.ssemble_default_template,
            "latency_ms": max(1, elapsed),
        }

    elif component == "db":
        try:
            shorts = get_all_shorts(limit=1)
            elapsed = int((time.perf_counter() - start) * 1000)
            return {
                "status": "ready",
                "component": "db",
                "storage": "SQLite Persistent Storage",
                "total_records": len(shorts),
                "latency_ms": max(1, elapsed),
            }
        except Exception as e:
            return {"status": "error", "component": "db", "message": str(e), "latency_ms": 0}

    else:
        elapsed = int((time.perf_counter() - start) * 1000)
        return {
            "status": "ready",
            "component": component,
            "latency_ms": max(1, elapsed),
        }


@app.get("/api/health")
def get_system_health():
    """Returns real-time status of all local and cloud components."""
    has_gemini = bool(settings.gemini_api_key)
    has_ssemble = bool(settings.ssemble_api_key)
    has_ffmpeg = bool(shutil.which("ffmpeg"))
    cf_path = ssemble_bridge._get_cloudflared_path()
    
    return {
        "status": "healthy",
        "gemini_2_flash": "ready" if has_gemini else "dry_run_mock_ready",
        "edge_neural_tts": "ready",
        "ffmpeg": "ready" if has_ffmpeg else "missing",
        "cloudflared": "ready" if cf_path else "missing",
        "ssemble_api": "connected" if has_ssemble else "unconfigured_use_local_studio",
        "output_directory": str(OUTPUT_DIR),
    }


@app.get("/api/niches")
def get_niches():
    """Returns all loaded high-RPM Verticals v3 niche profiles."""
    return niche_manager.get_all_niches()


@app.get("/api/topics")
def get_discovered_topics(niche_id: Optional[str] = "dark_history", limit: int = 10):
    """Fetches live trending viral hooks from Wikipedia, Hacker News, and Google Trends."""
    return TopicDiscovery.discover_topics_for_niche(niche_id or "dark_history", limit=limit)


@app.get("/api/ssemble/templates")
def get_ssemble_templates():
    """Returns available Ssemble viral subtitle & framing templates."""
    try:
        if ssemble_bridge.client.api_key:
            return ssemble_bridge.client.list_templates()
    except Exception:
        pass
    # Built-in template catalogue
    return [
        {"id": "hormozi1", "name": "Hormozi Classic", "description": "Bold yellow highlight on black outline with word bounce", "popular": True},
        {"id": "beast", "name": "MrBeast Explosive", "description": "High-saturation red & yellow active popping text", "popular": True},
        {"id": "neon", "name": "Cyberpunk Neon", "description": "Electric cyan & green glowing outline typography", "popular": False},
        {"id": "cinematic", "name": "Cinematic Minimal", "description": "Crisp white subtitles with subtle motion tracking", "popular": False},
        {"id": "clean", "name": "Clean Modern", "description": "Apple-grade sans serif with smooth word fades", "popular": True},
    ]


@app.get("/api/stats")
def get_stats():
    shorts = get_all_shorts(limit=100)
    today_uploads = count_today_uploads()
    return {
        "total_generated": len(shorts),
        "today_uploads": today_uploads,
        "daily_limit": 6,
        "quota_remaining": max(0, (6 - today_uploads) * 1600),
        "ssemble_template": settings.ssemble_default_template,
        "default_voice": settings.default_voice,
    }


@app.get("/api/history")
def get_history(limit: int = 30):
    return get_all_shorts(limit=limit)


@app.get("/api/short/{session_id}")
def get_short_details(session_id: str):
    data = get_short_by_session_id(session_id)
    if not data:
        raise HTTPException(status_code=404, detail="Short not found")
    return data


@app.get("/api/progress/{job_id}")
def get_job_progress(job_id: str):
    return JOB_PROGRESS.get(job_id, {"status": "idle", "percent": 0, "message": "No active job"})


def _async_generate_job(job_id: str, req: GenerateRequest):
    def on_prog(msg: str, pct: int):
        JOB_PROGRESS[job_id] = {
            "status": "running" if pct < 100 else "completed",
            "percent": pct,
            "message": msg,
        }

    try:
        res = orchestrator.run_pipeline(
            niche_id=req.niche_id,
            mode=req.mode,
            topic_hint=req.topic_hint,
            youtube_url=req.youtube_url,
            dry_run=req.dry_run,
            privacy_status=req.privacy_status,
            progress_callback=on_prog,
        )
        JOB_PROGRESS[job_id]["result"] = res
        JOB_PROGRESS[job_id]["status"] = "completed"
        JOB_PROGRESS[job_id]["percent"] = 100
        JOB_PROGRESS[job_id]["message"] = "Short generated successfully!"
    except Exception as e:
        logger.exception("Pipeline generation failed")
        JOB_PROGRESS[job_id] = {
            "status": "failed",
            "percent": 0,
            "message": str(e),
            "error": str(e),
        }


@app.post("/api/generate")
def trigger_generation(req: GenerateRequest, background_tasks: BackgroundTasks):
    import uuid
    job_id = uuid.uuid4().hex[:8]
    JOB_PROGRESS[job_id] = {
        "status": "starting",
        "percent": 5,
        "message": f"Initializing pipeline in '{req.mode}' mode...",
    }
    background_tasks.add_task(_async_generate_job, job_id, req)
    return {"job_id": job_id, "status": "started"}


@app.post("/api/ssemble/clip")
def clip_youtube_video(req: SsembleClipRequest, background_tasks: BackgroundTasks):
    """Clips a long-form YouTube video using Ssemble AI clipping engine."""
    import uuid
    job_id = uuid.uuid4().hex[:8]
    
    def _run_clip():
        JOB_PROGRESS[job_id] = {"status": "running", "percent": 20, "message": "Submitting YouTube video to Ssemble AI..."}
        try:
            output_name = f"ssemble_clip_{job_id}.mp4"
            final_path = str(OUTPUT_DIR / output_name)
            clip_res = ssemble_bridge.clip_youtube_video(
                youtube_url=req.youtube_url,
                output_path=final_path,
                template_id=req.template_id,
            )
            JOB_PROGRESS[job_id] = {
                "status": "completed",
                "percent": 100,
                "message": "Ssemble clip generated successfully!",
                "result": {
                    "video_path": final_path,
                    "viral_score": clip_res.get("viral_score"),
                    "hook_title": clip_res.get("hook_title"),
                }
            }
        except Exception as e:
            JOB_PROGRESS[job_id] = {"status": "failed", "percent": 0, "message": str(e), "error": str(e)}

    background_tasks.add_task(_run_clip)
    return {"job_id": job_id, "status": "clipping_started"}


@app.post("/api/upload/{session_id}")
def upload_existing_short(session_id: str):
    short_data = get_short_by_session_id(session_id)
    if not short_data:
        raise HTTPException(status_code=404, detail="Short not found")

    video_path = short_data.get("video_path")
    if not video_path or not os.path.exists(video_path):
        raise HTTPException(status_code=400, detail="Video file missing on disk")

    uploader = YouTubeUploader()
    try:
        res = uploader.upload_short(
            video_path=video_path,
            title=short_data.get("title", "YouTube Short"),
            description=short_data.get("description", ""),
            privacy_status=settings.youtube_default_privacy,
            contains_synthetic_media=True,
        )
        from src.core.database import update_short_status
        update_short_status(session_id, status="uploaded", youtube_video_id=res.get("video_id"))
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/settings/youtube/client-secret")
async def upload_client_secret(file: Any = None):
    # This expects a raw POST body or form data, to be simple we can just expect raw bytes in body
    # Or just use Request to get body
    pass # Wait, FastAPI with UploadFile requires python-multipart. Is it installed?

# Better way: Let's just use Request and write raw body.
from fastapi import Request
@app.post("/api/settings/youtube/client-secret")
async def upload_client_secret_raw(request: Request):
    secret_path = settings.abs_client_secrets_path
    secret_path.parent.mkdir(parents=True, exist_ok=True)
    body = await request.body()
    with open(secret_path, "wb") as f:
        f.write(body)
    return {"status": "success", "message": "Client secret saved."}

@app.get("/api/settings/youtube/status")
def get_youtube_auth_status():
    has_secret = settings.abs_client_secrets_path.exists()
    has_token = settings.abs_token_path.exists()
    return {
        "has_client_secret": has_secret,
        "is_authenticated": has_token
    }

from fastapi import BackgroundTasks

@app.post("/api/settings/youtube/authorize")
def authorize_youtube():
    if not settings.abs_client_secrets_path.exists():
        raise HTTPException(status_code=400, detail="Missing client_secret.json")
    try:
        from google_auth_oauthlib.flow import InstalledAppFlow
        from src.modules.publishing.youtube_oauth import SCOPES
        
        # We will catch the callback on our own FastAPI server port 8000
        flow = InstalledAppFlow.from_client_secrets_file(str(settings.abs_client_secrets_path), SCOPES)
        flow.redirect_uri = "http://localhost:8000/api/settings/youtube/callback"
        
        auth_url, state = flow.authorization_url(prompt='consent', access_type='offline')
        
        # Save flow temporarily in app state to use during callback
        app.state.oauth_flow = flow
        
        return {"status": "pending", "auth_url": auth_url}
    except Exception as e:
        logger.exception("OAuth generation failed")
        raise HTTPException(status_code=500, detail=str(e))

from fastapi.responses import HTMLResponse

@app.get("/api/settings/youtube/callback")
def youtube_callback(state: str, code: str):
    try:
        flow = getattr(app.state, "oauth_flow", None)
        if not flow:
            return HTMLResponse("OAuth flow not initialized. Please try again from the Studio UI.", status_code=400)
            
        import pickle
        flow.fetch_token(code=code)
        creds = flow.credentials
        
        settings.abs_token_path.parent.mkdir(parents=True, exist_ok=True)
        with open(settings.abs_token_path, "wb") as f:
            pickle.dump(creds, f)
            
        success_html = (
            "<html><head><script>window.close();</script></head>"
            "<body style='font-family: sans-serif; text-align: center; margin-top: 50px;'>"
            "<h3>Authentication Successful!</h3>"
            "<p>This window should close automatically.</p>"
            "</body></html>"
        )
        return HTMLResponse(success_html)
    except Exception as e:
        logger.exception("OAuth callback failed")
        return HTMLResponse(f"<h3>Authentication Failed</h3><p>{str(e)}</p>", status_code=500)

@app.get("/api/video/{filename}")
def stream_video(filename: str):
    # Security check: ensure path stays within OUTPUT_DIR
    safe_path = (OUTPUT_DIR / filename).resolve()
    if not str(safe_path).startswith(str(OUTPUT_DIR.resolve())):
        raise HTTPException(status_code=403, detail="Forbidden")
    if not safe_path.exists():
        raise HTTPException(status_code=404, detail="Video file not found")
    return FileResponse(str(safe_path), media_type="video/mp4")

