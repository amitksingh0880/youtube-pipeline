"""
YouTube Data API v3 OAuth 2.0 Client Manager.
Handles token caching, automatic refreshing, and one-time browser consent.
"""

import os
import pickle
from pathlib import Path
from typing import Optional
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build, Resource
from src.core.config import settings

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.readonly",
]


class YouTubeOAuth:
    @classmethod
    def get_authenticated_service(cls) -> Resource:
        """
        Retrieves an authorized YouTube Data API service instance.
        Uses cached credentials if valid; refreshes or prompts OAuth flow as needed.
        """
        token_path = settings.abs_token_path
        client_secrets_path = settings.abs_client_secrets_path

        creds = None
        if token_path.exists():
            with open(token_path, "rb") as token_file:
                try:
                    creds = pickle.load(token_file)
                except Exception:
                    creds = None

        # If credentials don't exist or are invalid
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not client_secrets_path.exists():
                    raise FileNotFoundError(
                        f"YouTube OAuth client secrets file not found at: {client_secrets_path}.\n"
                        "Please download Desktop OAuth credentials from Google Cloud Console "
                        "and save as config/client_secret.json."
                    )
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(client_secrets_path), SCOPES
                )
                creds = flow.run_local_server(port=0)

            # Cache the token for future runs
            token_path.parent.mkdir(parents=True, exist_ok=True)
            with open(token_path, "wb") as token_file:
                pickle.dump(creds, token_file)

        return build("youtube", "v3", credentials=creds)
