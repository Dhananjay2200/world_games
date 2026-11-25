import psycopg2

def migrate():
    conn = psycopg2.connect("postgresql://postgres:Dk#22000@localhost:5432/world_games_ai")
    conn.autocommit = True
    cur = conn.cursor()
    # Drop 1-to-1 unique constraint so topics can have news articles
    cur.execute("ALTER TABLE game_articles DROP CONSTRAINT IF EXISTS game_articles_topic_id_key;")
    # Add article_type column (PLAYBOOK or NEWS)
    cur.execute("ALTER TABLE game_articles ADD COLUMN IF NOT EXISTS article_type VARCHAR(50) DEFAULT 'PLAYBOOK';")
    cur.execute("CREATE INDEX IF NOT EXISTS ix_game_articles_article_type ON game_articles (article_type);")
    print("[+] Migration completed: article_type column and non-unique topic relation enabled.")
    conn.close()

if __name__ == "__main__":
    migrate()
