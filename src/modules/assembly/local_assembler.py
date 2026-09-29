"""
Local Studio Assembler Engine using FFmpeg.
Assembles the complete 1080x1920 60fps Short with animated karaoke ASS subtitles,
continuous scene pacing, and synchronized audio. Consumes 0 Ssemble credits.
"""

import os
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional
from src.modules.assembly.ass_subtitle_generator import ASSSubtitleGenerator


class LocalAssembler:
    @staticmethod
    def concat_clips(clip_paths: List[str], output_path: str, work_dir: Path) -> str:
        """Concatenates multiple video clips using ffmpeg concat demuxer."""
        list_file = work_dir / "video_concat_list.txt"
        with open(list_file, "w", encoding="utf-8") as f:
            for p in clip_paths:
                f.write(f"file '{Path(p).resolve().as_posix()}'\n")

        cmd = [
            "ffmpeg",
            "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", str(list_file),
            "-c", "copy",
            output_path,
        ]
        subprocess.run(cmd, capture_output=True, check=True)
        return output_path

    @classmethod
    def assemble_short(
        cls,
        beat_clips: List[str],
        beats_meta: List[Dict[str, Any]],
        master_audio_path: str,
        final_output_path: str,
        work_dir: Path,
        highlight_color: str = "&H0000FFFF&",
    ) -> str:
        """
        Full assembly pipeline:
        1. Concatenate reframed beat clips into one continuous video.
        2. Generate animated Hormozi-style ASS karaoke subtitles.
        3. Burn subtitles into video and mux narration audio with FFmpeg.
        """
        # Step 1: Concatenate clips
        raw_video = str(work_dir / "concatenated_raw.mp4")
        cls.concat_clips(beat_clips, raw_video, work_dir)

        # Step 2: Generate ASS subtitles
        ass_path = str(work_dir / "subtitles.ass")
        ASSSubtitleGenerator.generate_ass(
            beats_meta=beats_meta,
            output_ass_path=ass_path,
            highlight_color=highlight_color,
        )

        # In Windows FFmpeg, escape colon and backslashes for ass filter
        escaped_ass = ass_path.replace("\\", "/").replace(":", "\\:")

        # Step 3: Burn in subtitles and mux master audio
        cmd = [
            "ffmpeg",
            "-y",
            "-i", raw_video,
            "-i", master_audio_path,
            "-vf", f"ass='{escaped_ass}'",
            "-map", "0:v:0",
            "-map", "1:a:0",
            "-shortest",
            "-c:v", "libx264",
            "-preset", "ultrafast",
            "-crf", "23",
            "-threads", "1",
            "-max_muxing_queue_size", "1024",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-b:a", "192k",
            final_output_path,
        ]
        subprocess.run(cmd, capture_output=True, check=True)
        return final_output_path
