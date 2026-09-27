"""
Audio Mastering Engine using FFmpeg.
Applies broadcast volume normalization (-14 LUFS) and dynamic background music ducking.
"""

import os
import subprocess
from pathlib import Path
from typing import Optional


class AudioMaster:
    @staticmethod
    def normalize_loudness(input_audio: str, output_audio: str, target_lufs: float = -14.0) -> str:
        """
        Applies EBU R128 loudness normalization to achieve standard -14 LUFS for YouTube Shorts.
        """
        cmd = [
            "ffmpeg",
            "-y",
            "-i", input_audio,
            "-af", f"loudnorm=I={target_lufs}:LRA=11:TP=-1.5",
            "-c:a", "libmp3lame",
            "-b:a", "192k",
            output_audio,
        ]
        subprocess.run(cmd, capture_output=True, check=True)
        return output_audio

    @staticmethod
    def mix_background_music(
        narration_audio: str,
        output_audio: str,
        music_path: Optional[str] = None,
        music_volume: float = 0.08,
    ) -> str:
        """
        Mixes background music underneath the narration track.
        If music_path is absent or invalid, simply copies the narration.
        """
        if not music_path or not os.path.exists(music_path):
            return narration_audio

        cmd = [
            "ffmpeg",
            "-y",
            "-i", narration_audio,
            "-stream_loop", "-1",
            "-i", music_path,
            "-filter_complex",
            f"[1:a]volume={music_volume}[music];[0:a][music]amix=inputs=2:duration=first:dropout_transition=2[aout]",
            "-map", "[aout]",
            "-c:a", "libmp3lame",
            "-b:a", "192k",
            output_audio,
        ]
        subprocess.run(cmd, capture_output=True, check=True)
        return output_audio
