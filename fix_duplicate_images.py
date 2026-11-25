"""
Script to fix all existing articles that received the duplicate Białoruski Dom Sport image
by re-querying the updated ImageService with Wikipedia PageImages and strict Commons matching.
"""

import asyncio
from app.database.session import SessionLocal
from app.database.models import GameArticle
from app.services.image_service import ImageService
from app.services.cache_service import cache_service


async def fix_images():
    print("=" * 65)
    print(" WorldGames AI - Fixing Duplicate / Inaccurate Article Images")
    print("=" * 65)

    db = SessionLocal()
    image_service = ImageService()
    try:
        articles = db.query(GameArticle).all()
        fixed_count = 0

        for art in articles:
            url = art.primary_image_url or ""
            # Check if article has the duplicate image or needs authentic photo
            if "Bia%C5%82oruski" in url or "Białoruski" in url or not url or "Indoor_Athletics_Arena" in url or "GO_Sport_logo" in url:
                print(f"[*] Fixing image for: '{art.title}' (Category: {art.category})...")
                # Extract sport name
                sport_name = art.topic.name if art.topic else art.title.split(":")[0].strip()
                
                # Fetch authentic image
                new_img = await image_service.get_permitted_image(sport_name, art.category)
                if new_img and new_img.get("image_url") and new_img["image_url"] != url:
                    art.primary_image_url = new_img["image_url"]
                    art.image_caption = new_img.get("caption")
                    art.image_attribution = new_img.get("attribution")
                    art.image_license = new_img.get("license")
                    fixed_count += 1
                    print(f"    [+] Updated URL: {new_img['image_url']}")
                    print(f"    [+] Attribution: {new_img.get('attribution')}")
                else:
                    print(f"    [-] Kept fallback: {new_img.get('image_url')}")

        db.commit()
        cache_service.invalidate()
        print(f"\n[+] Successfully updated {fixed_count} articles with authentic, distinct sports photos!")
    finally:
        db.close()
    print("=" * 65)


if __name__ == "__main__":
    asyncio.run(fix_images())
