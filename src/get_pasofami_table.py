import io
import os
import re
import pandas as pd
import requests

target_url = "http://pasofami.game.coocan.jp/nesalltitlelst.htm"

print("Wayback Machineからアーカイブ情報を取得中...")
api_url = f"http://archive.org/wayback/available?url={target_url}"
api_res = requests.get(api_url).json()

if (
    "archived_snapshots" in api_res
    and "closest" in api_res["archived_snapshots"]
):
  archive_url = api_res["archived_snapshots"]["closest"]["url"]
  print(f"取得元アーカイブURL: {archive_url}")
else:
  raise RuntimeError("Wayback Machineに対象ページのアーカイブが見つかりません。")

print("PasofamiのHTMLを取得中...")
headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,"
        " like Gecko) Chrome/122.0.0.0 Safari/537.36"
    )
}
response = requests.get(archive_url, headers=headers)
response.encoding = "shift_jis"
response.raise_for_status()

print("テーブルデータを解析中...")
tables = pd.read_html(io.StringIO(response.text))
print(f"取得したテーブル数: {len(tables)}")

if len(tables) > 0:
  df_all = pd.concat(tables, ignore_index=True)
else:
  raise ValueError("テーブルが見つかりませんでした。")

print(f"総行数: {len(df_all)}")

# カラム名のクリーニング
new_columns = []
for i, col in enumerate(df_all.columns):
  col_str = (
    "_".join([str(c) for c in col]) if isinstance(col, tuple) else str(col)
  )
  col_str = re.sub(r"\[.*?\]", "", col_str)
  col_str = (
    col_str.strip()
    .replace(" ", "_")
    .replace("(", "")
    .replace(")", "")
    .replace("/", "_")
  )
  if (
    not col_str
    or col_str[0].isdigit()
    or not re.match(r"^[\w\u3000-\u9fff_-]+$", col_str)
  ):
    col_str = f"col_{i}"
  new_columns.append(col_str)

df_all.columns = new_columns
df_all = df_all.fillna("")

# XML形式に変換
xml_data = df_all.to_xml(
    index=False, encoding="utf-8", root_name="pasofami_nes_games", row_name="game"
)

# dbディレクトリに保存
output_dir = "db"
os.makedirs(output_dir, exist_ok=True)
output_filename = os.path.join(output_dir, "pasofami_nes_games.xml")

with open(output_filename, "w", encoding="utf-8") as f:
  f.write(xml_data)

print(f"XMLファイルの書き出しが完了しました: {output_filename}")
