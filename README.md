# kanji

小学生の漢字プリントメーカー（東京書籍「新しい国語」小1〜小3）。https://morihayashi-juku.github.io/kanji/

学年と「ここまで習った単元」を選ぶと、その範囲の復習プリント（A4横・縦書き、読み14問＋書き10問、こたえ別ページ）がその場でできる。

- 漢字・読み・例文のデータは `data/g1.txt`〜`data/g3.txt`、手順は `CLAUDE.md`。
- `index.html` は `python3 tools/build.py` で作る（データが中に入った1ファイル）。
