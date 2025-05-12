import csv, json
from pathlib import Path

INPUT = Path("data/boardgames.csv")
OUTPUT = Path("games_full.json")

with INPUT.open(encoding="utf-8") as f:
    reader = csv.DictReader(f)
    rows = list(reader)

games = []
for row in rows:
    id = row.get("id", "").strip()
    if not id:
        continue

    game = {
        "id": id,
        "title": row.get("title", "").strip(),
        "categories": [x.strip() for x in row.get("categories", "").split("/") if x.strip()],
        "minPlayers": int(row["minPlayers"]) if row["minPlayers"].isdigit() else None,
        "maxPlayers": int(row["maxPlayers"]) if row["maxPlayers"].isdigit() else None,
        "playTime": int(row["playTime"]) if row["playTime"].isdigit() else None,
        "difficulty": int(row["difficulty"]) if row["difficulty"].isdigit() else None,
        "socialIntensity": int(row["socialIntensity"]) if row["socialIntensity"].isdigit() else None,
        "learnEase": int(row["learnEase"]) if row["learnEase"].isdigit() else None,
        "description": row.get("description", "").strip(),
        "imageUrl": row.get("imageUrl", "").strip(),
        "similar": [],
    }

    games.append(game)

with OUTPUT.open("w", encoding="utf-8") as f:
    json.dump(games, f, ensure_ascii=False, indent=2)

print(f"✅ 已輸出 {len(games)} 筆遊戲資料 → games_full.json")
