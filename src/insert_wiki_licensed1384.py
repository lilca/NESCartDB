import sqlite3
import xml.etree.ElementTree as ET


def import_famicom_wiki_xml(xml_path, db_path):
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

  # famicom_wiki テーブルの作成（すべて英語・ASCIIのカラム名）
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS famicom_wiki (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            release_jp TEXT,
            release_na TEXT,
            release_eu TEXT,
            maker TEXT,
            remarks TEXT,
            footnote TEXT
        )
    """)

  # 既存データをクリア（必要に応じてコメントアウトしてください）
  cursor.execute("DELETE FROM famicom_wiki")

  insert_count = 0

  for game in root.findall("game"):
    # タイトルを取得
    title = game.findtext("タイトル_タイトル", "").strip()

    # タイトルが空の行（目次や集計データなど）はスキップ
    if not title:
      continue

    release_jp = game.findtext("発売日_日本", "").strip()
    release_na = game.findtext("発売日_北米", "").strip()
    release_eu = game.findtext("発売日_欧州", "").strip()
    maker = game.findtext("発売元_発売元", "").strip()
    remarks = game.findtext("備考_備考", "").strip()
    footnote = game.findtext("脚注_脚注", "").strip()

    # データベースへインサート
    cursor.execute(
        """
        INSERT INTO famicom_wiki (title, release_jp, release_na, release_eu, maker, remarks, footnote)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """,
        (title, release_jp, release_na, release_eu, maker, remarks, footnote),
    )
    insert_count += 1

  # 変更を保存して接続を閉じる
  conn.commit()
  conn.close()

  print(
      f"インサート完了: famicom_wiki に {insert_count} 件のデータを登録しました。"
  )


if __name__ == "__main__":
  xml_file = "db/famicom_games.xml"
  database_file = "db/nes_games.db"

  import_famicom_wiki_xml(xml_file, database_file)
