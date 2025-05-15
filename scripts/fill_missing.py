#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
補齊 details/*.json 裡缺少的 imageUrl / description / 玩家數 / 時間
資料來源：BoardGameGeek（先 XML API 找 id，再爬網頁抓內容）
"""

import json, re, time, sys, logging
from pathlib import Path
from urllib.parse import quote
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

# ---------- 基本設定 -------------------------------------------------- #
ROOT      = Path(__file__).resolve().parents[1]
DETAILS   = ROOT / "details"
TMP       = ROOT / "tmp"
TMP.mkdir(exist_ok=True)
ERR_LOG   = TMP / "fill_errors.log"

logging.basicConfig(
    filename=ERR_LOG,
    level=logging.WARNING,
    format="%(asctime)s  %(levelname)s  %(message)s",
)

HEADERS = {"User-Agent": "TabletopParadiseBot/0.2 (+https://github.com/TELIFUJ)"}
TIMEOUT = 12   # seconds

# ---------- BGG helpers ------------------------------------------------ #
def bgg_search(title: str) -> str | None:
    """使用 BGG XML API 以 title 搜尋並回傳第一個 game-id。找不到回傳 None。"""
    url = f"https://api.geekdo.com/xmlapi2/search?type=boardgame&query={quote(title)}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        r.raise_for_status()
    except Exception as e:
        logging.warning("search error: %s → %s", title, e)
        return None
    m = re.search(r'id="(\d+)"', r.text)
    return m.group(1) if m else None


def bgg_scrape(game_id: str) -> dict:
    """爬取 BGG 頁面並擷取 imageUrl / description / min/max players / playTime"""
    url = f"https://boardgamegeek.com/boardgame/{game_id}"
    try:
        html = requests.get(url, headers=HEADERS, timeout=TIMEOUT).text
    except Exception as e:
        logging.warning("scrape error: %s → %s", url, e)
        return {}

    soup = BeautifulSoup(html, "html.parser")

    # 封面
    img_tag   = soup.select_one("img[data-image]")
    image_url = img_tag["src"] if img_tag else ""

    # 描述
    desc_tag    = soup.select_one(".game-description")
    description = desc_tag.text.strip() if desc_tag else ""

    # 玩家數、時間
    text     = soup.get_text(" ", strip=True)
    min_p = max_p = play_time = None

    p = re.search(r"Players\s+(\d+)[^\d]+(\d+)", text)
    if p:
        min_p, max_p = int(p.group(1)), int(p.group(2))

    t = re.search(r"Playing Time\s+(\d+)", text)
    if t:
        play_time = int(t.group(1))

    return {
        "imageUrl": image_url,
        "description": description,
        "minPlayers": min_p,
        "maxPlayers": max_p,
        "playTime": play_time,
    }


def merge_data(original: dict, fetched: dict) -> dict:
    """原檔已有值就保留；沒有值才用 fetched 補"""
    result = original.copy()
    for k, v in fetched.items():
        if not v:
            continue
        # imageUrl / description 空字串可以被覆蓋
        if k in ("imageUrl", "description"):
            if original.get(k) in (None, "", []):
                result[k] = v
        else:
            if original.get(k) in (None, "", []):
                result[k] = v
    return result

# ---------- main ------------------------------------------------------- #
def main():
    # 收集所有 details/*.json + details/b/*.json
    detail_files = sorted(DETAILS.glob("*.json")) + sorted((DETAILS / "b").glob("*.json"))
    detail_files = detail_files[:20]  # ✅ 測試用途：只補前 20 筆，避免補太久卡住

    need_fill: list[Path] = []
    for f in detail_files:
        data = json.loads(f.read_text())
        if (not data.get("imageUrl")) or (not data.get("description")):
            need_fill.append(f)

    print(f"↯ 共有 {len(need_fill)} 筆資料需要補強")

    for jfile in tqdm(need_fill, desc="補資料中"):
        data  = json.loads(jfile.read_text())
        title = data.get("title")
        if not title:
            logging.warning("缺少 title：%s", jfile.name)
            continue

        try:
            gid = bgg_search(title)
            if not gid:
                fetched = {}
            else:
                fetched = bgg_scrape(gid)
        except Exception as e:
            logging.warning("skip %s: %s", title, e)
            fetched = {}

        # ⬇⬇ 永遠補 fallback，確保檔案有寫入
        if not fetched.get("description"):
            fetched["description"] = "（尚無簡介，歡迎日後補充！）"
        if not fetched.get("imageUrl"):
            fetched["imageUrl"] = "https://telifuj.github.io/tabletop-paradise/images/placeholder.jpg"

        data_filled = merge_data(data, fetched)
        jfile.write_text(json.dumps(data_filled, ensure_ascii=False, indent=2))

        time.sleep(2)  # 避免對 BGG 過於頻繁

    print("✅ 補資料腳本完成")
    if ERR_LOG.exists():
        print(f"⚠️  錯誤或超時請查看 {ERR_LOG}")


if __name__ == "__main__":
    main()
