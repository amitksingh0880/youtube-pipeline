"""Unit tests for Local Video Assembler and ASS Karaoke Subtitles."""

import os
import tempfile
from pathlib import Path
from src.modules.visuals.stock_sourcer import StockSourcer
from src.modules.visuals.motion_fx import MotionFX
from src.modules.voice.neural_tts import NeuralTTS
from src.modules.assembly.local_assembler import LocalAssembler


def test_local_video_assembly():
    with tempfile.TemporaryDirectory() as td:
        wd = Path(td)
        sourcer = StockSourcer()
        tts = NeuralTTS()

        # Generate test beat audio
        b_audio = str(wd / "beat.mp3")
        meta = tts.synthesize("Fast assembly test.", b_audio)
        meta["text"] = "Fast assembly test."

        # Generate test procedural background clip
        bg = str(wd / "bg.mp4")
        clip = str(wd / "clip.mp4")
        sourcer.generate_procedural_background(bg, duration=meta["duration"], theme_index=0)
        MotionFX.reframe_and_animate(bg, clip, target_duration=meta["duration"], apply_ken_burns=False)

        # Assemble short with animated subtitles
        final_mp4 = str(wd / "short.mp4")
        LocalAssembler.assemble_short([clip], [meta], b_audio, final_mp4, wd)

        assert os.path.exists(final_mp4)
        assert os.path.getsize(final_mp4) > 10000
