"""
Robust HTTP Client for the Ssemble AI Clipping API (https://aiclipping.ssemble.com/api/v1).
Leverages user's active 1-year Ssemble subscription for AI clipping, dynamic captions, and templates.
"""

import time
import requests
from typing import Any, Dict, List, Optional
from src.core.config import settings


class SsembleAPIError(Exception):
    """Custom exception for Ssemble API errors."""
    pass


class SsembleClient:
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key if api_key is not None else settings.ssemble_api_key
        self.base_url = (base_url or settings.ssemble_base_url).rstrip("/")
        if not self.api_key:
            # We don't fail at init so local-studio mode works without Ssemble key,
            # but API calls will fail with a clear message.
            pass

    @property
    def headers(self) -> Dict[str, str]:
        if not self.api_key:
            raise SsembleAPIError("SSEMBLE_API_KEY is not set in environment or .env file.")
        return {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def list_templates(self) -> List[Dict[str, Any]]:
        """Retrieves available caption/video templates (e.g. hormozi1, beast, neon)."""
        url = f"{self.base_url}/templates"
        resp = requests.get(url, headers=self.headers, timeout=30)
        if not resp.ok:
            raise SsembleAPIError(f"Failed to list templates ({resp.status_code}): {resp.text}")
        payload = resp.json().get("data", {})
        if isinstance(payload, dict):
            return payload.get("templates", [])
        return payload if isinstance(payload, list) else []

    def list_music(self) -> List[Dict[str, Any]]:
        """Retrieves list of available royalty-free music tracks."""
        url = f"{self.base_url}/music"
        resp = requests.get(url, headers=self.headers, timeout=30)
        if not resp.ok:
            raise SsembleAPIError(f"Failed to list music ({resp.status_code}): {resp.text}")
        payload = resp.json().get("data", {})
        if isinstance(payload, dict):
            return payload.get("music", [])
        return payload if isinstance(payload, list) else []

    def list_meme_hooks(self) -> List[Dict[str, Any]]:
        """Retrieves available viral meme hooks."""
        url = f"{self.base_url}/meme-hooks"
        resp = requests.get(url, headers=self.headers, timeout=30)
        if not resp.ok:
            raise SsembleAPIError(f"Failed to list meme hooks ({resp.status_code}): {resp.text}")
        payload = resp.json().get("data", {})
        if isinstance(payload, dict):
            return payload.get("memeHooks", [])
        return payload if isinstance(payload, list) else []

    def create_short(
        self,
        url: Optional[str] = None,
        file_url: Optional[str] = None,
        template_id: Optional[str] = None,
        preferred_length: str = "under60sec",
        language: str = "en",
        music: bool = False,
        music_name: Optional[str] = None,
        meme_hook: bool = False,
        meme_hook_name: Optional[str] = None,
        cta_enabled: bool = False,
        cta_text: Optional[str] = None,
        start_sec: int = 0,
        end_sec: int = 600,
        **extra_params,
    ) -> Dict[str, Any]:
        """
        Submits a video for AI clipping.
        Must provide either `url` (YouTube link) or `file_url` (direct public HTTPS link).
        """
        if not url and not file_url:
            raise ValueError("Must provide either a YouTube 'url' or a direct 'file_url'.")

        payload: Dict[str, Any] = {
            "start": start_sec,
            "end": end_sec,
            "preferredLength": preferred_length,
            "language": language,
            "template": template_id or settings.ssemble_default_template,
        }

        if url:
            payload["url"] = url
        elif file_url:
            payload["fileUrl"] = file_url

        if music:
            payload["music"] = True
            if music_name:
                payload["musicName"] = music_name

        if meme_hook:
            payload["memeHook"] = True
            if meme_hook_name:
                payload["memeHookName"] = meme_hook_name

        if cta_enabled:
            payload["ctaEnabled"] = True
            payload["ctaText"] = cta_text or "Subscribe for more!"

        payload.update(extra_params)

        create_url = f"{self.base_url}/shorts/create"
        resp = requests.post(create_url, headers=self.headers, json=payload, timeout=45)
        if not resp.ok:
            raise SsembleAPIError(f"Ssemble create_short failed ({resp.status_code}): {resp.text}")

        data = resp.json().get("data", {})
        return data

    def get_status(self, request_id: str) -> Dict[str, Any]:
        """Polls the status of a clipping request."""
        url = f"{self.base_url}/shorts/{request_id}/status"
        resp = requests.get(url, headers=self.headers, timeout=30)
        if not resp.ok:
            # Fallback to /shorts/:id
            url = f"{self.base_url}/shorts/{request_id}"
            resp = requests.get(url, headers=self.headers, timeout=30)
            if not resp.ok:
                raise SsembleAPIError(f"Failed to get status ({resp.status_code}): {resp.text}")
        return resp.json().get("data", {})

    def get_shorts(self, request_id: str) -> Dict[str, Any]:
        """Retrieves finished shorts and download URLs for a completed request."""
        url = f"{self.base_url}/shorts/{request_id}"
        resp = requests.get(url, headers=self.headers, timeout=30)
        if not resp.ok:
            raise SsembleAPIError(f"Failed to get shorts ({resp.status_code}): {resp.text}")
        return resp.json().get("data", {})

    def wait_for_completion(
        self,
        request_id: str,
        poll_interval: int = 10,
        timeout: int = 900,
        progress_callback: Optional[Any] = None,
    ) -> Dict[str, Any]:
        """
        Polls until the request reaches 'completed' or 'failed'.
        Calls progress_callback(status_dict) on each poll if provided.
        """
        elapsed = 0
        while elapsed < timeout:
            status_data = self.get_status(request_id)
            status = status_data.get("status", "").lower()

            if progress_callback:
                progress_callback(status_data)

            if status == "completed":
                return self.get_shorts(request_id)
            elif status == "failed":
                err = status_data.get("error") or "Unknown error from Ssemble"
                raise SsembleAPIError(f"Ssemble processing failed: {err}")

            time.sleep(poll_interval)
            elapsed += poll_interval

        raise TimeoutError(f"Ssemble request {request_id} timed out after {timeout} seconds.")
