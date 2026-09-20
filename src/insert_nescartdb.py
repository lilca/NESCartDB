import sqlite3
import xml.etree.ElementTree as ET

def get_allowed_attributes_from_db(db_path, table_name):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name});")
    columns = [row[1] for row in cursor.fetchall()]
    conn.close()
    
    if "id" in columns:
        columns.remove("id")
        
    return set(columns)

def parse_and_insert_xml(file_path, db_path, table_name, allowed_attributes):
    tree = ET.parse(file_path)
    root = tree.getroot()
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    count = 0
    
    for game_elem in root.iter():
        if game_elem.tag.split("}")[-1] == "game":
            cart_elem = None
            for child in game_elem:
                if child.tag.split("}")[-1] == "cartridge":
                    cart_elem = child
                    break
            
            if cart_elem is not None:
                # カートリッジの属性（system, dump, crc, sha1）
                cart_attrs = {k.split("}")[-1]: v for k, v in cart_elem.attrib.items()}
                system = cart_attrs.get("system", "")
                dump = cart_attrs.get("dump", "")
                crc = cart_attrs.get("crc", "")
                sha1 = cart_attrs.get("sha1", "")
                
                board_type = ""
                mapper = ""
                prg_size = ""
                chr_size = ""
                chip_type = ""
                
                # ボード要素と子要素を走査
                for board_elem in cart_elem:
                    if board_elem.tag.split("}")[-1] == "board":
                        board_attrs = {k.split("}")[-1]: v for k, v in board_elem.attrib.items()}
                        # boardの type 属性を board_type として取得
                        board_type = board_attrs.get("type", "")
                        mapper = board_attrs.get("mapper", "")
                        
                        for sub in board_elem:
                            sub_tag = sub.tag.split("}")[-1]
                            sub_attrs = {k.split("}")[-1]: v for k, v in sub.attrib.items()}
                            
                            if sub_tag == "prg":
                                prg_size = sub_attrs.get("size", "")
                            elif sub_tag == "chr":
                                chr_size = sub_attrs.get("size", "")
                            elif sub_tag == "chip":
                                chip_type = sub_attrs.get("type", "")

                # データベースに INSERT
                cursor.execute(
                    f"""
                    INSERT INTO {table_name} 
                    (system, dump, board_type, mapper, prg_size, chr_size, chip_type, crc, sha1) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (system, dump, board_type, mapper, prg_size, chr_size, chip_type, crc, sha1)
                )
                count += 1

    conn.commit()
    conn.close()
    print(f"✅ {count} 件のデータをテーブル '{table_name}' にインサートしました！")

def create_tbl(db_path, table_name):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(f"DROP TABLE IF EXISTS {table_name};")
    # dump と board_type を含めたテーブル構造
    cursor.execute(f"""
        CREATE TABLE {table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            system TEXT,
            dump TEXT,
            board_type TEXT,
            mapper TEXT,
            prg_size TEXT,
            chr_size TEXT,
            chip_type TEXT,
            crc TEXT,
            sha1 TEXT
        );
    """)

    conn.commit()
    conn.close()
    print(f"データベースのテーブル '{table_name}' の作成が完了しました。")

# --- 実行部分 ---
db_path = "db/nes_games.db"       
table_name = "nes_cart_tbl"       
xml_file = "db/NstDatabase.xml"   

print("--- テーブル作成開始 ---")
create_tbl(db_path, table_name)

print("\n--- スキーマ確認とインサート開始 ---")
try:
    allowed_attributes = get_allowed_attributes_from_db(db_path, table_name)
    print(f"DBから読み込んだ有効なカラム: {allowed_attributes}\n")
    
    parse_and_insert_xml(xml_file, db_path, table_name, allowed_attributes)
    print("\nすべての処理が正常に完了しました。")
    
except sqlite3.OperationalError as e:
    print(f"データベースエラー: テーブルまたはDBファイルが見つかりません ({e})")
except FileNotFoundError:
    print(f"エラー: XMLファイル '{xml_file}' が見つかりません。")
except ET.ParseError:
    print("エラー: XMLの構文解析に失敗しました。")
