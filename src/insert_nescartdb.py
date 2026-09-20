import sqlite3
import xml.etree.ElementTree as ET

# 1. SQLiteデータベースからテーブルのスキーマ（カラム名）を動的に取得する
def get_allowed_attributes_from_db(db_path, table_name):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    # テーブルのカラム情報を取得
    cursor.execute(f"PRAGMA table_info({table_name});")
    # row[1] にカラム名が入っている
    columns = [row[1] for row in cursor.fetchall()]
    conn.close()
    
    # 'id'（自動採番）などはXML側には存在しないため除外またはそのままでもOK
    if "id" in columns:
        columns.remove("id")
        
    return set(columns)

# XMLの構造上のタグの許可リスト
ALLOWED_TAGS = {
    "database", "game", "cartridge", "board", "prg", "chr", "chip"
}

def parse_and_validate_xml_file(file_path, allowed_attributes):
    tree = ET.parse(file_path)
    root = tree.getroot()
    
    record = {}
    
    # 要素を再帰的に走査してチェック
    for elem in root.iter():
        # タグ名のチェック
        if elem.tag not in ALLOWED_TAGS:
            print(f"【警告】スキーマ（タグ）にない要素が見つかりました: <{elem.tag}>")
        
        # 属性名のチェック（DBのスキーマと照合）
        for attr_name, attr_value in elem.attrib.items():
            if attr_name not in allowed_attributes:
                print(f"【警告】DBスキーマに存在しない属性が見つかりました: '{attr_name}' (値: {attr_value})")
            else:
                record[attr_name] = attr_value

    return record

def create_tbl(db_path, table_name):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 1. 毎回きれいな状態で作り直す場合（DROPしてからCREATE）
    cursor.execute(f"DROP TABLE IF EXISTS {table_name};")
    cursor.execute("""
        CREATE TABLE {table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            rom_name TEXT
        );
    """)

    # 2. XMLやDATからデータを読み込んでインサートする処理
    # （例：パースしたデータをループで回して INSERT するなど）
    # for row in parsed_data:
    #     cursor.execute("INSERT INTO games (title, rom_name) VALUES (?, ?)", (row['title'], row['rom']))

    conn.commit()
    conn.close()

print("データベースのテーブル作成とデータのインサートが完了しました。")
# --- 実行部分 ---
db_path = "nes_games.db"        # SQLiteのデータベースファイルパス
table_name = "nes_cart_tbl"         # 対象のテーブル名
xml_file = "db/NstDatabase.xml"     # ご指定のXMLファイルパス

print("--- テーブル作成開始 ---")
create_tbl(db_path, table_name)

print("--- スキーマ（DB）とXMLの検証を開始 ---")
try:
    # データベースからスキーマを自動読み込み
    allowed_attributes = get_allowed_attributes_from_db(db_path, table_name)
    print(f"DBから読み込んだ有効なカラム（スキーマ）: {allowed_attributes}\n")
    
    # パースと検証の実行
    extracted_data = parse_and_validate_xml_file(xml_file, allowed_attributes)
    print("\n検証・抽出完了")
    
except sqlite3.OperationalError as e:
    print(f"データベースエラー: テーブルまたはDBファイルが見つかりません ({e})")
except FileNotFoundError:
    print(f"エラー: XMLファイル '{xml_file}' が見つかりません。")
except ET.ParseError:
    print("エラー: XMLの構文解析に失敗しました。")
