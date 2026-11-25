"""
Database and Model Verification Script for WorldGames AI.
"""

from app.database.session import engine, init_models, SessionLocal
from app.database.models import GameTopic, GameArticle, AutomationState
from app.config import get_settings


def verify_database():
    settings = get_settings()
    print("=" * 65)
    print(" WorldGames AI - Database & Schema Diagnostic")
    print("=" * 65)
    print(f"[*] Connecting to: {settings.DATABASE_URL.split('@')[-1]}")
    
    init_models()
    
    db = SessionLocal()
    try:
        topic_count = db.query(GameTopic).count()
        article_count = db.query(GameArticle).count()
        
        # Ensure default automation state exists
        auto_state = db.query(AutomationState).first()
        if not auto_state:
            auto_state = AutomationState(
                is_running=False,
                daily_count=0,
                daily_limit=settings.DAILY_ARTICLE_LIMIT,
                interval_seconds=300
            )
            db.add(auto_state)
            db.commit()
            print("[+] Created initial AutomationState record.")
        else:
            print(f"[*] Existing AutomationState: is_running={auto_state.is_running}, daily={auto_state.daily_count}/{auto_state.daily_limit}")
            
        print(f"[+] Total Game Topics in DB: {topic_count}")
        print(f"[+] Total Game Articles in DB: {article_count}")
        print("[+] Database tables and schema verified successfully!")
        print("=" * 65)
    finally:
        db.close()


if __name__ == "__main__":
    verify_database()
