import csv, json
from pathlib import Path

INPUT = Path("data/boardgames.csv")
DETAILS_DIR = Path("details")
DETAILS_DIR.mkdir(exist_ok=True)

with INPUT.open(encoding="utf-8-sig") as f:  # 解決 Excel BOM 問題
    reader = csv.DictReader(f)
    rows = list(reader)

games = []
count = 0

for row in rows:
    id = row.get("id", "").strip()
    if not id:
        continue

    title = row.get("title", "").strip()
    description = row.get("description", "").strip()
    imageUrl = row.get("imageUrl", "").strip()

    # 分類欄支援 , 或 /
    raw_categories = row.get("categories", "")
    categories = [x.strip() for x in raw_categories.replace(",", "/").split("/") if x.strip()]

    def safe_int(key):
        val = row.get(key, "").strip()
        return int(val) if val.isdigit() else None

    game = {
        "id": id,
        "title": title,
        "categories": categories,
        "minPlayers": safe_int("minPlayers"),
        "maxPlayers": safe_int("maxPlayers"),
        "playTime": safe_int("playTime"),
        "difficulty": safe_int("difficulty"),
        "socialIntensity": safe_int("socialIntensity"),
        "learnEase": safe_int("learnEase"),
        "description": description,
        "imageUrl": imageUrl,
        "similar": [],
    }

    # 寫入單筆檔案
    with (DETAILS_DIR / f"{id}.json").open("w", encoding="utf-8") as f:
        json.dump(game, f, ensure_ascii=False, indent=2)

    games.append(game)
    count += 1

# 合併所有遊戲為一份網站主檔
FULL_OUTPUT = Path("public/games_full.json")
with FULL_OUTPUT.open("w", encoding="utf-8") as f:
    json.dump(games, f, ensure_ascii=False, indent=2)

print(f"✅ 已輸出 {count} 筆遊戲資料 → details/*.json")
print(f"✅ 合併完成 → public/games_full.json")
