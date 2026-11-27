"""
WorldGames AI - Editorial Writer Service.
Generates comprehensive 12-section encyclopedic guides OR dynamic sports news dispatches.
"""

from datetime import date
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

SYSTEM_NEWS_PROMPT = """You are a senior breaking sports journalist and editor for WorldGames.
Your task is to write a timely, factual, publication-grade sports news dispatch grounded strictly in the latest verified news items and timestamps provided in the prompt.

Format requirements:
# [Punchy, Accurate Breaking News Headline]

## 1. Breaking Lead & Key Takeaways
- Concise summary of the latest development, dates, teams/athletes, and verified facts.

## 2. Story Context & Significance
- Why this news matters right now for the sport, league, or upcoming competition.

## 3. Detailed Breakdown & Key Highlights
- Specific details from the reported news findings (transfers, match developments, announcements, or rule/tournament updates).

## 4. Key Figures, Teams & Sources
- Bullet points or a clean Markdown table summarizing the verified parties, dates, and developments mentioned in the sources.

## 5. What Lies Ahead
- Immediate next fixtures, deadlines, or impact on upcoming events.

Strict rules:
- Prioritize the latest news findings (with their `Published` timestamps and `Source`) over historical background.
- Do NOT invent fake scores, fake quotes, or outdated past-year results.
- Active journalistic tone, 650–1100 words, clean Markdown.
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
            today_str = date.today().isoformat()
            news_items = (
                research_dossier.get("live_news")
                or research_dossier.get("apitube_news")
                or findings
            )
            live_news_text = "\n".join([
                f"- [{f.get('published_at') or 'Recent'} | {f.get('source') or 'Wire'}] "
                f"{f.get('title')}: {f.get('content')} (URL: {f.get('url', '')})"
                for f in news_items[:6]
            ]) or findings_text

            logger.info(f"Generating Latest Sports News for: {topic_name} (Date: {today_str}, Angle: {news_angle or 'Latest Live Headlines'})")
            user_prompt = f"""Today's Date: {today_str}
Sport / Topic: {topic_name}
Category: {category}
Region: {region} ({country})
Requested Focus / Angle: {news_angle or 'Report the most recent breaking news from the live wire findings below'}

LATEST LIVE NEWS WIRE FINDINGS (Primary Source — prioritize newest timestamps):
{live_news_text}

Brief Sport Context (Secondary background only):
{wiki_summary[:600]}

Write the breaking sports news article strictly grounded in the latest news wire findings above."""

            response = await self.llm.ainvoke([
                {"role": "system", "content": SYSTEM_NEWS_PROMPT},
                {"role": "user", "content": user_prompt}
            ])
            full_content = response.content.strip()

            lines = full_content.splitlines()
            title = f"{topic_name}: {news_angle or 'Latest Breaking News & Updates'}"
            found_title = False
            summary_candidates = []
            for l in lines:
                stripped = l.strip()
                if stripped.startswith("# ") and not found_title:
                    title = stripped.replace("# ", "").strip()
                    found_title = True
                elif stripped and not stripped.startswith("#") and not stripped.startswith("|"):
                    clean_line = stripped.lstrip("-* ").replace("**", "").strip()
                    if len(clean_line) > 40:
                        summary_candidates.append(clean_line)
                        if len(summary_candidates) >= 2:
                            break

            summary = (
                " ".join(summary_candidates)[:280]
                if summary_candidates
                else f"Latest breaking news dispatch covering {topic_name} ({category})."
            )

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
