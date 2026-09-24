"""uploads/ の元画像から posters/full（拡大表示用）と posters/thumb（一覧用）を作る。

ファイル名は「【1-1】ポスター.jpg」「【吹奏楽】ポスター.jpg」の形式を想定。
【】内が「数字-数字」ならクラス、それ以外は部活として扱う。
使い方: python3 tools/make_images.py  （pip install pillow が必要）
"""
import json
import re
import unicodedata
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "uploads"
FULL = ROOT / "posters" / "full"
THUMB = ROOT / "posters" / "thumb"
FULL_MAX = (1400, 2000)   # 拡大表示用の最大サイズ（幅, 高さ）
THUMB_W = 360             # 一覧用サムネイルの幅

# 部活の表示順とファイル名用の英字 ID（新しい部活はここに追加）
CLUBS = [
    ("吹奏楽", "brass"), ("軽音学部", "lightmusic"), ("美術部", "art"),
    ("書道", "calligraphy"), ("華道", "ikebana"), ("茶道", "tea"),
    ("英語部", "english"), ("生物", "biology"), ("パソコン", "pc"),
    ("弓道部", "kyudo"), ("卓球", "tabletennis"), ("ハンドボール", "handball"),
    ("女子サッカー", "wsoccer"), ("女バレ", "wvolley"), ("チア", "cheer"),
]


def save(im, path, size):
    im = im.copy()
    im.thumbnail(size, Image.LANCZOS)
    im.save(path, "JPEG", quality=82, optimize=True, progressive=True)


def main():
    FULL.mkdir(parents=True, exist_ok=True)
    THUMB.mkdir(parents=True, exist_ok=True)
    club_ids = dict(CLUBS)
    classes, clubs = [], {}
    for f in sorted(SRC.iterdir()):
        m = re.search(r"【(.+?)】", unicodedata.normalize("NFC", f.name))
        if not m:
            print("skip:", f.name)
            continue
        name = m.group(1)
        is_class = re.fullmatch(r"\d-\d+", name) is not None
        if is_class:
            pid = "c" + name
        elif name in club_ids:
            pid = club_ids[name]
        else:
            print("CLUBS に未登録の部活:", name)
            continue
        im = ImageOps.exif_transpose(Image.open(f))
        if im.mode in ("RGBA", "LA", "P"):
            im = im.convert("RGBA")
            bg = Image.new("RGB", im.size, "white")
            bg.paste(im, mask=im.split()[-1])
            im = bg
        else:
            im = im.convert("RGB")
        save(im, FULL / f"{pid}.jpg", FULL_MAX)
        save(im, THUMB / f"{pid}.jpg", (THUMB_W, THUMB_W * 2))
        entry = {"id": pid, "name": name}
        if is_class:
            classes.append(entry)
        else:
            clubs[name] = entry

    classes.sort(key=lambda e: tuple(int(x) for x in e["name"].split("-")))
    ordered_clubs = [clubs[n] for n, _ in CLUBS if n in clubs]
    data = {"classes": classes, "clubs": ordered_clubs}
    (ROOT / "posters" / "data.js").write_text(
        "// tools/make_images.py が自動生成。表示名を変えたいときは name を書き換える。\n"
        "window.POSTERS = " + json.dumps(data, ensure_ascii=False, indent=2) + ";\n",
        encoding="utf-8",
    )
    print(f"クラス {len(classes)} 件, 部活 {len(ordered_clubs)} 件")


if __name__ == "__main__":
    main()
