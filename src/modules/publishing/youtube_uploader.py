"""
YouTube Shorts Video Uploader using YouTube Data API v3.
Features resumable upload chunks, SEO optimization, and 2026 Altered Media disclosure.
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional
from googleapiclient.http import MediaFileUpload
from src.core.config import settings
from src.modules.publishing.youtube_oauth import YouTubeOAuth


class YouTubeUploader:
    def __init__(self, youtube_service=None):
        self.service = youtube_service

    def _get_service(self):
        if not self.service:
            self.service = YouTubeOAuth.get_authenticated_service()
        return self.service

    def upload_short(
        self,
        video_path: str,
        title: str,
        description: str,
        tags: Optional[List[str]] = None,
        privacy_status: Optional[str] = None,
        publish_at: Optional[str] = None,
        contains_synthetic_media: bool = True,
        progress_callback: Optional[Any] = None,
    ) -> Dict[str, Any]:
        """
        Uploads a video to YouTube with Shorts formatting and compliance.
        publish_at: Optional ISO 8601 / RFC3339 string (e.g. '2026-10-01T15:00:00Z') for scheduled release.
        contains_synthetic_media: Enforces YouTube 2026 Altered Media disclosure (default True).
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found at: {video_path}")

        # Ensure #Shorts is present in title or description for YouTube algorithmic classification
        formatted_title = title[:100]
        if "#shorts" not in formatted_title.lower():
            if len(formatted_title) <= 92:
                formatted_title = f"{formatted_title} #Shorts"

        formatted_desc = f"{description}\n\n#Shorts #Viral"

        body = {
            "snippet": {
                "title": formatted_title,
                "description": formatted_desc,
                "tags": tags or ["Shorts", "Viral"],
                "categoryId": settings.youtube_category_id,
            },
            "status": {
                "privacyStatus": "private" if publish_at else (privacy_status or settings.youtube_default_privacy),
                "selfDeclaredMadeForKids": False,
                # YouTube 2026 Altered Media Policy Compliance
                "containsSyntheticMedia": contains_synthetic_media,
            },
        }

        if publish_at:
            body["status"]["publishAt"] = publish_at

        youtube = self._get_service()
        media = MediaFileUpload(
            video_path,
            chunksize=1024 * 1024 * 4,  # 4MB chunks
            resumable=True,
            mimetype="video/mp4",
        )

        request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)

        response = None
        while response is None:
            status, response = request.next_chunk()
            if status and progress_callback:
                progress_callback(int(status.progress() * 100))

        video_id = response.get("id")
        shorts_url = f"https://youtube.com/shorts/{video_id}"

        return {
            "video_id": video_id,
            "url": shorts_url,
            "response": response,
        }
