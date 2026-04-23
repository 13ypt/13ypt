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

動物崇拝の個体年代は、研究上の確定年代と推定年代が混在します。付属データはセラペウム碑文集成（Vercoutter 1962, Thompson 2012 付録）とブケウム碑文（Mond & Myers 1934 Vol. II, Goldbrunner 2004 で再検討）に基づく目安です。個別碑文に戻って厳密化する作業が研究の焦点となるため、`source` フィールドに具体的な碑文番号・出版物ページを入れて更新してください。

### `dateConfidence` フィールド

Apis/Buchis エントリに任意で付加できるフラグ。論文で統計的な主張（例：王権交代と聖牛儀礼の同年同期）を行う場合、どのエントリに議論の余地があるかを明示するために使う。

| 値 | 意味 |
|---|---|
| `secure` | 碑文にエジプト暦日付（年・月・日）で記録され、近代暦換算も確立 |
| `calculated` | 寿命・在任期間からの逆算（記録なし） |
| `estimated` | 当該王の在位から推定したのみ、碑文年号の記録なし |
| `disputed` | 複数の解釈が競合（例: M/M 12 の王帰属、Mond/Myers vs 修正案） |
| `disputed-day` | 年は確実だが、月日の同定に議論あり（例: M7 没／M8 生の「同年」主張） |
| `birth-disputed` | 生年の記録に解釈余地（例: M8 の Ptol V 治世25年記述） |
| `birth-year-disputed` | 治世年表記が追放・共治期を算入するかで前後する（例: M13 の Ptol XII 治世28年） |

## 年表・聖牛相関を論じるときの方法論的注意

このサイトは王権交代と聖牛イベントの時間的相関を可視化しますが、研究出版物で主張する場合は以下を明示してください。

### 1. 循環論証のリスク

Apis/Buchis の年代復元は、王朝年表を基準として逆算・校正されたもの（Thompson 2012, Mond & Myers 1934, Goldbrunner 2004）。したがって「聖牛の年代」と「王の年代」が一致するのは、**部分的に定義によって真**である可能性がある。特に Mond & Myers stela の年号表記が当該王の治世年を使っている以上、埋葬年と王の没年の一致は独立した証拠ではない。

解決案：各聖牛について、碑文にエジプト暦で記録された治世年・月・日を独立変数として提示し、王朝年表とは別経路（セラペウム内記念碑の相対年代、天文学的年代、パピルスの同期記述）で復元した絶対年代と対照する。

### 2. ベースライン比較（負の事例）

プトレマイオス朝 275 年間（前 305〜前 30）に王の即位・没イベントは約 15–20 件。±1 年窓で約 45 年が「王権交代期」に該当し、全期間の約 16%。聖牛イベント 14 件がランダムに分布するなら、王権交代期に入る期待値は約 2.3 件。観測値 8 件は χ² で強く有意だが、刻銘が残る聖牛イベントに選択バイアスがあるため純粋な統計検定は効かない。

→ **負の事例を明示的に並べる**：聖牛イベントが記録されなかった王権交代、あるいは王権交代が無かった聖牛イベントを列挙し、相関の選択性を立体化する。

該当する可能性のある「負の事例」：
- プトレマイオス3世即位（前246年） — アピス T5 は前231年に初登場、ブキス M6 即位も前222年と数年のラグ
- プトレマイオス5世即位（前204年） — 近接する聖牛イベントなし
- プトレマイオス9世初度即位（前116年） — Apis T10 生年と同じだが帰属は Cleopatra III + IX 共治
- プトレマイオス9世再即位（前88年） — テーベ破壊の年、聖牛イベント記録なし
- プトレマイオス10世即位（前107年） — 近接記録なし
- Apis T7 没・埋葬（前164年） — 王権交代と対応しない純粋な聖牛事件
- Apis T5 即位（前231年） — 同上

### 3. 「同年」主張の精度

「同年」を単位とする議論と「同月」「同日」を単位とする議論では根拠が異なる。特に M7 没／M8 生、M9 没／Ptol VI 没は Mond/Myers 以降の再検討で年月日の精度に幅が認められる。

### 4. Thompson 2012 Appendix D は「provisional」

Thompson は Appendix D 冒頭で Apis リストを **provisional** と明言し、Devauchelle による全面刊行を待つ状態。したがって本サイトの Apis データを確定事実として引用せず、Devauchelle の原碑文集成に戻ること（Stèles du Sérapéum）。`dateConfidence` フィールドに `calculated` / `birth-unverified` / `install-secure-birth-death-calculated` 等を付与しているのはそのため。

特に以下の bull は論文引用時に再検証を要する：

- **Bull 8 (Tahor)**: 生年は Thompson に明記なし、寿命22年からの逆算。表上で「前145年前後に生まれた」と書いてはならない（前 Ptolemy VIII 単独即位年の連動主張は破綻する）。実際の記録は前158年 installation、前143年 7月21日 没の2点のみ確実。
- **Bull 10 (Gerege III)**: Thompson の Apis-year 計算では生 c. 前119年。stele 設置期前116–107年は「生」ではなく "installation / 出現"。王権交代（Ptol VIII 没 前116）との同期主張はこの解釈に依存。
- **Bull 11 (Taamun III)**: 初出 前86年2月25日は記録確実。生年はトンプソンに明記なし、検証不能。
- **Bull 12 (Tabastet)**: 初出 前60年1月21日は記録確実（Auletes 亡命 前58 の 2年前）。生年は Apis 年 19 からの逆算。
- **Bull 13 (Tapihy/Taihy)**: ★ 重要 ★ **前30年時点で生存**（Octavian が訪問拒否）。没ではない。表で「Bull 13 没 前30年」と書くと論旨が逆転する。Cass. Dio 51.16.5（Thompson の "Diod. Sic." は Dio の誤記）。Marković 2015 はこの訪問拒否を王的 Apis 保護伝統からの断絶として中心論点化。

### 5. Cleopatra VII の Apis 関与について — Revillout の再構築は信頼できない

Thompson 2012 Appendix D 脚注85 は Louvre の Cleopatra VII 治世3年（前50/49年）Apis stelae について、「クレオパトラは名前が挙がっておらず、男性プトレマイオス（おそらく兄弟）で年号が付されている。Revillout の Cleopatra VII 役割に関する再構築は信頼できない」と明示。

したがって：
- **Apis** について女王の直接関与を主張する碑文証拠は希薄。
- **Buchis stela 13** については別史料であり、関与の解釈は Žabkar 1983 vs Goldbrunner 2004 で分かれる（`buchis.json` M13 の `note` 参照）。
- 「Cleopatra VII は動物崇拝儀礼に積極関与した」という一般化は、Apis と Buchis を一緒くたにせず、史料ごとに分けて論じるべし。Bucheum vol. 3 の再精査が必要。

### 6. Mond/Myers 王番号付けの誤り

Mond & Myers 1934 の王番号付けは旧規格（Bevan 1927 以前）を部分的に使用しており、現代標準（Hölbl 1994 で確立）と一致しない。特に:

| M/M 番号 | Mond/Myers 表記 | 現代正式 | 備考 |
|---|---|---|---|
| Stela 10 | Ptolemy VII | Ptolemy VIII Euergetes II (Physcon) | 単独治世 |
| Stela 11 | Ptolemy VIII (= Soter II) | Ptolemy IX Soter II | 形式的帰属、実治世は VIII 末期 |
| Stela 12 | Ptolemy XI | ★ 修正: Ptolemy IX Soter II 第二治世 | Mond/Myers は Auletes に帰属したが年次計算不可 |
| Stela 13 | Cleopatra VI | Cleopatra VII | 同一女王 |

引用時は現代番号を用い、M/M の旧番号は併記すること。
