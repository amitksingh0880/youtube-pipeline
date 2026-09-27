"""Unit tests for StockSourcer and MotionFX (Zero Metered API Calls)."""

import os
import tempfile
import subprocess
from pathlib import Path
from src.modules.visuals.stock_sourcer import StockSourcer
from src.modules.visuals.motion_fx import MotionFX


def test_procedural_background_radiance():
    with tempfile.TemporaryDirectory() as td:
        out_bg = os.path.join(td, "ambient_glow.mp4")
        sourcer = StockSourcer(pexels_api_key="", pixabay_api_key="")
        result = sourcer.generate_procedural_background(out_bg, duration=1.5, theme_index=0)

        assert os.path.exists(result)
        assert os.path.getsize(result) > 10000


def test_wikimedia_commons_search():
    sourcer = StockSourcer(pexels_api_key="", pixabay_api_key="")
    # Search for an iconic historical query guaranteed to have CC photos
    url = sourcer.search_wikimedia_commons("Albert Einstein")
    assert url is not None
    assert "upload.wikimedia.org" in url
    assert any(url.lower().endswith(ext) or ext in url.lower() for ext in [".jpg", ".jpeg", ".png", ".webp"])


def test_motion_fx_image_ken_burns():
    with tempfile.TemporaryDirectory() as td:
        wd = Path(td)
        test_img = str(wd / "test_frame.jpg")

        # Generate a test image using FFmpeg lavfi
        subprocess.run(
            ["ffmpeg", "-y", "-f", "lavfi", "-i", "testsrc=size=1080x1920:rate=1", "-frames:v", "1", test_img],
            capture_output=True,
            check=True,
        )

        out_clip_in = str(wd / "clip_zoom_in.mp4")
        MotionFX.reframe_and_animate(
            input_video=test_img,
            output_video=out_clip_in,
            target_duration=1.5,
            apply_ken_burns=True,
            beat_index=0,
        )
        assert os.path.exists(out_clip_in)
        assert os.path.getsize(out_clip_in) > 10000

        out_clip_out = str(wd / "clip_zoom_out.mp4")
        MotionFX.reframe_and_animate(
            input_video=test_img,
            output_video=out_clip_out,
            target_duration=1.5,
            apply_ken_burns=True,
            beat_index=1,
        )
        assert os.path.exists(out_clip_out)
        assert os.path.getsize(out_clip_out) > 10000


def test_source_beat_footage_zero_keys():
    with tempfile.TemporaryDirectory() as td:
        wd = Path(td)
        sourcer = StockSourcer(pexels_api_key="", pixabay_api_key="")
        mock_beats = [
            {"visual_query": "neural network brain", "duration_est": 2.0, "text": "Exploring the subconscious mind."},
            {"visual_query": "deep space galaxy", "duration_est": 2.0, "text": "Vast expanse of the universe."},
        ]

        footage_paths = sourcer.source_beat_footage(mock_beats, wd)
        assert len(footage_paths) == len(mock_beats)
        for p in footage_paths:
            assert os.path.exists(p)
            assert os.path.getsize(p) > 2000
