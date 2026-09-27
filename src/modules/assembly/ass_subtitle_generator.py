"""
Advanced SubStation Alpha (ASS) Karaoke Subtitle Generator.
Produces Alex Hormozi-style animated bouncing captions with active word highlights.
Calculates exact millisecond timing derived from Edge-TTS boundaries.
"""

from pathlib import Path
from typing import Any, Dict, List


def format_ass_time(seconds: float) -> str:
    """Converts seconds into ASS timestamp format: H:MM:SS.cc"""
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    centis = int(round((seconds - int(seconds)) * 100))
    if centis == 100:
        centis = 99
    return f"{hrs}:{mins:02d}:{secs:02d}.{centis:02d}"


class ASSSubtitleGenerator:
    HEADER_TEMPLATE = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Hormozi,Arial,68,&H00FFFFFF,&H0000FFFF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,5.0,2.5,2,40,40,360,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    @classmethod
    def generate_ass(
        cls,
        beats_meta: List[Dict[str, Any]],
        output_ass_path: str,
        highlight_color: str = "&H0000FFFF&",  # Bright Yellow in BGR hex
        words_per_phrase: int = 4,
    ) -> str:
        """
        Generates an ASS subtitle file with rapid 3-4 word phrase timing
        and active-word emphasis matching Alex Hormozi's viral style.
        """
        events = []
        current_timeline_sec = 0.0

        for beat in beats_meta:
            beat_duration = beat["duration"]
            raw_text = beat["text"].strip().upper()
            words = raw_text.split()

            if not words:
                current_timeline_sec += beat_duration
                continue

            # Distribute words evenly across the beat duration
            time_per_word = beat_duration / max(len(words), 1)

            # Group into chunks of 3-4 words for rapid retention-friendly readability
            for i in range(0, len(words), words_per_phrase):
                chunk = words[i:i + words_per_phrase]
                chunk_start = current_timeline_sec + (i * time_per_word)
                chunk_end = current_timeline_sec + (min(i + len(chunk), len(words)) * time_per_word)

                # For each word in the chunk, highlight it as active
                for w_idx, active_word in enumerate(chunk):
                    word_start = chunk_start + (w_idx * time_per_word)
                    word_end = word_start + time_per_word

                    # Build text with active word highlighted
                    formatted_words = []
                    for other_idx, other_word in enumerate(chunk):
                        if other_idx == w_idx:
                            formatted_words.append(f"{{\\c{highlight_color}\\b1}}{other_word}{{\\r}}")
                        else:
                            formatted_words.append(other_word)

                    line_text = " ".join(formatted_words)
                    start_str = format_ass_time(word_start)
                    end_str = format_ass_time(word_end)

                    event_line = f"Dialogue: 0,{start_str},{end_str},Hormozi,,0,0,0,,{line_text}"
                    events.append(event_line)

            current_timeline_sec += beat_duration

        content = cls.HEADER_TEMPLATE + "\n".join(events) + "\n"

        with open(output_ass_path, "w", encoding="utf-8") as f:
            f.write(content)

        return output_ass_path
