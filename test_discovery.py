"""
Test script for Topic Discovery Service across regions and categories.
"""

import asyncio
from app.database.session import SessionLocal
from app.services.discovery_service import DiscoveryService, WORLD_REGIONS, GAME_CATEGORIES


async def test_discovery():
    print("=" * 65)
    print(" WorldGames AI - Phase 1: Topic Discovery Diagnostic")
    print("=" * 65)
    
    db = SessionLocal()
    try:
        service = DiscoveryService(db)
        
        print(f"[*] Total Supported Regions: {len(WORLD_REGIONS)}")
        print(f"[*] Total Game Categories:   {len(GAME_CATEGORIES)}")
        
        # Test 1: Discover from South Asia (e.g. Kabaddi or Mallakhamb)
        res1 = await service.discover_new_game(target_region="South Asia")
        print(f"[+] Discovered Game 1: {res1['name']} | Category: {res1['category']} | Country: {res1.get('origin_country')}")
        
        # Test 2: Discover from Southeast Asia (e.g. Sepak Takraw)
        res2 = await service.discover_new_game(target_region="Southeast Asia")
        print(f"[+] Discovered Game 2: {res2['name']} | Category: {res2['category']} | Country: {res2.get('origin_country')}")
        
        # Test 3: Discover from Europe
        res3 = await service.discover_new_game(target_region="Europe")
        print(f"[+] Discovered Game 3: {res3['name']} | Category: {res3['category']} | Country: {res3.get('origin_country')}")
        
        print("[+] Topic discovery across continents passed successfully!")
    finally:
        db.close()
    print("=" * 65)


if __name__ == "__main__":
    asyncio.run(test_discovery())
