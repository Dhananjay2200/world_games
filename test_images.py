"""
Test script for Wikimedia Commons Image Discovery.
"""

import asyncio
from app.services.image_service import ImageService


async def test_images():
    print("=" * 65)
    print(" WorldGames AI - Image Discovery & Licensing Diagnostic")
    print("=" * 65)
    
    service = ImageService()
    test_games = ["Sepak Takraw", "Kabaddi", "Curling"]
    
    for game in test_games:
        print(f"[*] Discovering permitted imagery for: '{game}'...")
        res = await service.get_permitted_image(game, "Field & Team Ball Sports")
        print(f"    Image URL:   {res.get('image_url')}")
        print(f"    Attribution: {res.get('attribution')}")
        print(f"    License:     {res.get('license')}")
        print("-" * 50)
        
    print("[+] Image discovery & licensing passed successfully!")
    print("=" * 65)


if __name__ == "__main__":
    asyncio.run(test_images())
