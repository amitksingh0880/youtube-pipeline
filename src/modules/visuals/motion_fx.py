"""
Dynamic Motion FX Engine using FFmpeg.
Applies Ken Burns zoom-pan, 9:16 vertical reframing, and loop/trim synchronization.
"""

import subprocess
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
    ) -> str:
        """
        Reframes any video to 1080x1920 vertical Short format,
        loops if shorter than target_duration, trims to target_duration,
        and applies dynamic slow-zoom motion.
        """
        # Base scale and crop filter for 9:16 vertical
        base_filter = (
            f"scale={cls.WIDTH}:{cls.HEIGHT}:force_original_aspect_ratio=increase,"
            f"crop={cls.WIDTH}:{cls.HEIGHT}"
        )

        if apply_ken_burns:
            # Subtle smooth zoom (1.00 -> 1.08 over the clip)
            motion_filter = (
                f"{base_filter},"
                f"zoompan=z='min(zoom+0.0008,1.08)':d={int(target_duration * cls.FPS)}:s={cls.WIDTH}x{cls.HEIGHT}"
            )
        else:
            motion_filter = base_filter

        cmd = [
            "ffmpeg",
            "-y",
            "-stream_loop", "-1",
            "-i", input_video,
            "-t", str(target_duration),
            "-vf", motion_filter,
            "-an",  # Strip original video audio so narration is clean
            "-c:v", "libx264",
            "-r", str(cls.FPS),
            "-pix_fmt", "yuv420p",
            output_video,
        ]
        subprocess.run(cmd, capture_output=True, check=True)
        return output_video
