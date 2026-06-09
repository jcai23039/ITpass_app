from datetime import datetime
import os

print(f"現在実行中のファイル: {__file__}")   

file_name = "study_log.txt"

now_date = datetime.now().strftime("%Y-%m-%d")

if os.path.exists(file_name):
    print(f"確認: {file_name} はすでに存在しています。上書きします。")
else:
    print(f"確認: {file_name} は存在しません。新しく作成します。")

with open(file_name, mode="w", encoding="utf-8") as f:
    f.write(f"{now_date} Python学習開始\n")

with open(file_name, mode="a", encoding="utf-8") as f:
    f.write("ファイル操作を学習\n")

print(f"\n--- {file_name} ---")
with open(file_name, mode="r", encoding="utf-8") as f:
    content = f.read()
    print(content, end="")
