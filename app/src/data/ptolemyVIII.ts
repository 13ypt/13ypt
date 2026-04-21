import type { King } from "./types";

// プトレマイオス8世エウエルゲテス2世（フュスコン）のサンプルデータ。
// 引用は実在の学術文献・一次史料を参照しているが、学術利用時には
// 必ず一次情報を再確認のうえ、必要に応じて追加・修正してください。

export const ptolemyVIII: King = {
  id: "ptolemy-viii",
  name: "Ptolemy VIII Euergetes II",
  nameJa: "プトレマイオス8世エウエルゲテス2世",
  epithet: "Physcon / Kakergetes",
  epithetJa: "フュスコン（肥満王）／カケルゲテス",
  birthYear: -184,
  deathYear: -116,
  reigns: [
    { start: -170, end: -163, noteJa: "兄プトレマイオス6世・姉クレオパトラ2世との三者共治" },
    { start: -163, end: -145, noteJa: "キュレナイカ王" },
    { start: -145, end: -116, noteJa: "エジプト王（クレオパトラ2世・3世と共治）" },
  ],

  places: [
    { id: "alexandria", name: "Alexandria", nameJa: "アレクサンドリア", lat: 31.2001, lng: 29.9187 },
    { id: "eleusis-alex", name: "Eleusis (suburb of Alexandria)", nameJa: "エレウシス（アレクサンドリア近郊）", lat: 31.18, lng: 29.95 },
    { id: "memphis", name: "Memphis", nameJa: "メンフィス", lat: 29.8440, lng: 31.2547 },
    { id: "cyrene", name: "Cyrene", nameJa: "キュレネ", lat: 32.8250, lng: 21.8583 },
    { id: "paphos", name: "Paphos", nameJa: "パフォス（キュプロス）", lat: 34.7571, lng: 32.4056 },
    { id: "thebes", name: "Thebes", nameJa: "テーベ", lat: 25.7188, lng: 32.6103 },
    { id: "tebtunis", name: "Tebtunis", nameJa: "テブテュニス", lat: 29.1080, lng: 30.7434 },
    { id: "pelusium", name: "Pelusium", nameJa: "ペルシオン", lat: 31.0459, lng: 32.5422 },
  ],

  citations: [
    {
      id: "holbl2001",
      authors: "Hölbl, G.",
      year: 2001,
      title: "A History of the Ptolemaic Empire",
      publication: "London/New York: Routledge",
      pages: "pp. 194–204, 281–304",
    },
    {
      id: "huss2001",
      authors: "Huss, W.",
      year: 2001,
      title: "Ägypten in hellenistischer Zeit, 332–30 v. Chr.",
      publication: "München: C. H. Beck",
      pages: "S. 540–631",
    },
    {
      id: "chauveau2000",
      authors: "Chauveau, M.",
      year: 2000,
      title: "Egypt in the Age of Cleopatra: History and Society under the Ptolemies",
      publication: "Ithaca: Cornell University Press",
    },
    {
      id: "whitehorne1994",
      authors: "Whitehorne, J.",
      year: 1994,
      title: "Cleopatras",
      publication: "London/New York: Routledge",
      pages: "pp. 103–131",
    },
    {
      id: "mooren1988",
      authors: "Mooren, L.",
      year: 1988,
      title: "The Wives and Children of Ptolemy VIII Euergetes II",
      publication: "Proceedings of the XVIII International Congress of Papyrology, vol. II, Athens",
      pages: "pp. 435–444",
    },
    {
      id: "polybius",
      authors: "Polybius",
      year: "c. 150 BCE",
      title: "Histories, Book XXIX.27 (Day of Eleusis)",
      publication: "ed. Büttner-Wobst, Teubner",
      note: "一次史料（ポリュビオス）",
    },
    {
      id: "livy-xlv",
      authors: "Livius",
      year: "c. 20 BCE",
      title: "Ab Urbe Condita, XLV.12",
      publication: "Loeb Classical Library",
      note: "一次史料（リウィウス）",
    },
    {
      id: "gruen1984",
      authors: "Gruen, E. S.",
      year: 1984,
      title: "The Hellenistic World and the Coming of Rome",
      publication: "Berkeley: University of California Press",
      pages: "pp. 651–664",
    },
    {
      id: "seg-ix-7",
      authors: "SEG IX 7 (ed. Oliverio 1932)",
      year: -155,
      title: "Testamentum Ptolemaei VIII Euergetae (Cyrene Will)",
      publication: "Supplementum Epigraphicum Graecum IX, no. 7",
      note: "一次史料（碑文）",
    },
    {
      id: "braund1983",
      authors: "Braund, D.",
      year: 1983,
      title: "Royal Wills and Rome",
      publication: "Papers of the British School at Rome 51",
      pages: "pp. 16–57",
    },
    {
      id: "ptebt-i-5",
      authors: "Grenfell, B. P., Hunt, A. S., Smyly, J. G.",
      year: 1902,
      title: "P.Tebt. I 5 — Philanthrōpa of Ptolemy VIII, Cleopatra II and III",
      publication: "The Tebtunis Papyri, Part I, London: Henry Frowde",
      pages: "no. 5, pp. 12–55",
      note: "一次史料（パピルス）",
    },
    {
      id: "lenger-cordptol",
      authors: "Lenger, M.-T.",
      year: 1980,
      title: "Corpus des Ordonnances des Ptolémées (C.Ord.Ptol.)",
      publication: "Bruxelles: Académie Royale de Belgique",
      pages: "no. 53 (Amnesty decree of 118 BCE)",
    },
    {
      id: "veisse2004",
      authors: "Veïsse, A.-E.",
      year: 2004,
      title: "Les « révoltes égyptiennes »: Recherches sur les troubles intérieurs en Égypte du règne de Ptolémée III à la conquête romaine",
      publication: "Studia Hellenistica 41, Leuven: Peeters",
    },
    {
      id: "mcging1997",
      authors: "McGing, B. C.",
      year: 1997,
      title: "Revolt Egyptian Style: Internal Opposition to Ptolemaic Rule",
      publication: "Archiv für Papyrusforschung 43",
      pages: "pp. 273–314",
    },
    {
      id: "bennett-online",
      authors: "Bennett, C.",
      year: "2001–2013",
      title: "Ptolemaic Genealogy: Ptolemy VIII",
      publication: "Egyptian Royal Genealogy (online database)",
      url: "https://www.tyndalehouse.com/egypt/ptolemies/ptolemy_viii.htm",
    },
  ],

  events: [
    {
      id: "pviii-accession-170",
      startYear: -170,
      placeId: "alexandria",
      title: "Proclaimed co-ruler during the Sixth Syrian War",
      titleJa: "第6次シリア戦争下で共治王として即位",
      summary:
        "Amid Antiochus IV’s invasion threat, the Alexandrian court proclaimed the young Ptolemy VIII joint king with his elder brother Ptolemy VI and sister Cleopatra II.",
      summaryJa:
        "セレウコス朝アンティオコス4世の侵攻危機のなか、アレクサンドリア宮廷は若きプトレマイオス8世を兄プトレマイオス6世・姉クレオパトラ2世との共治王として擁立した。",
      category: "reign",
      citationIds: ["holbl2001", "huss2001", "polybius"],
      stateOfCountryJa:
        "王朝は幼少王3人による脆弱な三者共治。ラフィア会戦以後のネイティヴ・エジプト人兵士台頭（マキモイ）と大反乱（上エジプト独立王国の記憶）が残存し、中央財政は逼迫。",
      stateOfCountry:
        "Triple monarchy of three young siblings; aftermath of Raphia and the Great Revolt in Upper Egypt leaves central finances strained.",
    },
    {
      id: "pviii-antiochus-169",
      startYear: -169,
      placeId: "alexandria",
      title: "Antiochus IV occupies Lower Egypt; Ptolemy VIII proclaimed sole king",
      titleJa: "アンティオコス4世による下エジプト占領と単独王宣言",
      summary:
        "After Ptolemy VI was captured by Antiochus IV, the Alexandrians proclaimed Ptolemy VIII sole king. The brothers were soon formally reconciled.",
      summaryJa:
        "プトレマイオス6世がアンティオコス4世に捕縛されると、アレクサンドリア市民は8世を単独王として擁立。まもなく兄弟間の公式な和解が成立した。",
      category: "war",
      citationIds: ["polybius", "livy-xlv", "holbl2001", "huss2001"],
      stateOfCountryJa:
        "下エジプトの広範な地域がセレウコス軍に占拠され、宮廷は首都アレクサンドリアに籠城。神殿経済・灌漑体系は混乱。",
    },
    {
      id: "pviii-eleusis-168",
      startYear: -168,
      placeId: "eleusis-alex",
      title: "Day of Eleusis — Roman intervention forces Antiochus IV’s withdrawal",
      titleJa: "「エレウシスの日」──ローマの介入によるアンティオコス4世撤退",
      summary:
        "At Eleusis, a suburb of Alexandria, the Roman envoy C. Popillius Laenas drew a circle around Antiochus IV and compelled him to withdraw from Egypt — a decisive assertion of Roman hegemony over the Hellenistic East.",
      summaryJa:
        "アレクサンドリア近郊エレウシスにて、ローマ使節ポピリウス・ラエナスがアンティオコス4世の足元に円を描き、エジプト退去を即答させた有名な事件。ヘレニズム世界へのローマ覇権確立の画期。",
      category: "diplomacy",
      citationIds: ["polybius", "livy-xlv", "gruen1984", "holbl2001"],
      stateOfCountryJa:
        "王朝は軍事的には救われたが、以後プトレマイオス朝外交はローマの仲裁権を前提とする構造へ転換する。",
    },
    {
      id: "pviii-expel-vi-164",
      startYear: -164,
      placeId: "alexandria",
      title: "Ptolemy VIII expels Ptolemy VI from Alexandria",
      titleJa: "プトレマイオス6世をアレクサンドリアから追放",
      summary:
        "Tensions between the brothers erupted; Ptolemy VIII drove Ptolemy VI out of Alexandria. Ptolemy VI fled to Rome to petition the Senate.",
      summaryJa:
        "兄弟間の緊張が臨界に達し、8世は6世をアレクサンドリアから追放。6世はローマ元老院に援助を請うため渡航した。",
      category: "family",
      citationIds: ["polybius", "holbl2001", "whitehorne1994"],
      stateOfCountryJa:
        "宮廷分裂。軍・官僚団は両王に分かれて忠誠を誓い、行政機能は一時麻痺。",
    },
    {
      id: "pviii-rome-partition-163",
      startYear: -163,
      placeId: "cyrene",
      title: "Roman arbitration: Ptolemy VIII receives Cyrenaica",
      titleJa: "ローマの仲裁によるキュレナイカ授与",
      summary:
        "The Roman Senate partitioned the realm: Ptolemy VI retained Egypt and Cyprus, while Ptolemy VIII received Cyrenaica and moved his court to Cyrene.",
      summaryJa:
        "ローマ元老院は王国を分割。6世はエジプトとキュプロスを保持し、8世はキュレナイカを獲得してキュレネに宮廷を移した。",
      category: "diplomacy",
      citationIds: ["polybius", "holbl2001", "huss2001"],
      stateOfCountryJa:
        "帝国は事実上二分され、キュレナイカ宮廷は独立した貨幣発行と外交を行う。エジプト本体はプトレマイオス6世治下で相対的安定期に入る。",
    },
    {
      id: "pviii-cyprus-attempts",
      startYear: -162,
      endYear: -154,
      placeId: "paphos",
      title: "Repeated attempts to seize Cyprus",
      titleJa: "キュプロス奪取を繰り返し企図",
      summary:
        "Between 162 and 154 BCE Ptolemy VIII made multiple attempts, supported by Roman embassies, to wrest Cyprus from Ptolemy VI. All failed militarily.",
      summaryJa:
        "前162〜154年にかけて、ローマの使節団支援のもとキュプロス奪取を繰り返し試みるが、軍事的にはいずれも失敗。",
      category: "war",
      citationIds: ["polybius", "holbl2001", "huss2001"],
      stateOfCountryJa:
        "キュレナイカ財政は軍事遠征で消耗。外交的にはローマの言質を得つつ実力では兄に及ばず、国際的地位が低迷。",
    },
    {
      id: "pviii-will-155",
      startYear: -155,
      placeId: "cyrene",
      title: "Testamentary bequest of Cyrenaica to Rome (SEG IX 7)",
      titleJa: "キュレナイカをローマに遺贈する「遺言碑文」",
      summary:
        "After surviving an assassination attempt, Ptolemy VIII publicly inscribed a will bequeathing Cyrenaica to Rome should he die without legitimate heirs — the earliest attested royal testament to Rome.",
      summaryJa:
        "暗殺未遂を生き延びた8世は、嫡子なくして没した場合キュレナイカをローマに遺贈する旨を公に碑文化。ローマへの王位遺贈の先駆例とされる。",
      category: "diplomacy",
      citationIds: ["seg-ix-7", "braund1983", "holbl2001"],
      stateOfCountryJa:
        "キュレナイカは事実上ローマの被保護国化。王朝の主権の「条件付き」性が明文化された画期的文書。",
    },
    {
      id: "pviii-return-145",
      startYear: -145,
      placeId: "alexandria",
      title: "Return to Alexandria; marriage to Cleopatra II; purges",
      titleJa: "アレクサンドリア帰還、クレオパトラ2世との結婚、粛清",
      summary:
        "On Ptolemy VI’s death in Syria, Ptolemy VIII returned to Egypt, married his sister-widow Cleopatra II, and — according to Justin — killed her young son (Ptolemy VII ‘Neos Philopator’) at the wedding feast.",
      summaryJa:
        "兄6世のシリアでの戦死を受けて帰国。寡婦となった姉クレオパトラ2世と結婚し、ユスティヌスによれば婚宴の最中に彼女の幼い息子（プトレマイオス7世ネオス・フィロパトル）を殺害した。",
      category: "family",
      citationIds: ["holbl2001", "whitehorne1994", "mooren1988", "huss2001"],
      stateOfCountryJa:
        "王権再統合。しかし住民殺戮・ギリシア系知識人の追放（アレクサンドリア学派の離散）が伝えられ、アテナイオス等に反映された反フュスコン伝承の起点となる。",
    },
    {
      id: "pviii-marry-ciii-142",
      startYear: -142,
      placeId: "alexandria",
      title: "Marries his niece Cleopatra III",
      titleJa: "姪クレオパトラ3世との結婚",
      summary:
        "Without divorcing Cleopatra II, Ptolemy VIII also married her daughter Cleopatra III, establishing a tense three-cornered royal household.",
      summaryJa:
        "クレオパトラ2世と離婚せぬままその娘クレオパトラ3世とも結婚し、三者並立の不安定な王室を形成。",
      category: "family",
      citationIds: ["mooren1988", "whitehorne1994", "holbl2001"],
      stateOfCountryJa:
        "宮廷派閥は「2世派」と「3世派」に分裂。以後の内戦と政策対立の構造的起点。",
    },
    {
      id: "pviii-civil-war-132",
      startYear: -132,
      endYear: -124,
      placeId: "thebes",
      title: "Civil war with Cleopatra II; Upper Egypt in turmoil",
      titleJa: "クレオパトラ2世との内戦と上エジプトの混乱",
      summary:
        "Cleopatra II revolted in Alexandria; Ptolemy VIII fled to Cyprus with Cleopatra III. Concurrently, a native Egyptian revolt led by Harsiesi briefly held Thebes (132/1–130 BCE).",
      summaryJa:
        "クレオパトラ2世がアレクサンドリアで反乱、8世はクレオパトラ3世とともにキュプロスへ亡命。並行してハルシエシの率いるエジプト人反乱が短期間テーベを制圧した（前132/1〜130年）。",
      category: "revolt",
      citationIds: ["veisse2004", "mcging1997", "holbl2001", "huss2001"],
      stateOfCountryJa:
        "王国は南北に分断。上エジプトでは在地神官・軍人層が「ファラオ」を擁立し、プトレマイオス王権の象徴的・行政的正統性が一時的に失われる。",
    },
    {
      id: "pviii-memphites-130",
      startYear: -130,
      placeId: "paphos",
      title: "Alleged killing of Ptolemy Memphites",
      titleJa: "プトレマイオス・メンフィテス殺害伝承",
      summary:
        "According to Diodorus and Justin, from Cyprus Ptolemy VIII had his own son by Cleopatra II (Ptolemy Memphites) dismembered and sent to the queen on her birthday. Historicity debated.",
      summaryJa:
        "ディオドロスやユスティヌスによれば、キュプロスから8世はクレオパトラ2世との間の息子プトレマイオス・メンフィテスを殺害し、彼女の誕生日に遺体を送りつけたという。史実性は議論がある。",
      category: "family",
      citationIds: ["whitehorne1994", "holbl2001", "mooren1988"],
      stateOfCountryJa:
        "プロパガンダ戦が激化。後世の反フュスコン伝承の核となる挿話。",
    },
    {
      id: "pviii-return-127",
      startYear: -127,
      placeId: "alexandria",
      title: "Ptolemy VIII re-enters Alexandria",
      titleJa: "アレクサンドリア再入城",
      summary:
        "After years of fighting, Ptolemy VIII regained Alexandria; Cleopatra II fled to Syria.",
      summaryJa:
        "数年の戦闘の末、8世はアレクサンドリアを奪回。クレオパトラ2世はシリアへ逃亡した。",
      category: "reign",
      citationIds: ["holbl2001", "huss2001"],
      stateOfCountryJa:
        "中央権力は回復しつつあるが、下エジプトの行政網は荒廃し、税務・灌漑の再建が急務となる。",
    },
    {
      id: "pviii-reconcile-124",
      startYear: -124,
      placeId: "alexandria",
      title: "Reconciliation of the royal trio",
      titleJa: "王家三者の和解",
      summary:
        "Cleopatra II returned to Egypt and joint rule of Ptolemy VIII, Cleopatra II, and Cleopatra III was re-established, paving the way for the great amnesty of 118 BCE.",
      summaryJa:
        "クレオパトラ2世がエジプトに帰還し、8世・2世・3世による共治が再構築された。これは前118年の大恩赦令への布石となる。",
      category: "diplomacy",
      citationIds: ["holbl2001", "whitehorne1994", "huss2001"],
    },
    {
      id: "pviii-amnesty-118",
      startYear: -118,
      placeId: "tebtunis",
      title: "Great Amnesty Decree (P.Tebt. I 5 / C.Ord.Ptol. 53)",
      titleJa: "大恩赦令（P.Tebt. I 5 ／ C.Ord.Ptol. 53）",
      summary:
        "A comprehensive set of philanthrōpa addressing arrears, land tenure, temple privileges, the status of the Egyptian priesthood, and Greek/Egyptian legal jurisdiction. Crucial for Ptolemaic social and administrative history.",
      summaryJa:
        "延滞税・土地保有・神殿特権・エジプト人神官身分・ギリシア法／エジプト法の管轄区分を包括的に整理したフィラントロパ（恩典）勅令群。プトレマイオス朝社会・行政史の基本史料。",
      category: "decree",
      citationIds: ["ptebt-i-5", "lenger-cordptol", "holbl2001", "chauveau2000"],
      stateOfCountryJa:
        "内戦で疲弊した国土の再編期。エジプト人神官・在地エリートへの譲歩によって王権の社会的基盤が再構築され、後のクレオパトラ期へ続く「ハイブリッド」な支配様式が強化される。",
    },
    {
      id: "pviii-death-116",
      startYear: -116,
      placeId: "alexandria",
      title: "Death of Ptolemy VIII",
      titleJa: "プトレマイオス8世の死",
      summary:
        "Ptolemy VIII died in Alexandria, bequeathing the kingdom to Cleopatra III and whichever of his sons she chose; this set off the Ptolemy IX / Ptolemy X conflict.",
      summaryJa:
        "アレクサンドリアで死去。遺言によりクレオパトラ3世と、彼女が選んだ息子に王国を遺贈。これがプトレマイオス9世／10世の確執の起点となる。",
      category: "reign",
      citationIds: ["holbl2001", "whitehorne1994", "bennett-online"],
      stateOfCountryJa:
        "王朝は実質的に母系（クレオパトラ3世）主導へ移行。ローマの影響力はなお拡大傾向。",
    },
  ],
};
