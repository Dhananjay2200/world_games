"""
WorldGames AI - SEO Service.
Generates URL-friendly slugs, search-optimized meta descriptions, and keywords.
"""

import re
import json
from typing import Dict, List
from app.llm import get_chat_llm
from app.utils.logging import logger


class SEOService:
    def __init__(self):
        self.llm = get_chat_llm(temperature=0.3, max_tokens=300)

    def generate_slug(self, topic_name: str, category: str) -> str:
        """Creates a clean, URL-safe slug."""
        raw = f"{topic_name} {category} rules guide".lower()
        cleaned = re.sub(r"[^\w\s-]", "", raw)
        slug = re.sub(r"[\s_-]+", "-", cleaned).strip("-")
        return slug

    def calculate_reading_time(self, content: str) -> int:
        """Calculates estimated reading time based on standard 200 words per minute."""
        words = len(content.split())
        return max(1, round(words / 200))

    async def generate_seo_metadata(self, topic_name: str, category: str, region: str, country: str, summary: str) -> Dict:
        """Uses LLM to craft high-CTR meta description and high-intent SEO keywords."""
        prompt = f"""You are an SEO strategist specializing in global sports and games.
Create optimized SEO metadata for an encyclopedic article on:
- Sport/Game: {topic_name}
- Category: {category}
- Region: {region} ({country})
- Summary: {summary}

Respond in strict JSON with keys:
- "meta_description": string (Between 140 and 160 characters, compelling with a call to action)
- "keywords": array of 8-10 high search-intent keyword phrases
- "social_hashtags": array of 4-6 hashtags

Do not output code blocks or markdown, only raw JSON."""

        try:
            resp = await self.llm.ainvoke(prompt)
            content = resp.content.strip()
            if content.startswith("```"):
                content = content.strip("`").replace("json\n", "", 1).strip()
            data = json.loads(content)
            
            slug = self.generate_slug(topic_name, category)
            return {
                "slug": slug,
                "meta_description": data.get("meta_description", f"Learn the authentic rules, playing dimensions, history, and tactics of {topic_name} in our definitive world sports guide."),
                "keywords": data.get("keywords", [topic_name, f"{topic_name} rules", f"how to play {topic_name}", category, region]),
                "hashtags": data.get("social_hashtags", [f"#{topic_name.replace(' ', '')}", "#WorldGames", "#SportsHistory"]),
            }
        except Exception as e:
            logger.warning(f"SEO generation error: {e}, using rule-based fallback.")
            slug = self.generate_slug(topic_name, category)
            meta = f"Discover the complete guide to {topic_name}: rules, equipment, origins in {country}, and master playing tactics. Read now."
            return {
                "slug": slug,
                "meta_description": meta[:160],
                "keywords": [topic_name, f"{topic_name} rules", f"how to play {topic_name}", category, country],
                "hashtags": [f"#{topic_name.replace(' ', '')}", "#WorldGames"],
            }
