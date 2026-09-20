import sqlite3
import xml.etree.ElementTree as ET


def import_pasofami_xml(xml_path, db_path):
  # XMLファイルの読み込み
  try:
    tree = ET.parse(xml_path)
    root = tree.getroot()
  except Exception as e:
    print(f"XMLファイルの読み込みに失敗しました: {e}")
    return

  # SQLiteデータベースに接続
  conn = sqlite3.connect(db_path)
  cursor = conn.cursor()

  # pasofami_tbl テーブルの作成（存在しない場合）
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS pasofami_tbl (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            country TEXT,
            maker TEXT,
            release_date TEXT,
            price INTEGER,
            genre TEXT,
            mapper INTEGER,
            mirroring TEXT,
            prg_size TEXT,
            chr_size TEXT
        )
    """)

  # 既存のデータを重複させないためにクリアする場合（必要に応じてコメントアウトしてください）
  cursor.execute("DELETE FROM pasofami_tbl")

  is_header_passed = False
  insert_count = 0

  for game in root.findall("game"):
    col_1 = game.findtext("col_1", "").strip()

    # ヘッダー行（「タイトル名」という文字が入っている行）に到達するまでスキップ
    if not is_header_passed:
      if col_1 == "タイトル名":
        is_header_passed = True
      continue  # ヘッダー行自体もデータではないのでスキップ

    # 各フィールドのデータを取得
    title = col_1
    # タイトルが空の行はゴミデータとしてスキップ
    if not title:
      continue

    country = game.findtext("col_2", "").strip()
    maker = game.findtext("col_3", "").strip()
    release_date = game.findtext("col_4", "").strip()
    price_str = game.findtext("col_5", "").strip()
    genre = game.findtext("col_6", "").strip()
    mapper_str = game.findtext("col_7", "").strip()
    mirroring = game.findtext("col_8", "").strip()  # XML上の「フラグ」に対応
    prg_size = game.findtext("col_9", "").strip()
    chr_size = game.findtext("col_10", "").strip()

    # 価格やマッパー番号が数値に変換できる場合は数値化（空ならNULL）
    price = int(price_str) if price_str.isdigit() else None
    mapper = int(mapper_str) if mapper_str.isdigit() else None

    # データベースへインサート
    cursor.execute(
        """
        INSERT INTO pasofami_tbl (title, country, maker, release_date, price, genre, mapper, mirroring, prg_size, chr_size)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
        (
            title,
            country,
            maker,
            release_date,
            price,
            genre,
            mapper,
            mirroring,
            prg_size,
            chr_size,
        ),
    )
    insert_count += 1

  # 変更を保存して接続を閉じる
  conn.commit()
  conn.close()

  print(
      f"インサート完了: pasofami_tbl に {insert_count} 件のデータを登録しました"
      f"。"
  )


if __name__ == "__main__":
  # ファイル名やパスは適宜変更してください
  xml_file = "db/pasofami_nes_games.xml"
  database_file = "db/nes_games.db"

  import_pasofami_xml(xml_file, database_file)
