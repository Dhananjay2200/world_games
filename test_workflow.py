"""
Test script for End-to-End LangGraph Pipeline Execution.
Supports testing custom topics, automatic novel discovery, and duplicate reporting.
"""

import sys
import asyncio
from app.graph.workflow import run_single_game_workflow
from app.database.session import SessionLocal
from app.database.models import GameArticle, GameTopic, QualityEvaluation
from app.services.discovery_service import generate_canonical_key


async def test_workflow():
    print("=" * 65)
    print(" WorldGames AI - LangGraph End-to-End Pipeline Diagnostic")
    print("=" * 65)

    # 1. Check custom topic argument or determine a fresh topic
    custom_topic = sys.argv[1] if len(sys.argv) > 1 else None
    
    db = SessionLocal()
    try:
        existing_names = {t.canonical_name for t in db.query(GameTopic.canonical_name).all()}
    finally:
        db.close()

    topic_to_test = custom_topic
    if not topic_to_test:
        # If 'Kabaddi' is already generated, select another fresh seed topic
        starter_candidates = [
            ("Kabaddi", "Indigenous, Folk & Traditional Games", "South Asia", "India"),
            ("Hurling", "Field & Team Ball Sports", "Europe", "Ireland"),
            ("Capoeira", "Combat Sports & Martial Arts", "Latin America & Caribbean", "Brazil"),
            ("Buzkashi", "Indigenous, Folk & Traditional Games", "Central & West Asia", "Afghanistan"),
            ("Curling", "Winter & Ice Sports", "Europe", "Scotland"),
            ("Go (Weiqi / Baduk)", "Board, Tile & Strategy Games", "East Asia", "China / Japan / Korea"),
        ]

        selected_candidate = None
        for name, cat, reg, country in starter_candidates:
            if generate_canonical_key(name) not in existing_names:
                selected_candidate = (name, cat, reg, country)
                break

        if selected_candidate:
            name, cat, reg, country = selected_candidate
            print(f"[*] Testing fresh unexplored game: '{name}' ({cat} - {reg})...")
            result = await run_single_game_workflow(
                topic_name=name,
                category=cat,
                region=reg,
                country=country,
            )
        else:
            print("[*] All starter candidates generated. Running full autonomous AI discovery...")
            result = await run_single_game_workflow()
    else:
        print(f"[*] Testing requested topic: '{topic_to_test}'...")
        result = await run_single_game_workflow(topic_name=topic_to_test)

    print("\n[+] Workflow Execution Completed!")
    topic_name = result.get("topic", {}).get("name", "Unknown")
    final_status = result.get("status")
    print(f"    Topic:         {topic_name}")
    print(f"    Final Status:  {final_status}")

    # If duplicate was rejected, explain why and display the existing record from DB
    if final_status == "DUPLICATE_REJECTED":
        print("\n[!] WHY SCORE IS NONE IN THIS RUN:")
        print("    -> The Deduplication Gate (Node 2) prevented duplicate article generation.")
        print(f"    -> '{topic_name}' has ALREADY been researched, evaluated, and published in a previous run.")
        print("    -> The pipeline exited early to avoid generating duplicate content or wasting API tokens.")
        
        # Look up existing article in DB
        db = SessionLocal()
        try:
            canonical = generate_canonical_key(topic_name)
            topic_record = db.query(GameTopic).filter(GameTopic.canonical_name == canonical).first()
            if topic_record and topic_record.article:
                art = topic_record.article
                print(f"\n[+] EXISTING RECORD FOUND IN POSTGRESQL:")
                print(f"    Title:         {art.title}")
                print(f"    Quality Score: {art.score}/10.0")
                print(f"    Status:        {art.status}")
                print(f"    Words:         {len(art.content.split())} words")
                print(f"    Slug:          {art.slug}")
        finally:
            db.close()
    else:
        print(f"    Article ID:    {result.get('published_article_id')}")
        eval_info = result.get("evaluation", {})
        print(f"    Quality Score: {eval_info.get('overall_score')}/10.0 (Passed: {eval_info.get('passed')})")

        # Verify in DB
        db = SessionLocal()
        try:
            art_id = result.get("published_article_id")
            if art_id:
                art = db.query(GameArticle).filter(GameArticle.id == art_id).first()
                if art:
                    print(f"\n[+] Verified in PostgreSQL: '{art.title}' (Slug: {art.slug})")
                    print(f"[+] Total Word Count: {len(art.content.split())} words")
                    print(f"[+] Primary Image: {art.primary_image_url}")
                    print(f"[+] Publication Status: {art.status}")
        finally:
            db.close()

    print("=" * 65)


if __name__ == "__main__":
    asyncio.run(test_workflow())
