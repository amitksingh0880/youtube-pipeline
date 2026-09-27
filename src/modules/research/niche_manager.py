"""
Niche Intelligence Manager for YouTube Shorts Automation.
Loads rich Verticals v3-style niche profiles from niches/*.yaml and config/niches.yaml.
Shapes every stage of the pipeline: research, scripting tone, visual cues,
voice selection, caption styling, and topic discovery.
"""

import os
import random
import yaml
from pathlib import Path
from typing import Any, Dict, List, Optional
from src.core.config import CONFIG_DIR
from src.core.database import get_recent_topics

NICHES_DIR = Path(__file__).resolve().parent.parent.parent.parent / "niches"
CONFIG_NICHES_FILE = CONFIG_DIR / "niches.yaml"


class NicheManager:
    def __init__(self, niches_dir: Optional[Path] = None, fallback_file: Optional[Path] = None):
        self.niches_dir = niches_dir or NICHES_DIR
        self.fallback_file = fallback_file or CONFIG_NICHES_FILE
        self._niches: List[Dict[str, Any]] = []
        self._reload_niches()

    def _reload_niches(self):
        niches_map: Dict[str, Dict[str, Any]] = {}

        # 1. Load standalone rich profiles from niches/*.yaml
        if self.niches_dir.exists():
            for yaml_file in sorted(self.niches_dir.glob("*.yaml")):
                try:
                    with open(yaml_file, "r", encoding="utf-8") as f:
                        data = yaml.safe_load(f) or {}
                    niche_id = yaml_file.stem
                    data["id"] = data.get("id") or data.get("name") or niche_id
                    data["name"] = data.get("display_name") or data.get("name") or niche_id.replace("_", " ").title()
                    
                    # Extract suggested voice for backward compatibility
                    if "voice" in data and isinstance(data["voice"], dict):
                        suggested = data["voice"].get("suggested_voices", {})
                        if isinstance(suggested, dict):
                            data["default_voice"] = suggested.get("edge_tts", "en-US-ChristopherNeural")
                        data["voice_rate"] = data["voice"].get("pace", "+5%")

                    niches_map[data["id"]] = data
                except Exception as e:
                    pass

        # 2. Merge with config/niches.yaml (if any niches are defined there)
        if self.fallback_file.exists():
            try:
                with open(self.fallback_file, "r", encoding="utf-8") as f:
                    config_data = yaml.safe_load(f) or {}
                for item in config_data.get("niches", []):
                    nid = item.get("id")
                    if nid and nid not in niches_map:
                        niches_map[nid] = item
                    elif nid and nid in niches_map:
                        # Supplement missing fields
                        for k, v in item.items():
                            if k not in niches_map[nid]:
                                niches_map[nid][k] = v
            except Exception:
                pass

        self._niches = list(niches_map.values())

    def get_all_niches(self) -> List[Dict[str, Any]]:
        return self._niches

    def get_niche(self, niche_id: str) -> Optional[Dict[str, Any]]:
        normalized = niche_id.lower().replace("-", "_").strip()
        for n in self._niches:
            cur_id = str(n.get("id", "")).lower().replace("-", "_")
            cur_name = str(n.get("name", "")).lower()
            if cur_id == normalized or cur_name == normalized or normalized in cur_id:
                return n
        return None

    def pick_niche(self, preferred_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Picks a niche based on user preference or weighted rotation.
        """
        if preferred_id:
            found = self.get_niche(preferred_id)
            if found:
                return found

        if not self._niches:
            raise ValueError(f"No niches found in {self.niches_dir} or {self.fallback_file}")

        weights = [n.get("weight", 1) for n in self._niches]
        chosen = random.choices(self._niches, weights=weights, k=1)[0]
        return chosen

    def get_exclusion_topics(self, niche_id: str, limit: int = 30) -> List[str]:
        """
        Retrieves recent topics from the database to inject as negative constraints.
        """
        return get_recent_topics(niche_id, limit=limit)
