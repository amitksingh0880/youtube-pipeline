"""Unit tests for Niche Intelligence profiles and NicheManager."""

import pytest
from src.modules.research.niche_manager import NicheManager


def test_niche_loading():
    nm = NicheManager()
    niches = nm.get_all_niches()
    assert len(niches) >= 8, f"Expected at least 8 niches, got {len(niches)}"

    # Check key Verticals v3 niches exist
    niche_ids = [n["id"] for n in niches]
    assert "dark_history" in niche_ids
    assert "psychology" in niche_ids
    assert "space_science" in niche_ids
    assert "tech_ai" in niche_ids or "tech" in niche_ids


def test_niche_profile_structure():
    nm = NicheManager()
    dark_hist = nm.get_niche("dark_history")
    assert dark_hist is not None
    assert "script" in dark_hist
    assert "hooks" in dark_hist["script"]
    assert len(dark_hist["script"]["hooks"]) > 0
    assert "tone" in dark_hist["script"]
    assert "captions" in dark_hist
    assert "highlight_color" in dark_hist["captions"]


def test_niche_picking_and_rotation():
    nm = NicheManager()
    chosen = nm.pick_niche("psychology")
    assert chosen["id"] == "psychology"

    # Random pick without preference
    random_pick = nm.pick_niche()
    assert "id" in random_pick
    assert "name" in random_pick
