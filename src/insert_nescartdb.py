import xml.etree.ElementTree as ET

# 1. データベースのスキーマ（または許可するXMLの属性・タグ名）の定義
ALLOWED_ATTRIBUTES = {
    "system", "dump", "crc", "sha1", 
    "type", "mapper", "size"
}

ALLOWED_TAGS = {
    "database", "game", "cartridge", "board", "prg", "chr", "chip"
}

def parse_and_validate_xml(xml_string):
    root = ET.fromstring(xml_string)
    
    # データを格納する辞書（SQLiteインサート用）
    record = {}
    
    # 要素を再帰的に走査してチェック
    for elem in root.iter():
        # タグ名のチェック
        if elem.tag not in ALLOWED_TAGS:
            print(f"【警告】スキーマ（許可リスト）にないタグが見つかりました: <{elem.tag}>")
        
        # 属性名のチェック
        for attr_name, attr_value in elem.attrib.items():
            if attr_name not in ALLOWED_ATTRIBUTES:
                print(f"【警告】スキーマ（許可リスト）にない属性が見つかりました: '{attr_name}' (値: {attr_value})")
            else:
                record[attr_name] = attr_value

    return record

xml_file = ""

print("--- パースおよびスキーマ検証を開始 ---")
extracted_data = parse_and_validate_xml(xml_file)
