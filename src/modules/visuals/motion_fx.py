"""
Dynamic Motion FX Engine using FFmpeg.
Applies lightweight vertical reframing and loop/trim synchronization.
Optimized for low-memory cloud environments (512MB Render free tier).
Supports both image still assets and video b-roll footage.
"""

import subprocess
from pathlib import Path
from typing import Optional


class MotionFX:
    WIDTH = 1080
    HEIGHT = 1920
    FPS = 30

    @classmethod
    def reframe_and_animate(
        cls,
        input_video: str,
        output_video: str,
        target_duration: float,
        apply_ken_burns: bool = True,
        beat_index: int = 0,
    ) -> str:
        """
        Reframes any media (video or image) to 1080x1920 vertical Short format.
        - If image: scales up, center-crops to 9:16, and applies a lightweight slow pan.
        - If video: scales, center-crops to 9:16, loops if shorter than target_duration.
        """
        input_path = Path(input_video)
        ext = input_path.suffix.lower()
        is_image = ext in [".jpg", ".jpeg", ".png", ".webp"]

        if is_image:
            # Lightweight slow vertical pan instead of memory-hungry zoompan
            # Scale image slightly taller than output to allow pan headroom
            src_h = cls.HEIGHT + 120
            if beat_index % 2 == 0:
                crop_y = f"max(120-t*10\\,0)"
            else:
                crop_y = f"min(t*10\\,120)"

            vf = (
                f"scale={cls.WIDTH}:{src_h}:force_original_aspect_ratio=increase,"
                f"crop={cls.WIDTH}:{cls.HEIGHT}:0:'{crop_y}',"
                f"fps={cls.FPS}"
            )
            cmd = [
                "ffmpeg",
                "-y",
                "-loop", "1",
                "-i", str(input_video),
                "-t", str(target_duration),
                "-vf", vf,
                "-an",
                "-c:v", "libx264",
                "-preset", "fast",
                "-threads", "1",
                "-max_muxing_queue_size", "1024",
                "-pix_fmt", "yuv420p",
                str(output_video),
            ]
        else:
            # Video asset: scale and center-crop to 9:16 portrait
            base_filter = (
                f"scale={cls.WIDTH}:{cls.HEIGHT}:force_original_aspect_ratio=increase,"
                f"crop={cls.WIDTH}:{cls.HEIGHT}"
            )
            cmd = [
                "ffmpeg",
                "-y",
                "-stream_loop", "-1",
                "-i", str(input_video),
                "-t", str(target_duration),
                "-vf", base_filter,
                "-an",
                "-c:v", "libx264",
                "-preset", "fast",
                "-threads", "1",
                "-max_muxing_queue_size", "1024",
                "-r", str(cls.FPS),
                "-pix_fmt", "yuv420p",
                str(output_video),
            ]

        subprocess.run(cmd, capture_output=True, check=True)
        return output_video
