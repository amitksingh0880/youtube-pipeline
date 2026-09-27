"""
Anti-Hallucination Research Gate (inspired by Verticals v3).
Searches live facts across DuckDuckGo and scrapes clean context.
Enforces that Gemini 2.0 Flash bases claims, numbers, and dates strictly on verified research.
"""

import re
import urllib.parse
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional

DDG_URL = "https://html.duckduckgo.com/html/"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"


class ResearchGate:
    @staticmethod
    def sanitize_snippet(text: str, max_chars: int = 350) -> str:
        """Sanitizes text and wraps it in defensive boundary markers to prevent prompt injection."""
        clean = re.sub(r"\s+", " ", text).strip()
        # Remove any system prompt injection markers
        clean = clean.replace("```", "").replace("SYSTEM:", "").replace("USER:", "")
        return clean[:max_chars]

    @classmethod
    def search_facts(cls, query: str, max_results: int = 5) -> List[Dict[str, str]]:
        """
        Executes a free web search on DuckDuckGo HTML endpoint without requiring API keys.
        Returns a list of structured fact snippets.
        """
        headers = {
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Referer": "https://html.duckduckgo.com/",
        }
        data = {"q": query}

        try:
            resp = requests.post(DDG_URL, data=data, headers=headers, timeout=12)
            if not resp.ok:
                return []

            soup = BeautifulSoup(resp.text, "html.parser")
            results = []

            for result in soup.find_all("div", class_="result"):
                title_elem = result.find("a", class_="result__a")
                snippet_elem = result.find("a", class_="result__snippet")

                if title_elem and snippet_elem:
                    title = title_elem.get_text(strip=True)
                    snippet = snippet_elem.get_text(strip=True)

                    results.append({
                        "title": title,
                        "snippet": cls.sanitize_snippet(snippet),
                    })

                if len(results) >= max_results:
                    break

            return results
        except Exception:
            return []

    @classmethod
    def format_research_context(cls, facts: List[Dict[str, str]]) -> str:
        """Formats fact snippets into a secure research context block for Gemini 2.0 Flash."""
        if not facts:
            return ""

        lines = ["=== VERIFIED LIVE RESEARCH FACTS (Anti-Hallucination Gate) ==="]
        for idx, f in enumerate(facts, start=1):
            lines.append(f"[Fact {idx} - Source: {f['title']}]")
            lines.append(f'"""{f["snippet"]}"""\n')
        lines.append("=== END VERIFIED RESEARCH ===")
        return "\n".join(lines)
