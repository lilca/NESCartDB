import re
import sqlite3


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
    # 1. name の取得（ダブルクォート優先、なければ非スペース）
    m_name = re.search(r'\bname\s+"([^"]+)"', block)
    if not m_name:
      m_name = re.search(r"\bname\s+([^\s]+)", block)
    game_name = m_name.group(1) if m_name else ""

    # 2. description の取得（ダブルクォート優先、なければ非スペース）
    m_desc = re.search(r'\bdescription\s+"([^"]+)"', block)
    if not m_desc:
      m_desc = re.search(r"\bdescription\s+([^\s]+)", block)
    description = m_desc.group(1) if m_desc else ""

    # 3. rom ブロックの解析
    m_rom = re.search(r"rom\s*\((.*?)\)", block, re.DOTALL)
    file_name, size, crc, md5, sha1 = "", None, "", "", ""

    if m_rom:
      rom_block = m_rom.group(1)

      # file-name (romタグ内のname - ダブルクォートを最優先で全文取得)
      m_rname = re.search(r'\bname\s+"([^"]+)"', rom_block)
      if not m_rname:
        m_rname = re.search(r"\bname\s+([^\s]+)", rom_block)
      file_name = m_rname.group(1) if m_rname else ""

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
    cursor.execute(
        """
        INSERT INTO libretro_tbl (name, description, "file-name", size, crc, md5, sha1)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """,
        (game_name, description, file_name, size, crc, md5, sha1),
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

  import_libretro_dat(dat_file, database_file)      r"clrmamepro\s*\(.*?\)", "", text, flags=re.DOTALL | re.IGNORECASE
  )

  # 各 game ブロックを抽出
  game_blocks = re.findall(
      r"\bgame\s*\((.*?)\)\s*(?=\n\s*(?:game|\Z))", text_cleaned, re.DOTALL
  )
  if not game_blocks:
    game_blocks = re.findall(r"\bgame\s*\((.*?)\)", text_cleaned, re.DOTALL)

  inserted_count = 0

  for block in game_blocks:
    # 1. name の取得
    m_name = re.search(r'\bname\s+(?:"(.*?)"|([^\s]+))', block)
    game_name = (m_name.group(1) or m_name.group(2)) if m_name else ""

    # 2. description の取得
    m_desc = re.search(r'\bdescription\s+(?:"(.*?)"|([^\s]+))', block)
    description = (m_desc.group(1) or m_desc.group(2)) if m_desc else ""

    # 3. rom ブロックの解析
    m_rom = re.search(r"rom\s*\((.*?)\)", block, re.DOTALL)
    file_name, size, crc, md5, sha1 = "", None, "", "", ""

    if m_rom:
      rom_block = m_rom.group(1)

      # file-name (romタグ内のname)
      m_rname = re.search(r'\bname\s+(?:"(.*?)"|([^\s]+))', rom_block)
      file_name = (m_rname.group(1) or m_rname.group(2)) if m_rname else ""

      # size
      m_size = re.search(r'\bsize\s+(\d+)', rom_block)
      if m_size:
        size = int(m_size.group(1))

      # crc
      m_crc = re.search(r'\bcrc\s+([0-9a-fA-F]+)', rom_block)
      crc = m_crc.group(1) if m_crc else ""

      # md5
      m_md5 = re.search(r'\bmd5\s+([0-9a-fA-F]+)', rom_block)
      md5 = m_md5.group(1) if m_md5 else ""

      # sha1
      m_sha1 = re.search(r'\bsha1\s+([0-9a-fA-F]+)', rom_block)
      sha1 = m_sha1.group(1) if m_sha1 else ""

    # データベースへインサート
    cursor.execute(
        """
        INSERT INTO libretro_tbl (name, description, "file-name", size, crc, md5, sha1)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """,
        (game_name, description, file_name, size, crc, md5, sha1),
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
