import os
import requests

# libretro-databaseにあるファミコン（NES）用DATファイルのRaw URL
url = "https://github.com/libretro/libretro-database/raw/master/dat/Nintendo%20-%20Nintendo%20Entertainment%20System.dat"
output_filename = "db/nes_libretro.dat"

print("ファミコン用DATファイルをダウンロード中...")
response = requests.get(url)

if response.status_code == 200:
  with open(output_filename, "wb") as f:
    f.write(response.content)
  print(f"ダウンロード完了: {output_filename}")
  print(f"ファイルサイズ: {len(response.content) / (1024*1024):.2f} MB")
else:
  print(f"ダウンロードに失敗しました。ステータスコード: {response.status_code}")
