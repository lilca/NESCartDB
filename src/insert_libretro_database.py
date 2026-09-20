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
  cursor.execute(
      "CREATE TABLE IF NOT EXISTS libretro_tbl (id INTEGER PRIMARY KEY"
      ' AUTOINCREMENT, name TEXT, description TEXT, "file-name" TEXT, size'
      " INTEGER, crc TEXT, md5 TEXT, sha1 TEXT);"
  )

  # 既存データをクリア
  cursor.execute("DELETE FROM libretro_tbl")
  # AUTOINCREMENTのカウンターをリセットする
  cursor.execute("DELETE FROM sqlite_sequence WHERE name='libretro_tbl'")
  
  # 先頭の clrmamepro (...) ヘッダーブロックを削除
  text_cleaned = re.sub(
      r"clrmamepro\s*\(.*?\)", "", text, flags=re.DOTALL | re.IGNORECASE
  )

  # ---- ここがポイント ----
  # game ( ... ) ブロックの切り出しは「行頭の 'game (' の出現位置」で行う。
  # 括弧の数え上げ（(.*?)\)）に頼らないので、ファイル名中の
  # "(Japan)" "(Rev 1)" "(Unl)" のような括弧があっても壊れない。
  starts = [m.start() for m in re.finditer(r"^game\s*\(", text_cleaned, re.MULTILINE)]
  game_blocks = []
  for i, start in enumerate(starts):
    end = starts[i + 1] if i + 1 < len(starts) else len(text_cleaned)
    game_blocks.append(text_cleaned[start:end])

  # rom (...) の中身を丸ごと1つの正規表現でキャプチャする。
  # name → size → crc → md5 → sha1 という固定の並びを直接パターン化しているので、
  # name 内に "(" ")" が含まれていても size 以降まで正しく読める。
  rom_pattern = re.compile(
      r'rom\s*\(\s*name\s+"(?P<fname>[^"]*)"'
      r"\s+size\s+(?P<size>\d+)"
      r"\s+crc\s+(?P<crc>[0-9a-fA-F]+)"
      r"\s+md5\s+(?P<md5>[0-9a-fA-F]+)"
      r"\s+sha1\s+(?P<sha1>[0-9a-fA-F]+)"
      r"\s*\)",
      re.DOTALL,
  )

  inserted_count = 0

  for block in game_blocks:
    # 1. game の name 取得（rom行より前に出てくる最初の name）
    m_name = re.search(r'\bname\s+"([^"]+)"', block)
    game_name = m_name.group(1) if m_name else ""

    # 2. description 取得
    m_desc = re.search(r'\bdescription\s+"([^"]+)"', block)
    description = m_desc.group(1) if m_desc else ""

    # 3. rom ブロックの解析（括弧数えではなくフィールド構造で直接抽出）
    file_name, size, crc, md5, sha1 = "", None, "", "", ""
    m_rom = rom_pattern.search(block)
    if m_rom:
      file_name = m_rom.group("fname")
      size = int(m_rom.group("size"))
      crc = m_rom.group("crc")
      md5 = m_rom.group("md5")
      sha1 = m_rom.group("sha1")

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
