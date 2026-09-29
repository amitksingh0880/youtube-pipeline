"""
Dynamic Motion FX Engine using FFmpeg.
Applies Ken Burns zoom-pan (alternating zoom-in and zoom-out),
9:16 vertical reframing, and loop/trim synchronization.
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
        - If image: converts to dynamic Ken Burns motion clip with alternating zoom-in/zoom-out.
        - If video: scales, center-crops to 9:16, loops if shorter than target_duration, trims to target_duration.
        """
        input_path = Path(input_video)
        ext = input_path.suffix.lower()
        is_image = ext in [".jpg", ".jpeg", ".png", ".webp"]
        total_frames = max(1, int(target_duration * cls.FPS))

        if is_image:
            # Alternating zoom directions for dynamic cinematic pacing
            if beat_index % 2 == 0:
                # Smooth cinematic zoom-in: 1.00 -> 1.15
                zoom_expr = "min(zoom+0.0015\\,1.15)"
            else:
                # Smooth cinematic zoom-out: 1.15 -> 1.00
                zoom_expr = "if(lte(zoom\\,1.0)\\,1.15\\,max(1.001\\,zoom-0.0015))"

            vf = (
                f"scale={cls.WIDTH}:{cls.HEIGHT}:force_original_aspect_ratio=increase,"
                f"crop={cls.WIDTH}:{cls.HEIGHT},"
                f"zoompan=z='{zoom_expr}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={total_frames}:s={cls.WIDTH}x{cls.HEIGHT}:fps={cls.FPS}"
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
                "-preset", "ultrafast",
                "-threads", "1",
                "-max_muxing_queue_size", "1024",
                "-pix_fmt", "yuv420p",
                str(output_video),
            ]
        else:
            # Video asset: scale and center-crop to 9:16 portrait, loop if shorter than duration
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
                "-an",  # Strip original video audio so narration is clean
                "-c:v", "libx264",
                "-preset", "ultrafast",
                "-threads", "1",
                "-max_muxing_queue_size", "1024",
                "-r", str(cls.FPS),
                "-pix_fmt", "yuv420p",
                str(output_video),
            ]

        subprocess.run(cmd, capture_output=True, check=True)
        return output_video
