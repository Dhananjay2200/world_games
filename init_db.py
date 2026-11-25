import psycopg2

def init_postgres():
    conn = psycopg2.connect("postgresql://postgres:Dk#22000@localhost:5432/postgres")
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM pg_database WHERE datname = 'world_games_ai'")
    exists = cur.fetchone()
    if not exists:
        cur.execute("CREATE DATABASE world_games_ai")
        print("[+] Created database 'world_games_ai' successfully.")
    else:
        print("[*] Database 'world_games_ai' already exists.")
    conn.close()

if __name__ == "__main__":
    init_postgres()
