import sqlite3
import xml.etree.ElementTree as ET

# 1. SQLiteデータベースからテーブルのスキーマ（カラム名）を動的に取得する
def get_allowed_attributes_from_db(db_path, table_name):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name});")
    columns = [row[1] for row in cursor.fetchall()]
    conn.close()
    
    if "id" in columns:
        columns.remove("id")
        
    return set(columns)

ALLOWED_TAGS = {
    "database", "game", "cartridge", "board", "prg", "chr", "chip"
}

# 💡 検証しつつ、データベースにインサートする関数
def parse_and_insert_xml(file_path, db_path, table_name, allowed_attributes):
    tree = ET.parse(file_path)
    root = tree.getroot()
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    count = 0
    
    # 例として <game> タグをループしてデータを抽出・インサートする場合
    # （※XMLの実際の属性名 'name' や構造に合わせて適宜変更してください）
    for game_elem in root.findall(".//game"):
        title = game_elem.attrib.get("name", "")  # 例: 属性からタイトルを取得
        rom_name = game_elem.attrib.get("file", title) # 例: なければ代替え
        
        # 属性のバリデーションチェック（これまでのチェックロジックを統合）
        for attr_name, attr_value in game_elem.attrib.items():
            if attr_name not in allowed_attributes:
                print(f"【警告】DBスキーマにない属性: '{attr_name}'")

        # 💡 データベースにINSERT実行
        cursor.execute(
            f"INSERT INTO {table_name} (title, rom_name) VALUES (?, ?)",
            (title, rom_name)
        )
        count += 1

    conn.commit()
    conn.close()
    print(f"✅ {count} 件のデータをテーブル '{table_name}' にインサートしました！")

def create_tbl(db_path, table_name):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(f"DROP TABLE IF EXISTS {table_name};")
    cursor.execute(f"""
        CREATE TABLE {table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            rom_name TEXT
        );
    """)

    conn.commit()
    conn.close()
    print(f"データベースのテーブル '{table_name}' の作成が完了しました。")

# --- 実行部分 ---
db_path = "db/nes_games.db"        # SQLiteのデータベースファイルパス
table_name = "nes_cart_tbl"     # 対象のテーブル名
xml_file = "db/NstDatabase.xml" # ご指定のXMLファイルパス

print("--- テーブル作成開始 ---")
create_tbl(db_path, table_name)

print("\n--- スキーマ（DB）確認とインサート開始 ---")
try:
    # データベースからスキーマを自動読み込み
    allowed_attributes = get_allowed_attributes_from_db(db_path, table_name)
    print(f"DBから読み込んだ有効なカラム: {allowed_attributes}\n")
    
    # パースとインサートの実行
    parse_and_insert_xml(xml_file, db_path, table_name, allowed_attributes)
    print("\nすべての処理が正常に完了しました。")
    
except sqlite3.OperationalError as e:
    print(f"データベースエラー: テーブルまたはDBファイルが見つかりません ({e})")
except FileNotFoundError:
    print(f"エラー: XMLファイル '{xml_file}' が見つかりません。")
except ET.ParseError:
    print("エラー: XMLの構文解析に失敗しました。")
