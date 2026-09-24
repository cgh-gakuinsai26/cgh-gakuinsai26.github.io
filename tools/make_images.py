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

# 部活の表示順: (ファイル名の【】内, ファイル名用の英字 ID, 表示名)（新しい部活はここに追加）
CLUBS = [
    ("女子サッカー", "wsoccer", "女子サッカー部"),
    ("華道", "ikebana", "華道部"),
    ("茶道", "tea", "茶道部"),
    ("書道", "calligraphy", "書道部"),
    ("英語部", "english", "英語部"),
    ("パソコン", "pc", "パソコン部"),
    ("生物", "biology", "生物部"),
    ("美術部", "art", "美術部"),
    ("弓道部", "kyudo", "弓道部"),
    ("ハンドボール", "handball", "ハンドボール部"),
    ("女バレ", "wvolley", "女子バレーボール部"),
    ("チア", "cheer", "チアリーディング部"),
    ("吹奏楽", "brass", "吹奏楽部"),
    ("軽音学部", "lightmusic", "軽音楽部"),
    ("卓球", "tabletennis", "卓球部"),
]
ZEN = str.maketrans("0123456789", "０１２３４５６７８９")


def save(im, path, size):
    im = im.copy()
    im.thumbnail(size, Image.LANCZOS)
    im.save(path, "JPEG", quality=82, optimize=True, progressive=True)


def main():
    FULL.mkdir(parents=True, exist_ok=True)
    THUMB.mkdir(parents=True, exist_ok=True)
    club_ids = {key: pid for key, pid, _ in CLUBS}
    club_labels = {key: label for key, _, label in CLUBS}
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
        if is_class:
            grade, num = name.split("-")
            classes.append({"id": pid, "name": f"{grade}年{num}組".translate(ZEN),
                            "grade": int(grade), "num": int(num)})
        else:
            clubs[name] = {"id": pid, "name": club_labels[name]}

    classes.sort(key=lambda e: (e["grade"], e["num"]))
    for e in classes:
        del e["num"]
    ordered_clubs = [clubs[n] for n, _, _ in CLUBS if n in clubs]
    data = {"classes": classes, "clubs": ordered_clubs}
    (ROOT / "posters" / "data.js").write_text(
        "// tools/make_images.py が自動生成。表示名を変えたいときは name を書き換える。\n"
        "window.POSTERS = " + json.dumps(data, ensure_ascii=False, indent=2) + ";\n",
        encoding="utf-8",
    )
    print(f"クラス {len(classes)} 件, 部活 {len(ordered_clubs)} 件")


if __name__ == "__main__":
    main()
