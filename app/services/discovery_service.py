"""
WorldGames AI - Topic Discovery Service.
Rotates through 10 global regions and 12 game genres to discover both celebrated
world sports and rare, indigenous, traditional, or mind games.
"""

import hashlib
import json
import random
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from app.database.models import GameTopic
from app.llm import get_chat_llm
from app.utils.logging import logger

# 10 Worldwide Geographic Regions
WORLD_REGIONS = [
    "East Asia",
    "South Asia",
    "Southeast Asia",
    "Central & West Asia",
    "Europe",
    "Sub-Saharan Africa",
    "North America",
    "Latin America & Caribbean",
    "Oceania & Pacific",
    "Global & Multi-Regional",
]

# 12 Core Game Categories / Genres
GAME_CATEGORIES = [
    "Field & Team Ball Sports",
    "Combat Sports & Martial Arts",
    "Board, Tile & Strategy Games",
    "Indigenous, Folk & Traditional Games",
    "Racquet & Paddle Sports",
    "Target & Precision Sports",
    "Mind Sports & Tabletop Games",
    "Winter & Ice Sports",
    "Water & Aquatic Sports",
    "Extreme & Adventure Sports",
    "Esports & Competitive Digital Gaming",
    "Athletic & Gymnastic Disciplines",
]

# Curated seed bank to guarantee diverse, high-interest starter topics across continents
CURATED_SEED_GAMES = [
    {"name": "Sepak Takraw", "category": "Racquet & Paddle Sports", "region": "Southeast Asia", "country": "Malaysia / Thailand"},
    {"name": "Kabaddi", "category": "Indigenous, Folk & Traditional Games", "region": "South Asia", "country": "India"},
    {"name": "Hurling", "category": "Field & Team Ball Sports", "region": "Europe", "country": "Ireland"},
    {"name": "Capoeira", "category": "Combat Sports & Martial Arts", "region": "Latin America & Caribbean", "country": "Brazil"},
    {"name": "Buzkashi", "category": "Indigenous, Folk & Traditional Games", "region": "Central & West Asia", "country": "Afghanistan / Central Asia"},
    {"name": "Go (Weiqi / Baduk)", "category": "Board, Tile & Strategy Games", "region": "East Asia", "country": "China / Japan / Korea"},
    {"name": "Mancala", "category": "Board, Tile & Strategy Games", "region": "Sub-Saharan Africa", "country": "Pan-Africa"},
    {"name": "Lacrosse", "category": "Field & Team Ball Sports", "region": "North America", "country": "Haudenosaunee / North America"},
    {"name": "Australian Rules Football (AFL)", "category": "Field & Team Ball Sports", "region": "Oceania & Pacific", "country": "Australia"},
    {"name": "Curling", "category": "Winter & Ice Sports", "region": "Europe", "country": "Scotland"},
    {"name": "Pétanque", "category": "Target & Precision Sports", "region": "Europe", "country": "France"},
    {"name": "Mallakhamb", "category": "Athletic & Gymnastic Disciplines", "region": "South Asia", "country": "India"},
    {"name": "Calcio Storico Fiorentino", "category": "Indigenous, Folk & Traditional Games", "region": "Europe", "country": "Italy"},
    {"name": "Tejo", "category": "Target & Precision Sports", "region": "Latin America & Caribbean", "country": "Colombia"},
    {"name": "Dambe Boxing", "category": "Combat Sports & Martial Arts", "region": "Sub-Saharan Africa", "country": "Nigeria / Hausa"},
    {"name": "Bo-Taoshi", "category": "Field & Team Ball Sports", "region": "East Asia", "country": "Japan"},
    {"name": "Pelota Mixteca", "category": "Indigenous, Folk & Traditional Games", "region": "Latin America & Caribbean", "country": "Mexico"},
    {"name": "Ki-o-rahi", "category": "Indigenous, Folk & Traditional Games", "region": "Oceania & Pacific", "country": "New Zealand (Māori)"},
    {"name": "Chovgan (Polo Ancestor)", "category": "Field & Team Ball Sports", "region": "Central & West Asia", "country": "Azerbaijan / Iran"},
    {"name": "Hornussen", "category": "Indigenous, Folk & Traditional Games", "region": "Europe", "country": "Switzerland"},
]


def generate_canonical_key(name: str) -> str:
    """Creates a normalized lower-cased canonical string for deduplication."""
    clean = "".join(c.lower() for c in name.strip() if c.isalnum() or c in (" ", "-"))
    normalized = " ".join(clean.split())
    return normalized


def compute_sha256_hash(text: str) -> str:
    """Computes SHA-256 hash for exact deduplication indexing."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


class DiscoveryService:
    def __init__(self, db: Session):
        self.db = db

    def get_balanced_region_and_genre(self) -> tuple[str, str]:
        """Selects a region and genre balanced against past coverage."""
        selected_region = random.choice(WORLD_REGIONS)
        selected_genre = random.choice(GAME_CATEGORIES)
        return selected_region, selected_genre

    async def discover_new_game(
        self,
        target_region: Optional[str] = None,
        target_genre: Optional[str] = None
    ) -> Dict:
        """
        Discovers a game/sport topic that does not yet exist in the database.
        Balances regional and genre rotation.
        """
        region = target_region or random.choice(WORLD_REGIONS)
        genre = target_genre or random.choice(GAME_CATEGORIES)

        # 1. First check unused curated seed bank games
        existing_canonical = {
            t.canonical_name for t in self.db.query(GameTopic.canonical_name).all()
        }

        for seed in CURATED_SEED_GAMES:
            c_key = generate_canonical_key(seed["name"])
            if c_key not in existing_canonical:
                if (not target_region or seed["region"] == target_region) and \
                   (not target_genre or seed["category"] == target_genre):
                    return {
                        "name": seed["name"],
                        "canonical_name": c_key,
                        "category": seed["category"],
                        "origin_region": seed["region"],
                        "origin_country": seed["country"],
                        "source": "curated_seed",
                    }

        # 2. If seed is exhausted for this pair, use LLM to discover a novel game
        llm = get_chat_llm(temperature=0.8, max_tokens=300)
        prompt = f"""You are a global sports historian and traditional games ethnographer.
Identify 1 specific, real-world game or sport from the following parameters:
- Region: {region}
- Category: {genre}

Return ONLY valid JSON with keys:
- "name": string (Official or common English name of the game/sport)
- "category": string ("{genre}")
- "origin_region": string ("{region}")
- "origin_country": string (Country or culture where it originated)
- "brief_description": string (1-2 sentences on how it is played)

Rules:
- Must be a real, verifiable game played historically or currently.
- Do NOT return generic terms (e.g. do not just say "Football" or "Tag"). Give the specific discipline (e.g. "Gaelic Football", "Sepak Takraw", "Kabaddi", "Kho-Kho", "Calcio Fiorentino").
Do not include markdown code fences or other text."""

        try:
            response = await llm.ainvoke(prompt)
            content = response.content.strip()
            if content.startswith("```"):
                content = content.strip("`").replace("json\n", "", 1).strip()
            data = json.loads(content)

            c_key = generate_canonical_key(data["name"])
            if c_key in existing_canonical:
                # Fallback to random unused seed or append variation
                for seed in CURATED_SEED_GAMES:
                    s_key = generate_canonical_key(seed["name"])
                    if s_key not in existing_canonical:
                        return {
                            "name": seed["name"],
                            "canonical_name": s_key,
                            "category": seed["category"],
                            "origin_region": seed["region"],
                            "origin_country": seed["country"],
                            "source": "seed_fallback",
                        }

            return {
                "name": data["name"],
                "canonical_name": c_key,
                "category": data.get("category", genre),
                "origin_region": data.get("origin_region", region),
                "origin_country": data.get("origin_country", "Global"),
                "source": "llm_discovery",
            }
        except Exception as e:
            logger.warning(f"LLM discovery error, falling back to curated list: {e}")
            # Safe fallback
            fallback = random.choice(CURATED_SEED_GAMES)
            return {
                "name": fallback["name"],
                "canonical_name": generate_canonical_key(fallback["name"]),
                "category": fallback["category"],
                "origin_region": fallback["region"],
                "origin_country": fallback["country"],
                "source": "emergency_seed",
            }
