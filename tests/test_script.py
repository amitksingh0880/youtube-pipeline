"""Unit tests for Gemini 2.0 Flash Script Engine."""

from src.modules.scripting.script_engine import ScriptEngine, YouTubeShortScript


def test_script_engine_schema_and_generation():
    engine = ScriptEngine()
    niche = {"id": "dark_history", "name": "Dark History"}
    script = engine.generate_script(niche, topic_hint="Acoustic Kitty")

    assert isinstance(script, YouTubeShortScript)
    assert len(script.hook) > 5
    assert len(script.beats) >= 4
    assert script.loop_anchor != ""
    assert "#Shorts" in script.title
    assert len(script.tags) >= 3

    for beat in script.beats:
        assert len(beat.text) > 5
        assert len(beat.visual_query) > 2
        assert beat.duration_est > 0.0
