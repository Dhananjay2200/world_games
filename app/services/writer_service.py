"""
WorldGames AI - Editorial Writer Service.
Generates comprehensive 12-section encyclopedic guides OR dynamic sports news dispatches.
"""

from typing import Dict, Optional
from app.llm import get_chat_llm
from app.utils.logging import logger

SYSTEM_WRITER_PROMPT = """You are a world-class sports ethnographer, encyclopedist, and sports journalist.
Your task is to write a definitive, long-form (1500+ words), authoritative guide to the specified world game/sport.

You MUST write the article in structured Markdown adhering EXACTLY to the following 12 sections:

# [Catchy & Authoritative Title]

## 1. Overview, Origins & Etymology
## 2. Core Objective & Fundamental Concept
## 3. Playing Arena: Dimensions, Surface & Layout
## 4. Equipment & Gear Specifications
## 5. Team Composition & Player Roles
## 6. Official Rules & Match Progression
## 7. Scoring System, Points & Winning Conditions
## 8. Master Techniques, Skills & Tactical Strategies
## 9. Cultural Heritage, Rituals & Global Significance
## 10. Premier Tournaments, Leagues & Legendary Figures
## 11. International Variations & Modern Evolution
## 12. Getting Started Guide & Frequently Asked Questions

Format guidelines:
- Use clean Markdown with headers (##), bullet points, and data tables.
- Maintain an authoritative, vibrant, engaging, and culturally respectful voice.
"""

SYSTEM_NEWS_PROMPT = """You are a senior investigative sports correspondent and breaking news editor for WorldGames AI.
Your task is to write an authoritative, timely sports news dispatch or tournament report covering the specified sport/event.

You MUST format the news story in structured Markdown:

# [Punchy, Professional Sports News Headline]

## 1. Executive Summary & Key Takeaways
- The headline event, key score/outcome, and what transpired.

## 2. Tournament Context & Historical Stakes
- Why this championship, league match, or breaking development matters.

## 3. Game Progression & Critical Turning Points
- Play-by-play narrative highlighting game-changing plays, clutch defensive stands, and turning moments. Include a Markdown table summarizing key periods or score progression.

## 4. Outstanding Athletes & MVP Performances
- Individual excellence, record-setting statistics, and superstar contributions.

## 5. Tactical Breakdown & Strategies
- Formations, tactical maneuvers, and strategic decisions that decided the contest.

## 6. League Standings & What Lies Ahead
- Repercussions on the championship race, upcoming fixtures, and official quotes/reactions.

Format guidelines:
- Active, journalistic, high-energy tone.
- Length: 800 - 1200 words.
- Clean Markdown with headers, quotes, and tables where relevant.
"""


class WriterService:
    def __init__(self):
        self.llm = get_chat_llm(temperature=0.7, max_tokens=4000)

    async def generate_game_article(self, research_dossier: Dict, article_type: str = "PLAYBOOK", news_angle: Optional[str] = None) -> Dict:
        """Generates either a 12-section foundational playbook OR a sports news report."""
        topic_name = research_dossier["topic_name"]
        category = research_dossier["category"]
        region = research_dossier["origin_region"]
        country = research_dossier["origin_country"]
        wiki_summary = research_dossier.get("wikipedia_summary", "")
        findings = research_dossier.get("search_findings", [])
        findings_text = "\n".join([f"- {f.get('title')}: {f.get('content')}" for f in findings[:5]])

        if article_type == "NEWS":
            logger.info(f"Generating Sports News for: {topic_name} (Angle: {news_angle or 'Recent Tournaments & League Highlights'})")
            user_prompt = f"""Write an authoritative, breaking sports news report for the sport:
- Sport: {topic_name}
- Category: {category}
- Origin Region: {region} ({country})
- News Angle / Topic: {news_angle or 'Championship Finals, League Highlights & Rule Updates'}

Research & Background Context:
{wiki_summary}

Recent News Findings:
{findings_text}

Generate the full markdown sports news article following the 6 news sections."""

            response = await self.llm.ainvoke([
                {"role": "system", "content": SYSTEM_NEWS_PROMPT},
                {"role": "user", "content": user_prompt}
            ])
            full_content = response.content.strip()

            lines = full_content.splitlines()
            title = f"{topic_name}: {news_angle or 'Championship Clash & Latest News'}"
            for l in lines:
                if l.startswith("# "):
                    title = l.replace("# ", "").strip()
                    break

            summary = f"Breaking news and tournament dispatch on {topic_name} ({category}): analysis of pivotal plays, standout champions, and latest league standings."

            return {
                "title": title,
                "content": full_content,
                "summary": summary,
            }

        # Default: 12-section Playbook
        logger.info(f"Generating full game playbook for: {topic_name} ({category})")
        user_prompt = f"""Write the complete 12-section definitive guide for the following sport/game:
- Name: {topic_name}
- Category: {category}
- Origin Region: {region}
- Origin Country / Culture: {country}

Research Context & Wikipedia Findings:
{wiki_summary}

Additional Search Findings:
{findings_text}

Generate the full markdown guide following the 12 sections strictly without truncation."""

        response = await self.llm.ainvoke([
            {"role": "system", "content": SYSTEM_WRITER_PROMPT},
            {"role": "user", "content": user_prompt}
        ])

        full_content = response.content.strip()
        lines = full_content.splitlines()
        title = f"{topic_name}: The Ultimate Guide, Rules & Global Heritage"
        for l in lines:
            if l.startswith("# "):
                title = l.replace("# ", "").strip()
                break

        summary = f"{topic_name} is an exhilarating {category.lower()} originating from {country} ({region}). This comprehensive guide details its authentic rules, equipment specifications, tactical strategies, and cultural history."

        return {
            "title": title,
            "content": full_content,
            "summary": summary,
        }
