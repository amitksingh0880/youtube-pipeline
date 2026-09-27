"""Unit tests for Microsoft Edge Neural TTS voice synthesis."""

import os
import tempfile
from pathlib import Path
from src.modules.voice.neural_tts import NeuralTTS


def test_neural_tts_synthesis():
    with tempfile.TemporaryDirectory() as td:
        out_path = os.path.join(td, "test_voice.mp3")
        tts = NeuralTTS(default_voice="en-US-ChristopherNeural")
        res = tts.synthesize("Testing studio-grade neural voice.", out_path)

        assert os.path.exists(out_path)
        assert res["duration"] > 0.5
        assert "voice" in res
        assert res["voice"] == "en-US-ChristopherNeural"
        assert len(res["word_boundaries"]) > 0
