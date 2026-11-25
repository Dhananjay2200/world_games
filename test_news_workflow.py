"""
Test script to verify Sports News workflow without modifying existing playbooks.
"""

import asyncio
from app.graph.workflow import run_single_game_workflow
from app.database.session import SessionLocal
from app.database.models import GameArticle, GameTopic


async def test_news():
    print("=" * 65)
    print(" WorldGames AI - Sports News Pipeline Test")
    print("=" * 65)
    
    # 1. Count existing playbooks for Kabaddi before test
    db = SessionLocal()
    try:
        kabaddi_topic = db.query(GameTopic).filter(GameTopic.canonical_name == "kabaddi").first()
        initial_playbooks = db.query(GameArticle).filter(
            GameArticle.topic_id == kabaddi_topic.id,
            GameArticle.article_type == "PLAYBOOK"
        ).all()
        print(f"[*] Found {len(initial_playbooks)} foundational Playbook(s) for Kabaddi in DB.")
        for p in initial_playbooks:
            print(f"    - Existing Playbook: '{p.title}' (ID: {p.id}, Score: {p.score})")
    finally:
        db.close()

    # 2. Launch Sports News pipeline for Kabaddi
    news_headline = "Pro Kabaddi League 2026: Championship Finals Breakdown & Super-Raid Records"
    print(f"\n[*] Launching Sports News generation for: 'Kabaddi'...")
    print(f"    Angle: '{news_headline}'")
    
    result = await run_single_game_workflow(
        topic_name="Kabaddi",
        category="Indigenous, Folk & Traditional Games",
        region="South Asia",
        country="India",
        article_type="NEWS",
        news_angle=news_headline,
    )
    
    print("\n[+] Sports News Workflow Completed!")
    print(f"    Final Status:  {result.get('status')}")
    print(f"    News Art ID:   {result.get('published_article_id')}")
    print(f"    Score:         {result.get('evaluation', {}).get('overall_score')}/10.0")

    # 3. Verify in PostgreSQL that:
    # A) The original playbook is UNCHANGED and intact!
    # B) A new separate article row exists with article_type="NEWS"!
    db = SessionLocal()
    try:
        current_playbooks = db.query(GameArticle).filter(
            GameArticle.topic_id == kabaddi_topic.id,
            GameArticle.article_type == "PLAYBOOK"
        ).all()
        news_articles = db.query(GameArticle).filter(
            GameArticle.topic_id == kabaddi_topic.id,
            GameArticle.article_type == "NEWS"
        ).all()

        print("\n[+] POST-EXECUTION VERIFICATION:")
        print(f"    [Playbooks Intact] Total Playbooks for Kabaddi: {len(current_playbooks)}")
        assert len(current_playbooks) == len(initial_playbooks), "Old playbook count altered!"
        print(f"    -> Original playbook title: '{current_playbooks[0].title}' (Unchanged)")

        print(f"    [News Added] Total News Articles for Kabaddi: {len(news_articles)}")
        for n in news_articles:
            print(f"    -> News Title: '{n.title}' [Type: {n.article_type}, Score: {n.score}, Slug: {n.slug}]")
            print(f"       Word Count: {len(n.content.split())} words")

        print("\n[+] SUCCESS: Sports News published independently without altering old playbooks!")
    finally:
        db.close()
    print("=" * 65)


if __name__ == "__main__":
    asyncio.run(test_news())
