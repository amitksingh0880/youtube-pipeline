"""
Stock Footage & Visual Sourcer: multi-tiered B-roll sourcing engine.
Sourcing hierarchy:
1. Pexels Video API (if PEXELS_API_KEY configured)
2. Pixabay Video API (if PIXABAY_API_KEY configured)
3. Wikimedia Commons HD Archive ($0, zero key, unmetered, authentic historical/news/science photos)
4. Pollinations.ai Free Vertical Visual AI ($0, zero key, unmetered, 9:16 cinematic visuals)
5. Procedural Vibrant Gradient Engine ($0, 100% offline, radiant ambient glow)

Guarantees 100% visual richness without black screens and without consuming metered Gemini/Ssemble keys.
"""

import os
import re
import urllib.parse
import subprocess
import requests
from pathlib import Path
from typing import Any, Dict, List, Optional
from src.core.config import settings

PEXELS_SEARCH_URL = "https://api.pexels.com/videos/search"
PIXABAY_SEARCH_URL = "https://pixabay.com/api/videos/"
WIKIMEDIA_SEARCH_URL = "https://commons.wikimedia.org/w/api.php"
POLLINATIONS_BASE_URL = "https://image.pollinations.ai/prompt"


class StockSourcer:
    def __init__(
        self,
        pexels_api_key: Optional[str] = None,
        pixabay_api_key: Optional[str] = None,
    ):
        self.pexels_api_key = pexels_api_key or settings.pexels_api_key
        self.pixabay_api_key = pixabay_api_key or settings.pixabay_api_key

    def search_pexels(
        self,
        query: str,
        orientation: str = "portrait",
        min_duration: int = 3,
    ) -> Optional[str]:
        """Queries Pexels Video API for high-resolution video matching the query."""
        if not self.pexels_api_key:
            return None

        headers = {"Authorization": self.pexels_api_key}
        params = {
            "query": query,
            "per_page": 5,
            "orientation": orientation,
        }
        try:
            resp = requests.get(PEXELS_SEARCH_URL, headers=headers, params=params, timeout=12)
            if not resp.ok:
                if orientation == "portrait":
                    return self.search_pexels(query, orientation="", min_duration=min_duration)
                return None

            data = resp.json()
            videos = data.get("videos", [])
            for v in videos:
                if v.get("duration", 0) < min_duration:
                    continue
                files = v.get("video_files", [])
                hd_files = [f for f in files if f.get("height", 0) >= 720 or f.get("width", 0) >= 720]
                if hd_files:
                    return hd_files[0]["link"]
                elif files:
                    return files[0]["link"]
            return None
        except Exception:
            return None

    def search_pixabay(self, query: str) -> Optional[str]:
        """Queries Pixabay Video API for stock footage."""
        if not self.pixabay_api_key:
            return None
        params = {
            "key": self.pixabay_api_key,
            "q": query,
            "per_page": 5,
        }
        try:
            resp = requests.get(PIXABAY_SEARCH_URL, params=params, timeout=12)
            if not resp.ok:
                return None
            hits = resp.json().get("hits", [])
            for hit in hits:
                videos = hit.get("videos", {})
                for res_key in ("large", "medium", "small"):
                    if res_key in videos and videos[res_key].get("url"):
                        return videos[res_key]["url"]
            return None
        except Exception:
            return None

    def search_wikimedia_commons(
        self,
        query: str,
        min_width: int = 600,
    ) -> Optional[str]:
        """
        Free, unmetered, zero-key search on Wikimedia Commons.
        Retrieves authentic high-resolution public domain and CC images.
        """
        clean_query = re.sub(r"[^\w\s-]", "", query).strip()
        if not clean_query:
            return None

        # Clean query to top 3 salient words if too long
        words = clean_query.split()
        search_terms = " ".join(words[:4])

        params = {
            "action": "query",
            "generator": "search",
            "gsrsearch": search_terms,
            "gsrnamespace": 6,  # File namespace
            "prop": "imageinfo",
            "iiprop": "url|mime|dimensions",
            "format": "json",
            "gsrlimit": 10,
        }
        headers = {"User-Agent": "VerticalsContentEngine/3.1 (contact@verticals.local)"}

        try:
            resp = requests.get(WIKIMEDIA_SEARCH_URL, params=params, headers=headers, timeout=10)
            if not resp.ok:
                return None

            data = resp.json()
            pages = data.get("query", {}).get("pages", {})
            valid_urls = []
            for p in pages.values():
                for info in p.get("imageinfo", []):
                    mime = info.get("mime", "")
                    w = info.get("width", 0)
                    url = info.get("url", "")
                    if mime in ("image/jpeg", "image/png", "image/webp") and w >= min_width and url:
                        valid_urls.append(url)

            if valid_urls:
                return valid_urls[0]

            # Broader fallback: search with just first 2 words
            if len(words) > 2:
                params["gsrsearch"] = " ".join(words[:2])
                resp2 = requests.get(WIKIMEDIA_SEARCH_URL, params=params, headers=headers, timeout=10)
                if resp2.ok:
                    pages2 = resp2.json().get("query", {}).get("pages", {})
                    for p in pages2.values():
                        for info in p.get("imageinfo", []):
                            mime = info.get("mime", "")
                            w = info.get("width", 0)
                            url = info.get("url", "")
                            if mime in ("image/jpeg", "image/png", "image/webp") and w >= min_width and url:
                                return url

            return None
        except Exception:
            return None

    def generate_pollinations_image(
        self,
        prompt: str,
        output_path: str,
        seed: Optional[int] = None,
    ) -> Optional[str]:
        """
        Free, unmetered, zero-key AI image generation via Pollinations.ai.
        Generates vertical 9:16 cinematic visuals matching the scene description.
        """
        clean_prompt = prompt.replace("\n", " ").strip()
        encoded_prompt = urllib.parse.quote(clean_prompt)
        seed_param = seed if seed is not None else 42
        url = f"{POLLINATIONS_BASE_URL}/{encoded_prompt}?width=720&height=1280&nologo=true&seed={seed_param}"

        try:
            resp = requests.get(url, timeout=12)
            if resp.ok and len(resp.content) > 5000:
                with open(output_path, "wb") as f:
                    f.write(resp.content)
                return output_path
            return None
        except Exception:
            return None

    def download_media(self, url: str, output_path: str) -> str:
        """Downloads a video or image file from a remote URL."""
        headers = {"User-Agent": "VerticalsContentEngine/3.1 (contact@verticals.local)"}
        resp = requests.get(url, headers=headers, stream=True, timeout=30)
        resp.raise_for_status()
        with open(output_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    f.write(chunk)
        return output_path

    # Backwards-compatible alias for existing tests
    download_clip = download_media

    def generate_procedural_background(
        self,
        output_path: str,
        duration: float,
        width: int = 1080,
        height: int = 1920,
        theme_index: int = 0,
    ) -> str:
        """
        Generates a radiant, cinematic multi-color ambient motion background.
        Guarantees that even completely offline without internet or API keys,
        the video features glowing, vibrant visual depth instead of a black screen.
        """
        # Vibrant cinematic color schemes (base, primary accent, secondary glow)
        palettes = [
            ("0x0b0f19", "0x312e81", "0x6366f1"),  # Deep Indigo / Electric Violet
            ("0x18181b", "0x7f1d1d", "0xef4444"),  # Obsidian Crimson / Dramatic Red
            ("0x022c22", "0x065f46", "0x10b981"),  # Emerald Jade / Bio-Tech
            ("0x1e1b4b", "0x581c87", "0xa855f7"),  # Royal Amethyst / Mystery
            ("0x291807", "0x78350f", "0xf59e0b"),  # Golden Amber / Exploration
        ]
        base, acc1, acc2 = palettes[theme_index % len(palettes)]

        # Soft glowing ambient light fields with subtle vignette
        vf = (
            f"color=c={base}:s={width}x{height}:d={duration},"
            f"drawbox=x=0:y=0:w={width}:h={height//2}:c={acc1}@0.65:t=fill,"
            f"drawbox=x=150:y=400:w=780:h=780:c={acc2}@0.45:t=fill,"
            f"boxblur=luma_radius=120:luma_power=3,"
            f"vignette=PI/6,"
            f"fps=30"
        )
        cmd = [
            "ffmpeg",
            "-y",
            "-f", "lavfi",
            "-i", vf,
            "-t", str(duration),
            "-c:v", "libx264",
            "-preset", "fast",
            "-pix_fmt", "yuv420p",
            str(output_path),
        ]
        subprocess.run(cmd, capture_output=True, check=True)
        return output_path

    def source_beat_footage(
        self,
        beats: list,
        work_dir: Path,
        niche: Optional[Dict[str, Any]] = None,
    ) -> List[str]:
        """
        Multi-tiered visual sourcing engine:
        1. Pexels HD video (if key configured)
        2. Pixabay HD video (if key configured)
        3. Wikimedia Commons authentic HD image ($0, zero key, unmetered)
        4. Pollinations.ai 9:16 vertical AI image ($0, zero key, unmetered)
        5. Radiant ambient glowing gradient (100% offline fallback)
        """
        niche_style = ""
        if niche:
            visual_cfg = niche.get("visuals", {})
            style = visual_cfg.get("style", "")
            mood = visual_cfg.get("mood", "")
            niche_style = f"{style}, {mood}".strip(", ")

        footage_paths = []
        for i, beat in enumerate(beats):
            query = getattr(beat, "visual_query", "") or (beat.get("visual_query") if isinstance(beat, dict) else "")
            duration = getattr(beat, "duration_est", 4.0) or (beat.get("duration_est", 4.0) if isinstance(beat, dict) else 4.0)
            beat_text = getattr(beat, "text", "") or (beat.get("text") if isinstance(beat, dict) else "")

            # Tier 1 & 2: Stock Video APIs (if configured)
            clip_url = None
            if query:
                clip_url = self.search_pexels(query)
                if not clip_url:
                    clip_url = self.search_pixabay(query)

            if clip_url:
                video_dest = str(work_dir / f"raw_footage_{i:02d}.mp4")
                try:
                    self.download_media(clip_url, video_dest)
                    footage_paths.append(video_dest)
                    continue
                except Exception:
                    pass

            # Tier 3: Wikimedia Commons HD Image Archive ($0, unmetered)
            image_url = None
            if query:
                image_url = self.search_wikimedia_commons(query)

            if image_url:
                ext = ".png" if ".png" in image_url.lower() else ".jpg"
                img_dest = str(work_dir / f"raw_footage_{i:02d}{ext}")
                try:
                    self.download_media(image_url, img_dest)
                    footage_paths.append(img_dest)
                    continue
                except Exception:
                    pass

            # Tier 4: Pollinations.ai Vertical AI Image ($0, unmetered)
            ai_img_dest = str(work_dir / f"raw_footage_{i:02d}.jpg")
            prompt_components = []
            if query:
                prompt_components.append(query)
            elif beat_text:
                # Use key words from beat narration
                prompt_components.append(" ".join(beat_text.split()[:6]))

            if niche_style:
                prompt_components.append(niche_style)
            prompt_components.append("vertical 9:16 aspect ratio, dramatic lighting, high resolution, cinematic photorealism")
            full_prompt = ", ".join(prompt_components)

            generated = self.generate_pollinations_image(full_prompt, ai_img_dest, seed=42 + i * 7)
            if generated and os.path.exists(ai_img_dest) and os.path.getsize(ai_img_dest) > 5000:
                footage_paths.append(ai_img_dest)
                continue

            # Tier 5: Radiant Glowing Gradient (Guaranteed offline fallback)
            proc_dest = str(work_dir / f"raw_footage_{i:02d}.mp4")
            self.generate_procedural_background(proc_dest, duration=duration + 1.0, theme_index=i)
            footage_paths.append(proc_dest)

        return footage_paths
