"""
Neural TTS Voice Synthesizer using Microsoft Edge TTS (edge-tts).
Produces broadcast-grade, natural human narration matching ElevenLabs at $0 cost.
Extracts millisecond-precise sentence and word boundaries for animated subtitles.
"""

import asyncio
import subprocess
import edge_tts
from pathlib import Path
from typing import Any, Dict, List, Optional
from src.core.config import settings


def get_audio_duration(file_path: str) -> float:
    """Uses ffprobe to obtain exact audio duration in seconds."""
    cmd = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        file_path,
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return float(res.stdout.strip())


class NeuralTTS:
    def __init__(
        self,
        default_voice: Optional[str] = None,
        default_rate: Optional[str] = None,
        default_pitch: Optional[str] = None,
    ):
        self.default_voice = default_voice or settings.default_voice
        self.default_rate = default_rate or settings.voice_rate
        self.default_pitch = default_pitch or settings.voice_pitch

    async def _synthesize_async(
        self,
        text: str,
        output_audio_path: str,
        voice: Optional[str] = None,
        rate: Optional[str] = None,
        pitch: Optional[str] = None,
    ) -> Dict[str, Any]:
        voice = voice or self.default_voice
        rate = rate or self.default_rate
        pitch = pitch or self.default_pitch

        communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
        submaker = edge_tts.SubMaker()

        audio_bytes = bytearray()
        word_boundaries = []

        async for chunk in communicate.stream():
            chunk_type = chunk.get("type")
            if chunk_type == "audio":
                audio_bytes.extend(chunk["data"])
            elif chunk_type in ("WordBoundary", "SentenceBoundary"):
                submaker.feed(chunk)
                word_boundaries.append(chunk)

        with open(output_audio_path, "wb") as f:
            f.write(audio_bytes)

        duration = get_audio_duration(output_audio_path)
        srt_content = submaker.get_srt()

        return {
            "audio_path": output_audio_path,
            "duration": duration,
            "srt": srt_content,
            "word_boundaries": word_boundaries,
            "voice": voice,
        }

    def synthesize(
        self,
        text: str,
        output_audio_path: str,
        voice: Optional[str] = None,
        rate: Optional[str] = None,
        pitch: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Synchronous wrapper for speech synthesis."""
        return asyncio.run(
            self._synthesize_async(text, output_audio_path, voice=voice, rate=rate, pitch=pitch)
        )

    def synthesize_beats(
        self,
        beats: list,
        work_dir: Path,
        voice: Optional[str] = None,
        rate: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Synthesizes each beat separately to enable perfect visual sync per beat.
        Returns list of metadata dicts including audio_path, duration, and srt.
        """
        results = []
        for i, beat in enumerate(beats):
            out_file = str(work_dir / f"beat_{i:02d}.mp3")
            meta = self.synthesize(beat.text, out_file, voice=voice, rate=rate)
            meta["beat_number"] = getattr(beat, "beat_number", i + 1)
            meta["text"] = beat.text
            meta["visual_query"] = getattr(beat, "visual_query", "")
            results.append(meta)
        return results

    def concat_audio_files(self, audio_paths: List[str], output_path: str, work_dir: Path) -> str:
        """Concatenates multiple audio mp3 files cleanly using ffmpeg."""
        list_file = work_dir / "concat_audio_list.txt"
        with open(list_file, "w", encoding="utf-8") as f:
            for p in audio_paths:
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
