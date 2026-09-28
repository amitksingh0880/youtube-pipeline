"""
Viral Script Engine powered by Google Gemini 2.0 Flash.
Uses the official google-genai SDK with strict Pydantic structured output.
Enforces the 2026 YouTube Shorts 4-act viral retention framework.
"""

import json
import logging
from typing import List, Optional
from pydantic import BaseModel, Field
from google import genai
from google.genai import types
from src.core.config import settings

logger = logging.getLogger(__name__)


class ScriptBeat(BaseModel):
    beat_number: int = Field(description="Sequential beat index starting at 1")
    text: str = Field(description="Spoken narration sentence for this beat, crisp and conversational")
    visual_query: str = Field(description="2-4 word concrete search term for HD stock B-roll footage")
    duration_est: float = Field(description="Estimated spoken duration in seconds (typically 3.0 to 6.0s)")


class YouTubeShortScript(BaseModel):
    hook_type: str = Field(description="Hook framework used: Pattern Interrupt, Curiosity Gap, or Counter-Intuitive Claim")
    hook: str = Field(description="First spoken line, said in the first 0-2 seconds, under 15 words")
    beats: List[ScriptBeat] = Field(description="Ordered list of 4 to 6 narrative beats")
    loop_anchor: str = Field(description="The final phrase that flows seamlessly back into the first word of the hook")
    title: str = Field(description="High-CTR YouTube title under 60 chars, compelling and non-clickbait")
    description: str = Field(description="SEO description (2-3 sentences) with #Shorts and relevant topic hashtags")
    tags: List[str] = Field(description="5 to 8 targeted YouTube tags")
    pinned_comment: str = Field(description="Engaging question or prompt for the pinned comment section")


SYSTEM_INSTRUCTION = """You are an elite YouTube Shorts scriptwriter and retention director.
You write viral, educational, and psychology-driven short-form video scripts (45 to 55 seconds spoken, ~120 to 145 words total).

Your scripts must strictly follow the 2026 YouTube Shorts Retention Architecture:
1. Act 1: The Pattern Interrupt (0-2s, Beat 1)
   - Must stop scrolling immediately.
   - BANNED CLICHÉS: "Did you know", "Have you ever wondered", "In this video", "Welcome back", "Today we talk about".
   - Start right in the middle of the action or with a shocking counter-intuitive statement.

2. Act 2: The Stakes & Tension (2-15s, Beat 2)
   - Introduce the central mystery, conflict, or high stakes. Why should the viewer care?

3. Act 3: Escalation & Twists (15-40s, Beats 3-5)
   - Reveal surprising facts, historical turns, or psychological insights in rapid, punchy sentences.
   - Each beat must pair with a specific, concrete 2-4 word visual query for stock footage.

4. Act 4: The Climax & Infinite Loop Anchor (40-55s, Final Beat)
   - Deliver the payoff or conclusion.
   - The very last words of the script MUST syntactically and rhythmically connect directly back to the first word of Beat 1, creating an infinite watch loop.

Tone: Authoritative, intriguing, fast-paced, conversational, completely free of fluff."""


class ScriptEngine:
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key if api_key is not None else settings.gemini_api_key
        self.model = model or settings.gemini_model
        self.client = genai.Client(api_key=self.api_key) if self.api_key else None

    def generate_script(
        self,
        niche: dict,
        topic_hint: Optional[str] = None,
        exclude_topics: Optional[List[str]] = None,
        research_context: Optional[str] = None,
    ) -> YouTubeShortScript:
        """
        Generates a viral YouTube Short script conforming strictly to YouTubeShortScript schema.
        Integrates anti-hallucination verified research facts.
        """
        # If API key is not configured, return an intelligent mock script for dry-run/testing
        if not self.client:
            return self._generate_offline_mock(niche, topic_hint)

        exclude_block = ""
        if exclude_topics:
            formatted = "\n".join(f"- {t}" for t in exclude_topics[-25:])
            exclude_block = f"\n\nDO NOT repeat or closely imitate any of these recently covered topics:\n{formatted}"

        research_block = ""
        if research_context:
            research_block = f"\n\n{research_context}\n\nSTRICT REQUIREMENT: All historical facts, numbers, dates, and names in your script must be grounded in the verified research facts above. Do NOT hallucinate unverified claims."

        language_rule = ""
        if niche.get("language") == "hi":
            language_rule = "\n\nCRITICAL LANGUAGE REQUIREMENT: Write the entire script (including all beats and the hook) strictly in native Hindi using the Devanagari script (e.g., नमस्ते). Do not write in English or Hinglish."

        prompt = f"""Target Niche: {niche['name']} ({niche.get('description', '')})
Topic Hint: {topic_hint or 'Pick the most fascinating, viral, and lesser-known story/concept in this niche.'}{exclude_block}{research_block}{language_rule}

Requirements:
- Target spoken length: 45-55 seconds (120-145 words total).
- 4 to 6 beats total.
- Ensure the final beat ends on an infinite loop anchor that loops into the first sentence.
- Provide concrete, cinematic 2-4 word visual queries for B-roll footage (these can stay in English).
- Output ONLY valid JSON conforming to the requested schema."""

        candidate_models = [self.model, "gemini-flash-latest", "gemini-3.5-flash", "gemini-3.7-flash"]
        unique_models = list(dict.fromkeys([m for m in candidate_models if m]))

        last_error = None
        for target_model in unique_models:
            try:
                response = self.client.models.generate_content(
                    model=target_model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_INSTRUCTION,
                        response_mime_type="application/json",
                        response_schema=YouTubeShortScript,
                        temperature=0.8,
                    ),
                )
                script = YouTubeShortScript.model_validate_json(response.text)
                return script
            except Exception as e:
                last_error = e
                continue

        logger.warning(f"All Gemini candidate models failed ({last_error}). Falling back to offline mock script.")
        return self._generate_offline_mock(niche, topic_hint)

    def _generate_offline_mock(self, niche: dict, topic_hint: Optional[str] = None) -> YouTubeShortScript:
        """Offline high-quality mock script for local testing when no Gemini key is set."""
        niche_id = niche.get("id", "dark_history")
        
        if niche.get("language") == "hi":
            return YouTubeShortScript(
                hook_type="Curiosity Gap",
                hook="चाणक्य की यह एक नीति आपकी पूरी जिंदगी बदल सकती है।",
                beats=[
                    ScriptBeat(
                        beat_number=1,
                        text="चाणक्य की यह एक नीति आपकी पूरी जिंदगी बदल सकती है।",
                        visual_query="ancient indian scholar meditating",
                        duration_est=4.5,
                    ),
                    ScriptBeat(
                        beat_number=2,
                        text="उन्होंने कहा था कि इंसान की सबसे बड़ी ताकत उसका ज्ञान नहीं, बल्कि उसका धैर्य है।",
                        visual_query="warrior standing on mountain",
                        duration_est=6.5,
                    ),
                    ScriptBeat(
                        beat_number=3,
                        text="जब मुसीबत आती है, तो अज्ञानी लोग घबरा जाते हैं।",
                        visual_query="stormy ocean dark clouds",
                        duration_est=5.0,
                    ),
                    ScriptBeat(
                        beat_number=4,
                        text="लेकिन एक बुद्धिमान व्यक्ति उस तूफान में भी शांत रहता है और अपना रास्ता खोज लेता है।",
                        visual_query="sunrise shining through clouds",
                        duration_est=6.0,
                    ),
                    ScriptBeat(
                        beat_number=5,
                        text="इसलिए हमेशा धैर्य रखें, और अपनी बुद्धि से हर मुश्किल को पार करें।",
                        visual_query="ancient book open glowing",
                        duration_est=4.5,
                    ),
                ],
                loop_anchor="और अपनी बुद्धि से हर मुश्किल को पार करें।",
                title="चाणक्य नीति जो जिंदगी बदल देगी #Shorts",
                description="जीवन में सफलता के लिए चाणक्य की सबसे शक्तिशाली नीति। #Shorts #Chanakya #Motivation",
                tags=["shorts", "hindi", "chanakya", "motivation", "success"],
                pinned_comment="क्या आप इस नीति से सहमत हैं? कमेंट में बताएं!",
            )
            
        if niche_id == "dark_history":
            return YouTubeShortScript(
                hook_type="Pattern Interrupt",
                hook="The CIA spent twenty million dollars training a cat to be an international spy.",
                beats=[
                    ScriptBeat(
                        beat_number=1,
                        text="The CIA spent twenty million dollars training a cat to be an international spy.",
                        visual_query="secret agent vintage trench coat",
                        duration_est=4.2,
                    ),
                    ScriptBeat(
                        beat_number=2,
                        text="In the nineteen-sixties, Project Acoustic Kitty implanted a microphone inside a cat's ear canal and a transmitter at the base of its skull.",
                        visual_query="vintage cold war laboratory",
                        duration_est=6.5,
                    ),
                    ScriptBeat(
                        beat_number=3,
                        text="The goal was simple: listen to Soviet embassy diplomats in public parks without raising any suspicion.",
                        visual_query="park bench shadowy figures whispering",
                        duration_est=5.0,
                    ),
                    ScriptBeat(
                        beat_number=4,
                        text="On its very first real-world mission, operatives released the cat across from the Soviet compound in Washington.",
                        visual_query="washington dc 1960s street",
                        duration_est=5.2,
                    ),
                    ScriptBeat(
                        beat_number=5,
                        text="Within seconds, the secret agent cat wandered into traffic and was immediately struck by an oncoming taxi.",
                        visual_query="vintage taxi driving away",
                        duration_est=5.0,
                    ),
                    ScriptBeat(
                        beat_number=6,
                        text="The program was canceled forever, leaving historians stunned by the fact that...",
                        visual_query="classified secret document top secret stamp",
                        duration_est=4.5,
                    ),
                ],
                loop_anchor="leaving historians stunned by the fact that...",
                title="The $20M Spy Cat That Lasted 5 Minutes #Shorts",
                description="The bizarre true story of the CIA's Cold War acoustic kitty project. #Shorts #History #ColdWar",
                tags=["shorts", "history", "cia", "cold war", "weird history", "acoustic kitty"],
                pinned_comment="Would you have trusted a secret agent cat? Let me know your thoughts!",
            )
        else:
            return YouTubeShortScript(
                hook_type="Curiosity Gap",
                hook="Your subconscious mind makes decisions seven seconds before you are even aware of them.",
                beats=[
                    ScriptBeat(
                        beat_number=1,
                        text="Your subconscious mind makes decisions seven seconds before you are even aware of them.",
                        visual_query="human brain glowing synapses",
                        duration_est=4.5,
                    ),
                    ScriptBeat(
                        beat_number=2,
                        text="Neuroscientists used brain scanners to track electrical activity while participants chose between two simple buttons.",
                        visual_query="neuroscience MRI scanner hospital",
                        duration_est=5.5,
                    ),
                    ScriptBeat(
                        beat_number=3,
                        text="The computer accurately predicted which hand they would press seconds before the conscious urge even formed.",
                        visual_query="digital futuristic data screen",
                        duration_est=5.0,
                    ),
                    ScriptBeat(
                        beat_number=4,
                        text="This means our feeling of deliberate conscious control might just be a story our brain tells itself after the choice is already locked in.",
                        visual_query="man thinking deep portrait shadow",
                        duration_est=6.5,
                    ),
                    ScriptBeat(
                        beat_number=5,
                        text="Which makes you question if you are truly in control, or if...",
                        visual_query="infinite mirror reflection hallway",
                        duration_est=4.2,
                    ),
                ],
                loop_anchor="or if...",
                title="You Aren't in Control of Your Brain #Shorts",
                description="The shocking neuroscience experiment revealing the 7-second delay of free will. #Shorts #Psychology #Brain",
                tags=["shorts", "psychology", "neuroscience", "mind", "facts"],
                pinned_comment="Do you believe in free will, or is it an illusion? Drop your take below!",
            )
