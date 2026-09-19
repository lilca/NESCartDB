import io
import re
import pandas as pd
import requests

url = "https://ja.wikipedia.org/wiki/ファミリーコンピュータのゲームタイトル一覧"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

print("WikipediaからHTMLを取得中...")
response = requests.get(url, headers=headers)
response.raise_for_status()

print("テーブルデータを解析中...")
# Pandasの警告（StringIOのラップ）を回避しつつHTMLを読み込み
tables = pd.read_html(io.StringIO(response.text))
print(f"取得したテーブル数: {len(tables)}")

# 取得したテーブルをすべて結合
df_all = pd.concat(tables, ignore_index=True)
print(f"結合后的総行数: {len(df_all)}")

# カラム名のクリーニング（Wikipediaの引用や特殊文字、不正なタグ名を排除）
new_columns = []
for i, col in enumerate(df_all.columns):
    col_str = "_".join([str(c) for c in col]) if isinstance(col, tuple) else str(col)

    # Wikipediaの引用部分（[62]など）を削除
    col_str = re.sub(r'\[.*?\]', '', col_str)

    # スペースや括弧、スラッシュを置換
    col_str = col_str.strip().replace(' ', '_').replace('(', '').replace(')', '').replace('/', '_').replace(' ', '_')

    # XMLのタグ名として不正な文字が含まれる場合や、数字から始まる場合は安全な名前にフォールバック
    if not col_str or col_str[0].isdigit() or not re.match(r'^[\w\u3000-\u9fff_-]+$', col_str):
        col_str = f"col_{i}"

    new_columns.append(col_str)

df_all.columns = new_columns

# 欠損値（NaN）を空文字に置換
df_all = df_all.fillna("")

# XML形式に変換
xml_data = df_all.to_xml(index=False, encoding="utf-8", root_name="famicom_games", row_name="game")

# ファイルに保存
output_filename = "db/famicom_games_wiki.xml"
with open(output_filename, "w", encoding="utf-8") as f:
    f.write(xml_data)

print(f"XMLファイルの書き出しが完了しました: {output_filename}")

# Colab上でファイルをダウンロードする場合は以下のコメントアウトを解除
# from google.colab import files
# files.download(output_filename)
