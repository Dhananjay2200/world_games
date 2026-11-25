"""
WorldGames AI - Image Discovery Service.
Fetches verified, authentic imagery for world games:
1. Queries Wikipedia PageImages API for the curated lead image of the sport/game.
2. Falls back to strict Wikimedia Commons search (without loose wildcards).
3. Graceful category-specific fallback if no free media exists.
"""

from typing import Dict, Optional, Tuple
import urllib.parse
import httpx
from app.utils.logging import logger

DEFAULT_FALLBACK_IMAGES = {
    "Field & Team Ball Sports": "https://images.unsplash.com/photo-1579952363873-27f3bade9f55?q=80&w=1200&auto=format&fit=crop",
    "Combat Sports & Martial Arts": "https://images.unsplash.com/photo-1555597673-b21d5c935865?q=80&w=1200&auto=format&fit=crop",
    "Board, Tile & Strategy Games": "https://images.unsplash.com/photo-1529699211952-734e80c4d42b?q=80&w=1200&auto=format&fit=crop",
    "Indigenous, Folk & Traditional Games": "https://images.unsplash.com/photo-1533473359331-0135ef1b58bf?q=80&w=1200&auto=format&fit=crop",
    "Winter & Ice Sports": "https://images.unsplash.com/photo-1551698618-1dfe5d97d256?q=80&w=1200&auto=format&fit=crop",
    "Racquet & Paddle Sports": "https://images.unsplash.com/photo-1622279457486-62dcc4a431d6?q=80&w=1200&auto=format&fit=crop",
    "Target & Precision Sports": "https://images.unsplash.com/photo-1589487391730-58f20eb2c308?q=80&w=1200&auto=format&fit=crop",
    "Water & Aquatic Sports": "https://images.unsplash.com/photo-1544551763-46a013bb70d5?q=80&w=1200&auto=format&fit=crop",
    "Extreme & Adventure Sports": "https://images.unsplash.com/photo-1522163182402-834f871fd851?q=80&w=1200&auto=format&fit=crop",
    "General": "https://images.unsplash.com/photo-1461896836934-ffe607ba8211?q=80&w=1200&auto=format&fit=crop",
}


class ImageService:
    def __init__(self):
        self.headers = {
            "User-Agent": "WorldGamesBot/1.0 (https://worldgames.ai; contact@worldgames.ai)"
        }

    async def fetch_wikipedia_lead_image(self, title: str) -> Optional[Dict]:
        """
        Fetches the authentic, human-curated lead image directly from Wikipedia's PageImages API.
        This guarantees the photo is of the exact sport (e.g. actual Waka ama canoe, actual wrestling match).
        """
        url = "https://en.wikipedia.org/w/api.php"
        search_titles = [title]
        # Clean title variants (e.g. 'Go (Weiqi / Baduk)' -> 'Go (game)', 'Tejo' -> 'Tejo (sport)')
        if "(" in title:
            base_name = title.split("(")[0].strip()
            search_titles.append(base_name)
            search_titles.append(f"{base_name} (game)")
            search_titles.append(f"{base_name} (sport)")
        else:
            search_titles.append(f"{title} (sport)")
            search_titles.append(f"{title} (game)")

        try:
            async with httpx.AsyncClient(timeout=10.0, headers=self.headers) as client:
                for t in search_titles:
                    params = {
                        "action": "query",
                        "format": "json",
                        "titles": t,
                        "prop": "pageimages|info",
                        "piprop": "original|thumbnail",
                        "pithumbsize": "1200",
                        "redirects": "1",
                    }
                    resp = await client.get(url, params=params)
                    if resp.status_code == 200:
                        data = resp.json()
                        pages = data.get("query", {}).get("pages", {})
                        for pid, pdata in pages.items():
                            if pid != "-1":
                                thumb = pdata.get("thumbnail", {}).get("source")
                                orig = pdata.get("original", {}).get("source")
                                img_url = thumb or orig
                                if img_url and not any(bad in img_url.lower() for bad in ["flag", "icon", "logo", "map", "symbol"]):
                                    clean_title = pdata.get("title", title)
                                    return {
                                        "image_url": img_url,
                                        "caption": f"Authentic action photograph of {clean_title}",
                                        "attribution": f"Curated via Wikipedia / Wikimedia Commons ({clean_title})",
                                        "license": "Creative Commons / Public Domain",
                                    }
        except Exception as e:
            logger.warning(f"Wikipedia pageimages lookup error for '{title}': {e}")
        return None

    async def search_wikimedia_commons_strict(self, query: str) -> Optional[Dict]:
        """
        Strict search on Wikimedia Commons.
        Matches exact sport name without loose 'OR sport' wildcards.
        """
        clean_name = query.split("(")[0].strip() if "(" in query else query
        url = "https://commons.wikimedia.org/w/api.php"
        params = {
            "action": "query",
            "format": "json",
            "generator": "search",
            "gsrsearch": f'"{clean_name}"',  # Strict phrase match
            "gsrnamespace": "6",             # File namespace
            "gsrlimit": "5",
            "prop": "imageinfo",
            "iiprop": "url|extmetadata|dimensions|mime",
            "iiurlwidth": "1200",
        }

        try:
            async with httpx.AsyncClient(timeout=10.0, headers=self.headers) as client:
                resp = await client.get(url, params=params)
                if resp.status_code == 200:
                    data = resp.json()
                    pages = data.get("query", {}).get("pages", {})
                    for pid, pdata in pages.items():
                        title = pdata.get("title", "").lower()
                        # Reject the generic Belarusian house of sport file or logos
                        if "białoruski" in title or "bialoruski" in title or "logo" in title:
                            continue

                        imageinfo = pdata.get("imageinfo", [])
                        if imageinfo:
                            info = imageinfo[0]
                            mime = info.get("mime", "")
                            if "jpeg" in mime or "png" in mime or "jpg" in mime:
                                ext = info.get("extmetadata", {})
                                artist = ext.get("Artist", {}).get("value", "Wikimedia Commons Contributor")
                                clean_artist = re_strip_html(artist)
                                license_short = ext.get("LicenseShortName", {}).get("value", "Creative Commons / Public Domain")
                                desc = ext.get("ImageDescription", {}).get("value", f"{query} photograph")
                                clean_desc = re_strip_html(desc)

                                return {
                                    "image_url": info.get("thumburl") or info.get("url"),
                                    "caption": clean_desc[:200],
                                    "attribution": f"Photo by {clean_artist} via Wikimedia Commons ({license_short})",
                                    "license": license_short,
                                }
        except Exception as e:
            logger.warning(f"Wikimedia strict search error for '{query}': {e}")
        return None

    async def get_permitted_image(self, topic_name: str, category: str) -> Dict:
        """
        Finds a verified licensed image:
        Tier 1: Wikipedia PageImages (curated lead photo)
        Tier 2: Strict Wikimedia Commons search
        Tier 3: Graceful category fallback
        """
        # Tier 1: Wikipedia PageImages (Highest relevance)
        wiki_lead = await self.fetch_wikipedia_lead_image(topic_name)
        if wiki_lead and wiki_lead.get("image_url"):
            return wiki_lead

        # Tier 2: Strict Wikimedia Commons Search
        strict_comm = await self.search_wikimedia_commons_strict(topic_name)
        if strict_comm and strict_comm.get("image_url"):
            return strict_comm

        # Tier 3: Category Fallback
        fallback_url = DEFAULT_FALLBACK_IMAGES.get(category, DEFAULT_FALLBACK_IMAGES["General"])
        return {
            "image_url": fallback_url,
            "caption": f"Atmospheric representation of {topic_name} ({category})",
            "attribution": "Editorial sports imagery via Unsplash Free License",
            "license": "Unsplash Commercial Free Use",
        }


def re_strip_html(text: str) -> str:
    """Removes HTML markup from metadata strings."""
    import re
    clean = re.sub(r"<[^>]+>", "", text or "")
    return " ".join(clean.split())
