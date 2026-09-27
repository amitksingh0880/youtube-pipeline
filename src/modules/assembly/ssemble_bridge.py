"""
Ssemble Cloud Bridge: exposes local video via high-speed Cloudflare Tunnel
and submits it to Ssemble's AI clipping engine (https://app.ssemble.com).
Leverages user's active 1-year subscription with automatic local fallback.
Also supports direct YouTube long-form video clipping without local uploading.
"""

import os
import time
import shutil
import logging
import threading
import http.server
import socketserver
import subprocess
import requests
from pathlib import Path
from typing import Any, Dict, Optional
from src.core.config import settings
from src.core.ssemble_client import SsembleClient, SsembleAPIError

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
LOCAL_CLOUDFLARED = PROJECT_ROOT / "assets" / "bin" / "cloudflared.exe"


class FileServerThread(threading.Thread):
    """Simple single-file HTTP server thread for streaming video to Ssemble."""
    def __init__(self, file_path: str, port: int = 8899):
        super().__init__(daemon=True)
        self.file_path = file_path
        self.port = port
        self.server: Optional[socketserver.TCPServer] = None

    def run(self):
        file_dir = os.path.dirname(self.file_path)

        class CustomHandler(http.server.SimpleHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory=file_dir, **kwargs)

            def log_message(self, format, *args):
                pass  # Suppress noisy request logs

        try:
            # Allow port reuse to avoid 'Address already in use' during quick successive runs
            socketserver.TCPServer.allow_reuse_address = True
            with socketserver.TCPServer(("0.0.0.0", self.port), CustomHandler) as httpd:
                self.server = httpd
                httpd.serve_forever()
        except Exception as e:
            logger.debug(f"FileServerThread stopped: {e}")

    def stop(self):
        if self.server:
            try:
                self.server.shutdown()
                self.server.server_close()
            except Exception:
                pass


class SsembleBridge:
    def __init__(self, ssemble_client: Optional[SsembleClient] = None):
        self.client = ssemble_client or SsembleClient()

    def _get_cloudflared_path(self) -> Optional[str]:
        """Locates cloudflared executable on system PATH or in assets/bin/."""
        path = shutil.which("cloudflared")
        if path:
            return path
        if LOCAL_CLOUDFLARED.exists():
            return str(LOCAL_CLOUDFLARED)
        return None

    def polish_with_ssemble(
        self,
        local_video_path: str,
        output_path: str,
        template_id: Optional[str] = None,
        timeout: int = 900,
    ) -> Optional[str]:
        """
        Connects local video to Ssemble's clipping and captioning API via Cloudflare Tunnel.
        Applies Ssemble's cloud viral templates, sound effects, and licensed background music.
        """
        if not self.client.api_key:
            raise SsembleAPIError(
                "SSEMBLE_API_KEY is not configured in .env. "
                "Add your Ssemble API key to .env or use mode 'local-studio'."
            )

        cf_binary = self._get_cloudflared_path()
        if not cf_binary:
            raise SsembleAPIError(
                "Cloudflare Tunnel ('cloudflared') not found. "
                "Please place cloudflared.exe in assets/bin/ or install it on PATH."
            )

        port = 8899
        server = FileServerThread(local_video_path, port=port)
        server.start()
        time.sleep(1.0)

        tunnel_proc = None
        public_url = None
        try:
            # Launch cloudflared tunnel
            cmd = [cf_binary, "tunnel", "--url", f"http://127.0.0.1:{port}"]
            tunnel_proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
            )

            # Wait for public URL to appear in cloudflared stderr output
            for _ in range(40):
                line = tunnel_proc.stderr.readline() if tunnel_proc.stderr else ""
                if "trycloudflare.com" in line:
                    for part in line.split():
                        if part.startswith("https://") and "trycloudflare.com" in part:
                            clean_base = part.strip().rstrip("/")
                            public_url = f"{clean_base}/{os.path.basename(local_video_path)}"
                            break
                    if public_url:
                        break
                time.sleep(0.5)

            if not public_url:
                raise SsembleAPIError("Failed to obtain temporary public tunnel URL from cloudflared.")

            logger.info(f"Streaming rough cut to Ssemble via tunnel: {public_url}")

            # Submit rough cut to Ssemble AI Clipping API
            create_resp = self.client.create_short(
                file_url=public_url,
                template_id=template_id or settings.ssemble_default_template,
                preferred_length="under60sec",
            )
            request_id = create_resp.get("requestId")
            if not request_id:
                raise SsembleAPIError(f"No requestId returned by Ssemble API: {create_resp}")

            logger.info(f"Ssemble processing short (requestId: {request_id}). Polling status...")

            # Poll for completion
            results = self.client.wait_for_completion(request_id, timeout=timeout)
            shorts = results.get("shorts", [])
            if not shorts:
                raise SsembleAPIError("Ssemble returned 0 shorts for this video.")

            # Pick highest viral score short
            best = max(shorts, key=lambda s: s.get("viral_score", 0))
            video_url = best.get("video_url")
            if not video_url:
                raise SsembleAPIError("No download video_url provided in Ssemble response.")

            # Download finished short
            logger.info(f"Downloading polished Short from Ssemble: {video_url}")
            resp = requests.get(video_url, stream=True, timeout=60)
            resp.raise_for_status()
            with open(output_path, "wb") as f:
                for chunk in resp.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        f.write(chunk)

            logger.info(f"Ssemble polished Short downloaded successfully to {output_path}")
            return output_path

        finally:
            if tunnel_proc:
                try:
                    tunnel_proc.terminate()
                    tunnel_proc.wait(timeout=3)
                except Exception:
                    pass
            server.stop()

    def clip_youtube_video(
        self,
        youtube_url: str,
        output_path: str,
        template_id: Optional[str] = None,
        timeout: int = 900,
    ) -> Dict[str, Any]:
        """
        Directly submits a long-form YouTube video URL to Ssemble's AI clipping engine.
        No local file streaming or tunnel needed. Ssemble parses the YouTube video,
        detects viral hooks, applies auto-framing & Hormozi captions, and returns clips.
        """
        if not self.client.api_key:
            raise SsembleAPIError("SSEMBLE_API_KEY is not configured in .env.")

        logger.info(f"Submitting YouTube URL to Ssemble AI Clipper: {youtube_url}")
        create_resp = self.client.create_short(
            url=youtube_url,
            template_id=template_id or settings.ssemble_default_template,
            preferred_length="under60sec",
        )
        request_id = create_resp.get("requestId")
        if not request_id:
            raise SsembleAPIError(f"No requestId returned by Ssemble API: {create_resp}")

        logger.info(f"Ssemble clipping long-form video (requestId: {request_id}). Polling...")
        results = self.client.wait_for_completion(request_id, timeout=timeout)
        shorts = results.get("shorts", [])
        if not shorts:
            raise SsembleAPIError("Ssemble returned 0 clipped shorts for this YouTube video.")

        best = max(shorts, key=lambda s: s.get("viral_score", 0))
        video_url = best.get("video_url")
        if not video_url:
            raise SsembleAPIError("No video_url in Ssemble clipped result.")

        resp = requests.get(video_url, stream=True, timeout=60)
        resp.raise_for_status()
        with open(output_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    f.write(chunk)

        return {
            "output_path": output_path,
            "viral_score": best.get("viral_score", 90),
            "hook_title": best.get("title", ""),
            "all_clips": shorts,
        }
