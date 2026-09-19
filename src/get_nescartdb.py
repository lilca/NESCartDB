import requests

# Nestopia / Libretro公式リポジトリにある、BootGodベースの決定版XMLデータベース
url = (
    "https://raw.githubusercontent.com/libretro/nestopia/master/NstDatabase.xml"
)
xml_filename = "NstDatabase.xml"

print(
    "決定版データベース (NstDatabase.xml) をGitHubから直接ダウンロード中..."
)
response = requests.get(url)

if response.status_code == 200:
  with open(xml_filename, "wb") as f:
    f.write(response.content)
  print(
      f"ダウンロード完了: {xml_filename}"
      f" ({len(response.content)/(1024*1024):.2f} MB)"
  )
else:
  print(f"ダウンロードに失敗しました。ステータスコード: {response.status_code}")
