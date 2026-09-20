import os
import sqlite3

# dbディレクトリのパスを設定
db_dir = "db"
os.makedirs(db_dir, exist_ok=True)
db_path = os.path.join(db_dir, "nes_games.db")

# データベースに接続（ファイルが存在しない場合は新規作成されます）
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

conn.commit()
conn.close()

print(f"SQLiteデータベースを準備しました: {db_path}")
