# Ptolemaic Timeline Visualiser

プトレマイオス朝エジプト（前 332〜前 30 年）の王の治世、主要な政治的出来事、およびアピス牛・ブキス牛崇拝の年代データを統合的に可視化する、研究用の軽量ウェブサイトです。

## 特徴

- **全員タイムライン**: 全王（男王／女王）を横軸年代で重ねて表示。共同統治は斜線、治世中断（亡命）は点線の暗色矩形。
- **王個別ビュー**: サイドバーから王を選ぶと、その治世に限定したミニタイムライン＋同期間の政治事件・アピス／ブキス牛が集約表示。
- **4レイヤー**: 王／政治事件／アピス／ブキスを個別にオン・オフ可能。
- **出典表示**: 各項目にツールチップ・詳細画面で `source` を表示（Hölbl, Huss, Vercoutter, Mond & Myers, Veïsse など）。
- **日⇄英切替**: 右上の言語ボタンで表示言語を切替。
- **ズーム**: タイムラインの年あたりピクセル数を変更可能。
- **依存ゼロ**: 純粋な HTML/CSS/vanilla JS + JSON。`python3 -m http.server` で即起動。

## 起動

```bash
cd ptolemaic
python3 -m http.server 8000
# http://localhost:8000/ を開く
```

GitHub Pages に載せる場合は、このディレクトリをルート（またはサブディレクトリ）として配信してください。

## ディレクトリ構成

```
ptolemaic/
├── index.html          # エントリ
├── assets/
│   ├── style.css
│   └── app.js          # SVG レンダラと UI ロジック
├── data/
│   ├── kings.json      # 王 (治世・共同統治・中断)
│   ├── events.json     # 政治・宗教・軍事・反乱
│   ├── apis.json       # アピス牛 (生誕・即位・没)
│   └── buchis.json     # ブキス牛 (生誕・即位・没)
└── docs/
    └── data-guide.md   # データ編集ガイド
```

## データの拡張

すべてのデータは JSON ファイルに外出しされています。詳細は [`docs/data-guide.md`](docs/data-guide.md) を参照。各エントリに `source` フィールドを設けており、碑文番号・文献ページを加えることで研究ノートとして蓄積できます。

## 既知の限界

- アピス／ブキスの個体年代は出典ベースの目安。個別碑文（Sérapéum stelae, Bucheum stelae）による厳密化は `data/*.json` に直接反映できます。
- ロゼッタ・ストーン等の勅令と連動する祭儀活動は `events.json` の `religious` カテゴリに入れています。
