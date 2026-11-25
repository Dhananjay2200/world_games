"""
Test script for Multi-Source Research Service (Wikipedia + Tavily).
"""

import asyncio
from app.services.research_service import ResearchService


async def test_research():
    print("=" * 65)
    print(" WorldGames AI - Phase 2: Research Diagnostic")
    print("=" * 65)
    
    service = ResearchService()
    test_game = "Sepak Takraw"
    category = "Racquet & Paddle Sports"
    
    print(f"[*] Querying Wikipedia & Tavily for: {test_game}...")
    dossier = await service.gather_full_research(
        topic_name=test_game,
        category=category,
        region="Southeast Asia",
        country="Malaysia / Thailand",
    )
    
    wiki_len = len(dossier.get("wikipedia_summary", ""))
    tavily_count = len(dossier.get("search_findings", []))
    print(f"[+] Wikipedia Summary Length: {wiki_len} characters")
    if wiki_len > 0:
        print(f"[+] Wikipedia Snippet: {dossier['wikipedia_summary'][:200]}...")
    print(f"[+] Tavily Search Results:  {tavily_count} items")
    print("[+] Research service diagnostic completed successfully!")
    print("=" * 65)


if __name__ == "__main__":
    asyncio.run(test_research())
