import os
import sqlite3

# dbディレクトリのパスを設定
db_dir = "db"
os.makedirs(db_dir, exist_ok=True)
db_path = os.path.join(db_dir, "nes_games.db")

# データベースに接続（ファイルが存在しない場合は新規作成されます）
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# テーブル作成のサンプル（ゲーム情報を格納する場合の例）
cursor.execute("""
    CREATE TABLE IF NOT EXISTS games (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        release_date TEXT,
        developer TEXT,
        source TEXT
    )
""")

conn.commit()
conn.close()

print(f"SQLiteデータベースを準備しました: {db_path}")
