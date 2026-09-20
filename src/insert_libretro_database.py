import re
import sqlite3


def extract_value(pattern, text):
  """ダブルクォート、シングルクォート、または非スペースの値を安全に抽出するヘルパー"""
  m = re.search(pattern, text)
  if m:
    return m.group(1) or m.group(2) or m.group(3) or ""
  return ""


def import_libretro_dat(dat_path, db_path):
  # DATファイルの読み込み
  try:
    with open(dat_path, "r", encoding="utf-8", errors="ignore") as f:
      text = f.read()
  except Exception as e:
    print(f"DATファイルの読み込みに失敗しました: {e}")
    return

  # SQLiteデータベースに接続
  conn = sqlite3.connect(db_path)
  cursor = conn.cursor()

  # libretro_tbl テーブルの作成
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS libretro_tbl (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            description TEXT,
            "file-name" TEXT,
            size INTEGER,
            crc TEXT,
            md5 TEXT,
            sha1 TEXT
