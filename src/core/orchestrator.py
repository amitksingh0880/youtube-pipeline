"""
Master Workflow Orchestrator for YouTube Shorts Automation Studio.
Coordinates the end-to-end pipeline:
Niche Intelligence -> Multi-Source Trend Scout -> Anti-Hallucination Research Gate ->
Gemini 2.0 Flash Scripting -> Edge Neural Voice -> Stock B-roll -> Motion FX ->
Dual Assembly (Local Studio / Ssemble AI / Ssemble Clip) -> Altered Media YouTube Upload -> SQLite DB.
"""

import os
import uuid
import tempfile
import logging
from pathlib import Path
from typing import Any, Callable, Dict, Optional

from src.core.config import OUTPUT_DIR, settings
from src.core.database import record_short, update_short_status
from src.modules.research.niche_manager import NicheManager
from src.modules.research.trend_scout import TrendScout
from src.modules.research.research_gate import ResearchGate
from src.modules.scripting.script_engine import ScriptEngine
from src.modules.voice.neural_tts import NeuralTTS
from src.modules.voice.audio_master import AudioMaster
from src.modules.visuals.stock_sourcer import StockSourcer
from src.modules.visuals.motion_fx import MotionFX
from src.modules.assembly.local_assembler import LocalAssembler
from src.modules.assembly.ssemble_bridge import SsembleBridge
from src.modules.publishing.youtube_uploader import YouTubeUploader

logger = logging.getLogger(__name__)


class ShortsOrchestrator:
    def __init__(self):
        self.niche_manager = NicheManager()
        self.trend_scout = TrendScout()
        self.research_gate = ResearchGate()
        self.script_engine = ScriptEngine()
        self.neural_tts = NeuralTTS()
        self.audio_master = AudioMaster()
        self.stock_sourcer = StockSourcer()
        self.local_assembler = LocalAssembler()
        self.ssemble_bridge = SsembleBridge()
        self.youtube_uploader = YouTubeUploader()

    def run_pipeline(
        self,
        niche_id: Optional[str] = None,
        mode: str = "local-studio",  # "local-studio", "ssemble-ai", "ssemble-clip"
        topic_hint: Optional[str] = None,
        youtube_url: Optional[str] = None,
        dry_run: bool = False,
        privacy_status: Optional[str] = None,
        progress_callback: Optional[Callable[[str, int], None]] = None,
    ) -> Dict[str, Any]:
        """
        Executes one full creation and publishing cycle across any selected mode.
        """
        def update_progress(msg: str, pct: int):
            if progress_callback:
                progress_callback(msg, pct)
            logger.info(f"[{pct}%] {msg}")

        session_id = uuid.uuid4().hex[:10]
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

        # Step 1: Select Niche & Anti-Repeat Check
        update_progress("Selecting niche profile & loading intelligence...", 10)
        niche = self.niche_manager.pick_niche(niche_id)
        exclusions = self.niche_manager.get_exclusion_topics(niche["id"], limit=30)
        final_short_path = str(OUTPUT_DIR / f"short_{niche['id']}_{session_id}.mp4")

        # Handle Mode: ssemble-clip (Long-Form YouTube Video Clipping)
        if mode == "ssemble-clip" and youtube_url:
            update_progress(f"Submitting long-form video to Ssemble AI Clipper: {youtube_url}...", 30)
            clip_res = self.ssemble_bridge.clip_youtube_video(
                youtube_url=youtube_url,
                output_path=final_short_path,
                template_id=niche.get("ssemble_template", settings.ssemble_default_template),
            )
            update_progress("Generating high-CTR metadata with Gemini 2.0 Flash...", 70)
            hook_title = clip_res.get("hook_title") or f"Viral Clip from {niche['name']}"
            script_meta = self.script_engine.generate_script(
                niche=niche,
                topic_hint=hook_title,
                exclude_topics=exclusions,
            )

            record_id = record_short(
                session_id=session_id,
                niche_id=niche["id"],
                topic=hook_title,
                hook=script_meta.hook,
                voice_id="ssemble_original_audio",
                mode=mode,
                script_data=script_meta.model_dump(),
                video_path=final_short_path,
                title=script_meta.title,
                description=script_meta.description,
                status="generated" if dry_run else "ready_for_upload",
            )
            update_progress("Ssemble clip ready!", 100)
            return {
                "session_id": session_id,
                "record_id": record_id,
                "niche": niche,
                "topic": hook_title,
                "script": script_meta.model_dump(),
                "video_path": final_short_path,
                "youtube": None,
                "mode": mode,
                "dry_run": dry_run,
            }

        # Step 2: Scout Topic / Trend
        update_progress(f"Formulating viral angle for '{niche['name']}'...", 20)
        active_topic = topic_hint or self.trend_scout.get_seed_query(niche)

        # Step 2.5: Anti-Hallucination Research Gate (Verticals v3 Innovation)
        update_progress(f"Researching verified live facts for '{active_topic}'...", 25)
        facts = self.research_gate.search_facts(active_topic)
        research_ctx = self.research_gate.format_research_context(facts)

        # Step 3: Scriptwriting with Gemini 2.0 Flash
        update_progress("Writing high-retention script with Gemini 2.0 Flash...", 35)
        script = self.script_engine.generate_script(
            niche=niche,
            topic_hint=active_topic,
            exclude_topics=exclusions,
            research_context=research_ctx,
        )

        with tempfile.TemporaryDirectory() as td:
            work_dir = Path(td)

            # Step 4: Neural Speech Synthesis
            update_progress("Synthesizing studio-grade human narration (Edge-TTS)...", 50)
            voice_id = niche.get("voice", niche.get("default_voice", settings.default_voice))
            
            if voice_id == "ChristopherNeural":
                voice_id = "en-US-ChristopherNeural"
            elif voice_id == "GuyNeural":
                voice_id = "en-US-GuyNeural"
            elif voice_id == "AriaNeural":
                voice_id = "en-US-AriaNeural"
                
            voice_rate = niche.get("voice_rate", settings.voice_rate)
            beats_meta = self.neural_tts.synthesize_beats(
                beats=script.beats,
                work_dir=work_dir,
                voice=voice_id,
                rate=voice_rate,
            )

            # Concatenate beat audio tracks
            raw_audio = str(work_dir / "raw_narration.mp3")
            audio_paths = [b["audio_path"] for b in beats_meta]
            self.neural_tts.concat_audio_files(audio_paths, raw_audio, work_dir)

            # Master audio with loudness normalization (-14 LUFS)
            master_audio = str(work_dir / "master_audio.mp3")
            self.audio_master.normalize_loudness(raw_audio, master_audio, target_lufs=-14.0)

            # Step 5: Source Visual B-roll Footage
            update_progress("Sourcing HD stock footage & generating visuals...", 65)
            raw_footage_paths = self.stock_sourcer.source_beat_footage(
                beats=script.beats,
                work_dir=work_dir,
                niche=niche,
            )

            # Step 6: Dynamic Motion FX (Ken Burns & 9:16 Reframe)
            update_progress("Applying 9:16 reframe & Ken Burns motion...", 75)
            reframed_clips = []
            for i, (clip_p, meta) in enumerate(zip(raw_footage_paths, beats_meta)):
                out_clip = str(work_dir / f"clip_{i:02d}.mp4")
                self.motion_fx_clip = MotionFX.reframe_and_animate(
                    input_video=clip_p,
                    output_video=out_clip,
                    target_duration=meta["duration"],
                    apply_ken_burns=True,
                    beat_index=i,
                )
                reframed_clips.append(out_clip)

            # Step 7: Video Assembly
            highlight_color = niche.get("captions", {}).get("highlight_color", "&H0000FFFF&")

            if mode == "ssemble-ai":
                update_progress("Polishing video with Ssemble Cloud AI engine...", 85)
                # First assemble rough local cut
                rough_local = str(work_dir / "rough_cut.mp4")
                self.local_assembler.assemble_short(
                    beat_clips=reframed_clips,
                    beats_meta=beats_meta,
                    master_audio_path=master_audio,
                    final_output_path=rough_local,
                    work_dir=work_dir,
                    highlight_color=highlight_color,
                )
                try:
                    self.ssemble_bridge.polish_with_ssemble(
                        local_video_path=rough_local,
                        output_path=final_short_path,
                    )
                except Exception as e:
                    logger.warning(f"Ssemble Cloud Bridge failed: {e}. Falling back gracefully to Local Studio.")
                    # Fallback to local assembly
                    self.local_assembler.assemble_short(
                        beat_clips=reframed_clips,
                        beats_meta=beats_meta,
                        master_audio_path=master_audio,
                        final_output_path=final_short_path,
                        work_dir=work_dir,
                        highlight_color=highlight_color,
                    )
            else:
                # Standalone Local Studio Engine (Hormozi ASS animated captions)
                update_progress("Assembling 1080x1920 Short with animated karaoke subtitles...", 85)
                self.local_assembler.assemble_short(
                    beat_clips=reframed_clips,
                    beats_meta=beats_meta,
                    master_audio_path=master_audio,
                    final_output_path=final_short_path,
                    work_dir=work_dir,
                    highlight_color=highlight_color,
                )

        # Step 8: Record in SQLite Database
        record_id = record_short(
            session_id=session_id,
            niche_id=niche["id"],
            topic=active_topic,
            hook=script.hook,
            voice_id=voice_id,
            mode=mode,
            script_data=script.model_dump(),
            video_path=final_short_path,
            title=script.title,
            description=script.description,
            status="generated" if dry_run else "ready_for_upload",
        )

        upload_result = None
        update_progress(f"Generation complete. Ready for manual upload.", 100)

        return {
            "session_id": session_id,
            "record_id": record_id,
            "niche": niche,
            "topic": active_topic,
            "script": script.model_dump(),
            "video_path": final_short_path,
            "youtube": upload_result,
            "mode": mode,
            "dry_run": dry_run,
        }
