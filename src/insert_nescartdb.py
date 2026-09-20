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

# --- テスト用のXML（あえて未知の項目 'unknown_attr' と '<unknown_tag>' を混ぜています） ---
sample_xml = """<?xml version="1.0" encoding="UTF-8"?>
<database version="1.0" conformance="loose">
    <game>
        <cartridge system="NES-PAL" dump="ok" crc="001388B3" sha1="4BCD36C05FCAF45C74001257C65AFB7EC5FA53D7" unknown_attr="invalid_value">
            <board type="NES-TLROM" mapper="4">
                <prg size="256k" />
                <chr size="128k" />
                <chip type="MMC3C" />
                <unknown_tag>extra_data</unknown_tag>
            </board>
        </cartridge>
    </game>
</database>
"""

print("--- パースおよびスキーマ検証を開始 ---")
extracted_data = parse_and_validate_xml(sample_xml)
