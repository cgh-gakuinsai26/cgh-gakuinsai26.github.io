# 学院祭 出店ポスター

公開URL: https://cgh-gakuinsai26.github.io/

## ポスターの追加・差し替え

1. `uploads/` に画像を入れる（ファイル名は `【2-3】ポスター.jpg`、`【吹奏楽】ポスター.jpg` の形式）
   - 【】内が「数字-数字」ならクラス、それ以外は部活
   - 新しい部活は `tools/make_images.py` の `CLUBS` に追加する（表示名と並び順もここで決める）
2. `python3 tools/make_images.py` を実行（`pip install pillow` が必要）
   - `posters/full/`（拡大表示用）、`posters/thumb/`（一覧用）、`posters/data.js`（一覧データ）が作り直される
3. 表示名を変えたいときは `posters/data.js` の `name` を書き換える
   （ただし 2 を再実行すると元に戻るので、その場合は `make_images.py` 側で調整する）
