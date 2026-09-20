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
        )
    """)

  # 既存データをクリア
  cursor.execute("DELETE FROM libretro_tbl")

  # 先頭の clrmamepro (...) ヘッダーブロックを削除
  text_cleaned = re.sub(
      r"clrmamepro\s*\(.*?\)", "", text, flags=re.DOTALL | re.IGNORECASE
  )

  # 各 game ブロックを抽出
  game_blocks = re.findall(
      r"\bgame\s*\((.*?)\)\s*(?=\n\s*(?:game|\Z))", text_cleaned, re.DOTALL
  )
  if not game_blocks:
    game_blocks = re.findall(r"\bgame\s*\((.*?)\)", text_cleaned, re.DOTALL)

  inserted_count = 0

  for block in game_blocks:
    # 汎用抽出パターン: ダブル/シングルクォートで囲まれているか、スペースなしの文字列を取得
    val_pattern = r'\b{0}\s+(?:"([^"]*)"|\'([^\']*)\'|([^\s]+))'

    # 1. name の取得
    game_name = extract_value(val_pattern.format("name"), block)

    # 2. description の取得
    description = extract_value(val_pattern.format("description"), block)

    # 3. rom ブロックの解析
    m_rom = re.search(r"rom\s*\((.*?)\)", block, re.DOTALL)
    file_name, size, crc, md5, sha1 = "", None, "", "", ""

    if m_rom:
      rom_block = m_rom.group(1)

      # file-name (romタグ内のname - クォートの種類に関わらず全文取得)
      file_name = extract_value(val_pattern.format("name"), rom_block)

      # size
      m_size = re.search(r"\bsize\s+(\d+)", rom_block)
      if m_size:
        size = int(m_size.group(1))

      # crc
      m_crc = re.search(r"\bcrc\s+([0-9a-fA-F]+)", rom_block)
      crc = m_crc.group(1) if m_crc else ""

      # md5
      m_md5 = re.search(r"\bmd5\s+([0-9a-fA-F]+)", rom_block)
      md5 = m_md5.group(1) if m_md5 else ""

      # sha1
      m_sha1 = re.search(r"\bsha1\s+([0-9a-fA-F]+)", rom_block)
      sha1 = m_sha1.group(1) if m_sha1 else ""

    # データベースへインサート
    params = (game_name, description, file_name, size, crc, md5, sha1)
    cursor.execute(
        """
        INSERT INTO libretro_tbl (name, description, "file-name", size, crc, md5, sha1)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """,
        params,
    )
    inserted_count += 1

  conn.commit()
  conn.close()
  print(
      f"インサート完了: libretro_tbl に {inserted_count} 件のデータを登録しました。"
  )


if __name__ == "__main__":
  dat_file = "db/nes_libretro.dat"
  database_file = "db/nes_games.db"

  import_libretro_dat(dat_file, database_file)
