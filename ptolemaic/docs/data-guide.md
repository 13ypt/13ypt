# データ編集ガイド / Data editing guide

ビジュアライザはすべて `ptolemaic/data/*.json` を読み込みます。ビルドや依存関係は不要です。JSON を編集してブラウザをリロードするだけで反映されます。

## 起動方法

```bash
cd ptolemaic
python3 -m http.server 8000
# http://localhost:8000/ を開く
```

（GitHub Pages に載せる場合は `ptolemaic/` をそのまま配信、または Pages のルートに置き換え可。）

## 年の表記

すべて BCE（紀元前）は **負の整数** で記述します。例：前 305 年 → `-305`。

## kings.json

王1人につき1オブジェクト。コレジェンシー（共同統治）と治世の中断を表現できます。

| フィールド | 必須 | 説明 |
|---|---|---|
| `id` | ✓ | 一意のID（URL安全）|
| `number` | ✓ | ローマ数字（"I", "II", …） |
| `name` / `nameJa` | ✓ | 欧文名 / 和名 |
| `epithet` / `epithetJa` | ✓ | 称号（例: Soter） |
| `start` / `end` | ✓ | 単独王としての治世開始・終了年（負数 = BCE） |
| `satrapFrom` |  | サトラップ就任年（プトレマイオス1世のみ） |
| `coregencyStart` / `soloFrom` |  | 共同統治期間（斜線表示）|
| `interruption` |  | 治世中断（亡命・追放）の配列 `[{from, to, note}]` |
| `color` |  | バーの色（省略時はデフォルト） |
| `isQueen` |  | `true` で女王レーンに表示 |
| `summary` / `summaryEn` | ✓ | 和文／英文の解説（ツールチップ・詳細画面で使用） |
| `source` |  | 典拠（ツールチップと詳細画面に表示） |

## events.json

政治的・宗教的・軍事的・反乱事件のポイントイベント。

| フィールド | 必須 | 説明 |
|---|---|---|
| `year` | ✓ | 年（負数 = BCE）|
| `category` | ✓ | `military` / `political` / `religious` / `revolt`（色分け）|
| `title` / `titleEn` | ✓ | 和文／英文タイトル |
| `note` |  | 補足 |
| `source` |  | 典拠（例: `OGIS 90`, `Polyb. V.79-86`） |

新しいカテゴリを追加したい場合は `assets/style.css` の `--event-*` 変数と、凡例／タグを合わせて拡張してください。

## apis.json / buchis.json

動物崇拝の個体データ。生誕・即位（祭儀上の導入）・没の3点で年代がある碑文に対応。

| フィールド | 必須 | 説明 |
|---|---|---|
| `id` | ✓ | 一意のID |
| `name` / `nameEn` | ✓ | 碑文番号や通称 |
| `birth` | ✓ | 生誕年（負数 = BCE） |
| `installed` |  | 神殿への導入・即位年（白い縦線で表示）|
| `death` | ✓ | 没年（●で表示）|
| `note` |  | 補足（碑文番号、特記事項）|
| `source` |  | 典拠（例: `Mond & Myers 1934, Bucheum II, stela 13`）|

## 参考文献 / Key references

- Hölbl, G. (2001). *A History of the Ptolemaic Empire*.
- Huss, W. (2001). *Ägypten in hellenistischer Zeit 332–30 v. Chr.*
- Vercoutter, J. (1962). *Textes biographiques du Sérapéum de Memphis.*
- Devauchelle, D. (1994). Articles on Serapeum stelae (BIFAO, RdE).
- Mond, R. & Myers, O. H. (1934). *The Bucheum*, 3 vols.
- Veïsse, A.-E. (2004). *Les « révoltes égyptiennes ».*
- Thompson, D. J. (2012). *Memphis under the Ptolemies* (2nd ed.).
- Pfeiffer, S. (2004). *Das Dekret von Kanopos (238 v. Chr.).*
- Roller, D. W. (2010). *Cleopatra: A Biography.*
- Bennett, C. (2001-2013). *Ptolemaic Dynasty* genealogy project (https://www.instonebrewer.com/tyndalearchive/egyptroyalgenealogy/).

## データの確認性について

動物崇拝の個体年代は、研究上の確定年代と推定年代が混在します。付属データはセラペウム碑文集成（Vercoutter 1962 以降）とブケウム碑文（Mond & Myers 1934 Vol. II）に基づく目安です。個別碑文に戻って厳密化する作業が研究の焦点となるため、`source` フィールドに具体的な碑文番号・出版物ページを入れて更新してください。
