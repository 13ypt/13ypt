// Deutsch Tutor · AI — ブラウザから Anthropic API を直叩き
// No framework, no bundler. ES module.

/* ============================================================
   Storage & State
   ============================================================ */
const KEY = {
  apiKey: "de-tutor:apikey",
  model:  "de-tutor:model",
  tutor:  "de-tutor:tutor-history",
  scen:   "de-tutor:scenario",
  level:  "de-tutor:level"
};

const state = {
  apiKey: localStorage.getItem(KEY.apiKey) || "",
  model:  localStorage.getItem(KEY.model)  || "claude-sonnet-4-6",
  tutor:  JSON.parse(localStorage.getItem(KEY.tutor) || "[]"),
  scenario: localStorage.getItem(KEY.scen)  || "alltag",
  level:    localStorage.getItem(KEY.level) || "B2"
};

function saveTutor() { localStorage.setItem(KEY.tutor, JSON.stringify(state.tutor)); }

/* ============================================================
   Markdown helpers
   ============================================================ */
function renderMd(text) {
  if (!text) return "";
  if (typeof marked === "undefined" || typeof DOMPurify === "undefined") {
    // Fallback: escape + preserve newlines
    return escapeHtml(text).replace(/\n/g, "<br>");
  }
  const html = marked.parse(text, { breaks: true, gfm: true });
  return DOMPurify.sanitize(html);
}
function escapeHtml(s) {
  return s.replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}

/* ============================================================
   Anthropic API (streaming)
   ============================================================ */
async function streamMessage({ system, messages, onDelta, model, maxTokens = 2048 }) {
  if (!state.apiKey) throw new Error("API キーが未設定です。右上の⚙から設定してください。");
  const body = {
    model: model || state.model,
    max_tokens: maxTokens,
    system,
    messages,
    stream: true
  };
  const res = await fetch("https://api.anthropic.com/v1/messages", {
    method: "POST",
    headers: {
      "content-type": "application/json",
      "x-api-key": state.apiKey,
      "anthropic-version": "2023-06-01",
      "anthropic-dangerous-direct-browser-access": "true"
    },
    body: JSON.stringify(body)
  });
  if (!res.ok) {
    const txt = await res.text();
    let msg = `API エラー ${res.status}`;
    try {
      const j = JSON.parse(txt);
      if (j.error?.message) msg += ` — ${j.error.message}`;
    } catch { msg += ` — ${txt.slice(0, 200)}`; }
    if (res.status === 401) msg += "\n\nAPI キーを確認してください。";
    throw new Error(msg);
  }
  const reader = res.body.getReader();
  const dec = new TextDecoder();
  let buf = "", full = "";
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buf += dec.decode(value, { stream: true });
    const parts = buf.split("\n\n");
    buf = parts.pop();
    for (const chunk of parts) {
      for (const line of chunk.split("\n")) {
        if (!line.startsWith("data: ")) continue;
        const payload = line.slice(6).trim();
        if (!payload || payload === "[DONE]") continue;
        try {
          const evt = JSON.parse(payload);
          if (evt.type === "content_block_delta" && evt.delta?.type === "text_delta") {
            full += evt.delta.text;
            onDelta?.(evt.delta.text, full);
          }
        } catch { /* ignore malformed chunks */ }
      }
    }
  }
  return full;
}

/* ============================================================
   System prompts
   ============================================================ */
const SCENARIOS = {
  alltag:     "Alltagsgespräch über ein beliebiges Thema (Wetter, Wochenende, Hobby, Reisen, Essen).",
  cafe:       "Du bist Bedienung in einem Berliner Café. Der Schüler ist Gast. Bestellung, Empfehlungen, Small Talk.",
  arzt:       "Du bist Hausärztin in Berlin. Der Schüler ist Patient. Beschwerden, Anamnese, Therapieempfehlung.",
  amt:        "Du bist Beamtin im Bürgeramt. Der Schüler will sich anmelden oder ein Formular ausfüllen.",
  uni:        "Du bist Doktormutter (FU Berlin), Sprechstunde. Der Schüler ist Doktorand. Fragen zur Dissertation, zum Methodenteil, zur Zeitplanung.",
  konferenz:  "Du bist Kollege nach einem Konferenzvortrag. Stelle kritische, höfliche Fragen zur Methodik und zum Quellenmaterial.",
  smalltalk:  "Du bist neuer Kollege am Institut. Kurzer, höflicher Small Talk in der Kaffeeküche.",
  debatte:    "Du debattierst ein aktuelles Thema (KI in der Wissenschaft, Klimapolitik, Open Access). Vertritt oft die Gegenposition, damit der Schüler argumentieren muss.",
  frei:       "Du wählst ein interessantes, B2+ geeignetes Thema und beginnst das Gespräch."
};

function tutorSystem(scenario, level) {
  return `Du bist "Frau Dr. Müller", eine strenge, geduldige, kompetente Deutschlehrerin an der Freien Universität Berlin.
Dein Schüler ist ein japanischer Akademiker (Postdoc in Ägyptologie) auf dem Niveau ${level}. Er will sein Deutsch ernsthaft verbessern.

# SZENARIO
${SCENARIOS[scenario] || SCENARIOS.alltag}

# ABLAUF — bei JEDER Schüler-Nachricht folge GENAU dieser Struktur, mit diesen Markdown-Überschriften:

## 💬 Antwort
Reagiere zuerst natürlich und inhaltlich auf den Schüler, im Szenario bleibend (1–2 Sätze). Schreibe auf dem Niveau ${level}.

## ✏️ Korrektur
Prüfe den Schüler-Text AKRIBISCH auf ALLE Fehler in:
- Grammatik (Kasus, Genus, Numerus, Tempus, Modus)
- Wortstellung (V2, Nebensatz, TeKaMoLo)
- Rektion (Verben + Präpositionen, feste Wendungen)
- Artikel, Deklination
- Rechtschreibung, Zeichensetzung
- Wortwahl, Idiomatik, Register

Für JEDEN Fehler — auch winzige — gib einen Block im Format:
- **❌** \`{falsche Stelle}\`
- **✅** \`{richtige Version}\`
- **💡** {kurze Erklärung auf Deutsch; bei komplexen Regeln ergänze Japanisch in Klammern}

ZUSÄTZLICH: Gib für grammatisch korrekte, aber unnatürliche Stellen einen Block:
- **🗣️ Natürlicher** \`{Schüler-Version}\` → \`{idiomatische Version}\` (kurze Erklärung)

Wenn wirklich kein Fehler vorliegt: schreibe "Keine Fehler — sehr schön! 🎉" UND gib dennoch mindestens einen 🗣️-Block, falls es stilistisch besser ginge.

## 🔁 Alternative Formulierungen
Gib DREI Umformulierungen des zentralen Schüler-Satzes in verschiedenen Registern:
- 🎓 **gehoben / akademisch**: …
- 💬 **neutral / Standard**: …
- 🤝 **umgangssprachlich**: …

## ❓ Weiterführende Frage
Stelle eine offene Frage im Szenario (1 Satz), die den Schüler zu mehr Sprachproduktion herausfordert.

# REGELN
- Antworte IMMER auf Deutsch (außer kurzen 💡-Erklärungen, die bei komplexen Regeln auch Japanisch sein dürfen).
- Wenn der Schüler auf Japanisch / Englisch schreibt: ermutige ihn freundlich ("Versuch es bitte auf Deutsch!") und gib dennoch die 🔁-Formulierungen als Muster auf Deutsch.
- Sei streng: Winke KEINE Fehler durch, auch nicht kleine Kommafehler.
- Sei motivierend: konkret loben, wenn etwas gut ist.
- Benutze sauberes Markdown. Keine HTML-Tags.`;
}

const KORREKTUR_SYSTEM = (level, tone) => `Du bist ein präziser Lektor für akademisches Deutsch. Du korrigierst Texte japanischer Autoren auf Zielniveau ${level} im Stil "${tone}".

# AUSGABE — gib GENAU diese Markdown-Struktur zurück:

## 🎯 Korrigierte Fassung
Der vollständige Text, sprachlich geglättet, idiomatisch, im gewünschten Stil. Absätze klar trennen. Aussageabsicht bewahren.

## 📋 Änderungen im Detail
Eine Markdown-Tabelle mit ALLEN Änderungen (auch Kommas, Artikel, Präpositionen). Nichts übersehen.

| # | Original | Verbessert | Grund |
|---|---|---|---|
| 1 | … | … | kurze Erklärung auf Deutsch (bei komplexen Regeln + Japanisch) |

## 🔁 Stilvarianten
Schreibe den Text in DREI Registern KOMPLETT UM:

### 🎓 Gehoben / akademisch
Nominalstil, Passiv, Partizipialkonstruktionen, Konnektoren wie "infolgedessen", "hinsichtlich", "im Zuge".

### 💬 Neutral / klar
Standard-Schriftdeutsch, gemischt aktiv/passiv, präzise.

### ⚡ Prägnant
Kurz, aktiv, direkt. Keine Nominalisierungen. Maximal 15 Wörter pro Satz.

## 💡 Stil-Tipps
Max. 5 Bulletpoints zu wiederkehrenden Mustern (z. B. "Tendenz zu Nominalstil, der hier vermieden werden sollte"), auf Deutsch, bei Bedarf kurz Japanisch.

# REGELN
- Niemals Aussage verfälschen.
- Bei Unklarheit mehrere Optionen anbieten, aber eine Hauptfassung wählen.
- Sauberes Markdown, keine HTML-Tags.`;

const WORTSCHATZ_SYSTEM = `Du bist C1/C2-Deutschlehrer für einen japanischen Akademiker. Erkläre den angefragten Ausdruck gründlich.

# AUSGABE — Markdown mit dieser Struktur:

## {Wort / Ausdruck}

**Bedeutung** (DE): …
**和訳**: …
**Register**: neutral / gehoben / umgangssprachlich / fachsprachlich
**Form**: Wortart, bei Nomen: Artikel + Genitiv-Endung + Plural, bei Verben: 3 Stammformen + Hilfsverb + Rektion, bei Präpositionen: Kasus

### 🧩 Typische Kollokationen
Mindestens 5 typische Verbindungen (Verb+Nomen, Adj+Nomen, feste Phrasen).

### 📝 Beispielsätze
- **B2**: …
- **C1**: … (idiomatisch, etwas komplex)
- **C2**: … (akademisch / literarisch / Presse)

### 🔁 Synonyme mit Nuancen
- **{Syn1}** — wann verwendet man es? Unterschied zum Zielwort.
- **{Syn2}** — …
- **{Syn3}** — …
Mindestens 3 Synonyme mit klarer Nuancenbeschreibung.

### ⚠️ Häufige Fehler
- Typische Falschverwendungen, besonders durch Japaner.
- Verwechslungsrisiko mit ähnlichen Wörtern (mit kurzer Abgrenzung).

### 🇯🇵 Auf Japanisch
Ein kurzer japanischer Absatz (3–5 Sätze): Kernbedeutung, typischer Kontext, wichtigster Lernpunkt.

# REGELN
- Wenn der Eintrag ein Verb ist: Rektion (z. B. "sich auseinandersetzen mit + Dativ") immer angeben.
- Sauberes Markdown, keine HTML-Tags.`;

const UEBUNGEN_SYSTEM = (topic, type, level, count) => `Du erstellst maßgeschneiderte Deutschübungen für einen japanischen Lerner.
THEMA: ${topic}
TYP: ${type}
ZIELNIVEAU: ${level}
ANZAHL: ${count}

# AUSGABE — Markdown:

## 📝 Aufgaben
${count} nummerierte Aufgaben, nach Schwierigkeit aufsteigend. Authentisch formuliert (Alltag, Presse, Wissenschaft).
- Bei Lückentext: Lücke mit \`___\` markieren, ggf. Infinitiv in Klammern.
- Bei Übersetzung: den japanischen Satz zuerst.
- Bei Fehlersuche: je ein oder zwei Fehler pro Satz, markiert "Finde und korrigiere".
- Bei Leseverstehen: einen kurzen authentischen Text + 3-5 Fragen.

---

## ✅ Lösungen & Erklärungen
Für JEDE Aufgabe die Nummer + Lösung + eine 1-2 Zeilen Erklärung (Deutsch; bei komplexen Regeln zusätzlich kurz Japanisch).

# REGELN
- Verwende für das Niveau angemessene Wörter (keine Anfänger-Vokabeln bei C1/C2).
- Sauberes Markdown, keine HTML-Tags.`;

/* ============================================================
   UI: Tabs
   ============================================================ */
const tabs = document.querySelectorAll("#tabs button");
const panels = document.querySelectorAll(".panel");
tabs.forEach(btn => btn.addEventListener("click", () => switchTab(btn.dataset.tab)));
function switchTab(id) {
  tabs.forEach(b => b.classList.toggle("active", b.dataset.tab === id));
  panels.forEach(p => p.classList.toggle("active", p.id === id));
}

/* ============================================================
   UI: Settings modal & onboarding
   ============================================================ */
const onboarding = document.getElementById("onboarding");
const mainPanels = ["tutor", "korrektur", "wortschatz", "uebungen"];

function ensureApiKey() {
  if (!state.apiKey) {
    mainPanels.forEach(id => document.getElementById(id).classList.remove("active"));
    document.querySelectorAll("#tabs button").forEach(b => b.classList.remove("active"));
    onboarding.classList.remove("hidden");
    onboarding.classList.add("active");
    return false;
  }
  onboarding.classList.add("hidden");
  onboarding.classList.remove("active");
  return true;
}

document.getElementById("save-key").addEventListener("click", () => {
  const key = document.getElementById("apikey-input").value.trim();
  const model = document.getElementById("model-input").value;
  if (!key.startsWith("sk-ant-")) {
    alert("API キーは通常 'sk-ant-' で始まります。正しいキーを入力してください。");
    return;
  }
  state.apiKey = key;
  state.model = model;
  localStorage.setItem(KEY.apiKey, key);
  localStorage.setItem(KEY.model, model);
  onboarding.classList.add("hidden");
  onboarding.classList.remove("active");
  switchTab("tutor");
  renderTutorChat();
});

const settingsModal = document.getElementById("settings-modal");
document.getElementById("settings-btn").addEventListener("click", () => {
  document.getElementById("set-apikey").value = state.apiKey;
  document.getElementById("set-model").value = state.model;
  settingsModal.classList.remove("hidden");
});
document.getElementById("settings-close").addEventListener("click", () => settingsModal.classList.add("hidden"));
document.getElementById("set-save").addEventListener("click", () => {
  const key = document.getElementById("set-apikey").value.trim();
  const model = document.getElementById("set-model").value;
  if (key && !key.startsWith("sk-ant-")) {
    alert("API キーは 'sk-ant-' で始まります。");
    return;
  }
  state.apiKey = key;
  state.model = model;
  localStorage.setItem(KEY.apiKey, key);
  localStorage.setItem(KEY.model, model);
  settingsModal.classList.add("hidden");
  if (!ensureApiKey()) return;
});
document.getElementById("set-clear").addEventListener("click", () => {
  if (!confirm("保存した API キーと会話ログを全て削除します。よろしいですか？")) return;
  Object.values(KEY).forEach(k => localStorage.removeItem(k));
  state.apiKey = ""; state.tutor = [];
  renderTutorChat();
  settingsModal.classList.add("hidden");
  ensureApiKey();
});

/* ============================================================
   Tutor (chat)
   ============================================================ */
const tutorChat    = document.getElementById("tutor-chat");
const tutorForm    = document.getElementById("tutor-form");
const tutorInput   = document.getElementById("tutor-input");
const tutorSend    = document.getElementById("tutor-send");
const tutorScenario = document.getElementById("tutor-scenario");
const tutorLevel    = document.getElementById("tutor-level");
const tutorNew      = document.getElementById("tutor-new");

tutorScenario.value = state.scenario;
tutorLevel.value    = state.level;
tutorScenario.addEventListener("change", () => { state.scenario = tutorScenario.value; localStorage.setItem(KEY.scen, state.scenario); });
tutorLevel.addEventListener("change",    () => { state.level    = tutorLevel.value;    localStorage.setItem(KEY.level, state.level); });

tutorNew.addEventListener("click", () => {
  if (!confirm("現在の会話履歴を削除して、新しい会話を始めますか？")) return;
  state.tutor = [];
  saveTutor();
  renderTutorChat();
});

function renderTutorChat() {
  tutorChat.innerHTML = "";
  if (state.tutor.length === 0) {
    const greeting = document.createElement("div");
    greeting.className = "msg ai";
    greeting.innerHTML = `<div class="avatar">M</div><div class="bubble">Hallo! Ich bin Frau Dr. Müller. Schreib mir einfach auf Deutsch — ich korrigiere jedes Detail und gebe dir Umformulierungen. Dein Szenario: <b>${escapeHtml(tutorScenario.options[tutorScenario.selectedIndex].text)}</b>. Bereit? 🇩🇪</div>`;
    tutorChat.appendChild(greeting);
    return;
  }
  for (const m of state.tutor) addBubble(m.role, m.content, false);
  tutorChat.scrollTop = tutorChat.scrollHeight;
}
function addBubble(role, content, typing = false) {
  const div = document.createElement("div");
  div.className = `msg ${role === "user" ? "user" : "ai"}`;
  const avatar = role === "user" ? "DU" : "M";
  const bubble = document.createElement("div");
  bubble.className = "bubble" + (typing ? " typing" : "");
  if (role === "user") bubble.textContent = content;
  else bubble.innerHTML = renderMd(content);
  div.innerHTML = `<div class="avatar">${avatar}</div>`;
  div.appendChild(bubble);
  tutorChat.appendChild(div);
  tutorChat.scrollTop = tutorChat.scrollHeight;
  return bubble;
}

tutorInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    tutorForm.requestSubmit();
  }
});

tutorForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  if (!ensureApiKey()) return;
  const text = tutorInput.value.trim();
  if (!text) return;
  tutorInput.value = "";
  state.tutor.push({ role: "user", content: text });
  addBubble("user", text);
  saveTutor();

  const aiBubble = addBubble("ai", "", true);
  tutorSend.disabled = true;
  try {
    const system = tutorSystem(state.scenario, state.level);
    const full = await streamMessage({
      system,
      messages: state.tutor,
      onDelta: (_d, full) => { aiBubble.innerHTML = renderMd(full); tutorChat.scrollTop = tutorChat.scrollHeight; },
      maxTokens: 2048
    });
    aiBubble.classList.remove("typing");
    aiBubble.innerHTML = renderMd(full);
    state.tutor.push({ role: "assistant", content: full });
    saveTutor();
  } catch (err) {
    aiBubble.classList.remove("typing");
    aiBubble.innerHTML = `<div class="error-banner">⚠️ ${escapeHtml(err.message)}</div>`;
    state.tutor.pop(); // undo user message pairing so retry works
    saveTutor();
  } finally {
    tutorSend.disabled = false;
  }
});

/* ============================================================
   Korrektur
   ============================================================ */
const korrInput  = document.getElementById("korr-input");
const korrLevel  = document.getElementById("korr-level");
const korrTone   = document.getElementById("korr-tone");
const korrOut    = document.getElementById("korr-output");
const korrSubmit = document.getElementById("korr-submit");

korrSubmit.addEventListener("click", async () => {
  if (!ensureApiKey()) return;
  const txt = korrInput.value.trim();
  if (!txt) { alert("テキストを入力してください。"); return; }
  korrOut.classList.remove("hidden");
  korrOut.innerHTML = '<p class="hint">生成中 …</p>';
  korrSubmit.disabled = true;
  try {
    const system = KORREKTUR_SYSTEM(korrLevel.value, korrTone.value);
    const full = await streamMessage({
      system,
      messages: [{ role: "user", content: txt }],
      onDelta: (_d, full) => { korrOut.innerHTML = renderMd(full); },
      maxTokens: 4096
    });
    korrOut.innerHTML = renderMd(full);
  } catch (err) {
    korrOut.innerHTML = `<div class="error-banner">⚠️ ${escapeHtml(err.message)}</div>`;
  } finally {
    korrSubmit.disabled = false;
  }
});

/* ============================================================
   Wortschatz
   ============================================================ */
const wortForm = document.getElementById("wort-form");
const wortInput = document.getElementById("wort-input");
const wortOut   = document.getElementById("wort-output");

document.querySelectorAll("#wort-chips .chip").forEach(c => c.addEventListener("click", () => {
  wortInput.value = c.dataset.w;
  wortForm.requestSubmit();
}));

wortForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  if (!ensureApiKey()) return;
  const w = wortInput.value.trim();
  if (!w) return;
  wortOut.classList.remove("hidden");
  wortOut.innerHTML = '<p class="hint">解説生成中 …</p>';
  try {
    const full = await streamMessage({
      system: WORTSCHATZ_SYSTEM,
      messages: [{ role: "user", content: w }],
      onDelta: (_d, full) => { wortOut.innerHTML = renderMd(full); },
      maxTokens: 2048
    });
    wortOut.innerHTML = renderMd(full);
  } catch (err) {
    wortOut.innerHTML = `<div class="error-banner">⚠️ ${escapeHtml(err.message)}</div>`;
  }
});

/* ============================================================
   Übungen
   ============================================================ */
const uebSubmit = document.getElementById("ueb-submit");
const uebOut    = document.getElementById("ueb-output");

uebSubmit.addEventListener("click", async () => {
  if (!ensureApiKey()) return;
  const topic = document.getElementById("ueb-topic").value;
  const type  = document.getElementById("ueb-type").value;
  const level = document.getElementById("ueb-level").value;
  const count = document.getElementById("ueb-count").value;

  uebOut.classList.remove("hidden");
  uebOut.innerHTML = '<p class="hint">問題生成中 …</p>';
  uebSubmit.disabled = true;
  try {
    const full = await streamMessage({
      system: UEBUNGEN_SYSTEM(topic, type, level, count),
      messages: [{ role: "user", content: `Bitte generiere ${count} Aufgaben zum Thema "${topic}" im Format "${type}" für Niveau ${level}.` }],
      onDelta: (_d, full) => { uebOut.innerHTML = renderMd(full); },
      maxTokens: 3072
    });
    uebOut.innerHTML = renderMd(full);
  } catch (err) {
    uebOut.innerHTML = `<div class="error-banner">⚠️ ${escapeHtml(err.message)}</div>`;
  } finally {
    uebSubmit.disabled = false;
  }
});

/* ============================================================
   Init
   ============================================================ */
if (ensureApiKey()) {
  renderTutorChat();
} else {
  // Show onboarding (already handled by ensureApiKey)
}
