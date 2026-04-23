/* Ptolemaic Timeline Visualiser
 * Vanilla JS SVG renderer. Data loaded from ./data/*.json. */

(() => {
  const SVG_NS = "http://www.w3.org/2000/svg";
  const YEAR_MIN = -365;
  const YEAR_MAX = -25;
  const DEFAULT_PX_PER_YEAR = 4;
  const ROW_HEIGHT = 26;
  const KING_ROW_GAP = 4;
  const AXIS_HEIGHT = 28;
  const TOP_PAD = 8;
  const LEFT_PAD = 30;
  const RIGHT_PAD = 30;

  const state = {
    pxPerYear: DEFAULT_PX_PER_YEAR,
    lang: "ja", // or "en"
    view: "timeline", // "timeline" | "king"
    selectedKing: null,
    filters: { kings: true, events: true, apis: true, buchis: true, queens: true },
    data: { kings: [], events: [], apis: [], buchis: [] },
  };

  // ---------- utilities ----------
  const el = (tag, attrs = {}, children = []) => {
    const node = tag.includes(":") || ["svg","g","rect","circle","line","text","path","defs","pattern","polygon","use"].includes(tag)
      ? document.createElementNS(SVG_NS, tag)
      : document.createElement(tag);
    for (const [k, v] of Object.entries(attrs)) {
      if (k === "class") node.setAttribute("class", v);
      else if (k === "text") node.textContent = v;
      else if (k.startsWith("on") && typeof v === "function") node.addEventListener(k.slice(2), v);
      else if (v !== undefined && v !== null) node.setAttribute(k, v);
    }
    (Array.isArray(children) ? children : [children]).forEach(c => {
      if (c == null) return;
      node.appendChild(typeof c === "string" ? document.createTextNode(c) : c);
    });
    return node;
  };

  const fmtYear = (y) => {
    if (y == null) return "—";
    if (y < 0) return `${-y} BCE`;
    return `${y} CE`;
  };

  const fmtRange = (a, b) => `${-a}–${-b} BCE`;

  const xOf = (year) => LEFT_PAD + (year - YEAR_MIN) * state.pxPerYear;

  // ---------- data loading ----------
  async function loadData() {
    const [kings, events, apis, buchis] = await Promise.all([
      fetch("data/kings.json").then(r => r.json()),
      fetch("data/events.json").then(r => r.json()),
      fetch("data/apis.json").then(r => r.json()),
      fetch("data/buchis.json").then(r => r.json()),
    ]);
    state.data = { kings, events, apis, buchis };
  }

  // ---------- layout ----------
  // Assign kings to rows so overlapping reigns stack (coregencies).
  function assignRows(items, getStart, getEnd) {
    const rows = []; // each row holds last-end
    const result = new Map();
    const sorted = [...items].sort((a, b) => getStart(a) - getStart(b));
    for (const it of sorted) {
      let placed = -1;
      for (let i = 0; i < rows.length; i++) {
        if (rows[i] <= getStart(it)) { placed = i; break; }
      }
      if (placed === -1) { rows.push(getEnd(it)); placed = rows.length - 1; }
      else rows[placed] = getEnd(it);
      result.set(it, placed);
    }
    return { rows: rows.length, map: result };
  }

  // ---------- tooltip ----------
  const tooltip = document.createElement("div");
  tooltip.className = "tooltip";
  document.body.appendChild(tooltip);

  function showTooltip(evt, html) {
    tooltip.innerHTML = html;
    tooltip.classList.add("visible");
    moveTooltip(evt);
  }
  function moveTooltip(evt) {
    const pad = 14;
    let x = evt.clientX + pad;
    let y = evt.clientY + pad;
    const rect = tooltip.getBoundingClientRect();
    if (x + rect.width > window.innerWidth - 8) x = evt.clientX - rect.width - pad;
    if (y + rect.height > window.innerHeight - 8) y = evt.clientY - rect.height - pad;
    tooltip.style.left = `${x}px`;
    tooltip.style.top = `${y}px`;
  }
  function hideTooltip() { tooltip.classList.remove("visible"); }

  // ---------- header / sidebar ----------
  function renderHeader() {
    const header = document.getElementById("site-header");
    header.innerHTML = "";
    header.appendChild(el("h1", { class: "site-title" }, [
      "Ptolemaic Timeline",
      el("small", {}, state.lang === "ja"
        ? "プトレマイオス朝の治世・政治・動物崇拝 可視化"
        : "Reigns, politics and animal cults of Ptolemaic Egypt"),
    ]));
    const nav = el("nav", { class: "site-nav" });
    const tlBtn = el("button", { class: "btn" + (state.view === "timeline" ? " active" : ""), onclick: () => { state.view = "timeline"; state.selectedKing = null; render(); } }, state.lang === "ja" ? "全員タイムライン" : "Full timeline");
    const langBtn = el("button", { class: "btn", onclick: () => { state.lang = state.lang === "ja" ? "en" : "ja"; render(); } }, state.lang === "ja" ? "EN" : "日本語");
    nav.append(tlBtn, langBtn);
    header.appendChild(nav);
  }

  function renderSidebar() {
    const side = document.getElementById("sidebar");
    side.innerHTML = "";

    // Filters
    side.appendChild(el("h3", {}, state.lang === "ja" ? "表示レイヤー" : "Layers"));
    const filterRows = [
      ["kings",  state.lang === "ja" ? "王（男王）" : "Kings",           "var(--king)"],
      ["queens", state.lang === "ja" ? "女王" : "Queens",                "var(--king-queen)"],
      ["events", state.lang === "ja" ? "政治的出来事" : "Political events","var(--event-political)"],
      ["apis",   state.lang === "ja" ? "アピス牛" : "Apis bulls",        "var(--apis)"],
      ["buchis", state.lang === "ja" ? "ブキス牛" : "Buchis bulls",      "var(--buchis)"],
    ];
    for (const [key, label, color] of filterRows) {
      const row = el("label", { class: "filter-row" });
      const cb = el("input", { type: "checkbox" });
      cb.checked = state.filters[key];
      cb.addEventListener("change", () => { state.filters[key] = cb.checked; render(); });
      row.append(cb, el("span", { class: "swatch", style: `background:${color}` }), document.createTextNode(label));
      side.appendChild(row);
    }

    side.appendChild(el("h3", {}, state.lang === "ja" ? "王一覧（クリック）" : "Kings (click)"));
    const list = el("div", { class: "king-list" });
    for (const k of state.data.kings) {
      const btn = el("button", {
        class: state.selectedKing === k.id ? "active" : "",
        onclick: () => { state.selectedKing = k.id; state.view = "king"; render(); }
      });
      const name = state.lang === "ja" ? k.nameJa : k.name;
      btn.appendChild(document.createTextNode(name));
      btn.appendChild(el("span", { class: "king-dates" }, fmtRange(k.start, k.end)));
      list.appendChild(btn);
    }
    side.appendChild(list);
  }

  // ---------- main timeline ----------
  function renderTimeline() {
    const vp = document.getElementById("viewport");
    vp.innerHTML = "";

    const controls = el("div", { class: "timeline-controls" });
    const zoomLabel = el("label", {}, state.lang === "ja" ? "ズーム" : "Zoom");
    const zoomIn = el("button", { class: "btn", onclick: () => { state.pxPerYear = Math.min(12, state.pxPerYear + 1); render(); } }, "+");
    const zoomOut = el("button", { class: "btn", onclick: () => { state.pxPerYear = Math.max(2, state.pxPerYear - 1); render(); } }, "−");
    const zoomReset = el("button", { class: "btn", onclick: () => { state.pxPerYear = DEFAULT_PX_PER_YEAR; render(); } }, state.lang === "ja" ? "リセット" : "Reset");
    controls.append(zoomLabel, zoomOut, zoomIn, zoomReset);
    vp.appendChild(controls);

    const wrap = el("div", { class: "timeline-wrap" });
    vp.appendChild(wrap);

    // Separate male kings vs queens (draw them on different row-stacks)
    const maleKings = state.data.kings.filter(k => !k.isQueen);
    const queens = state.data.kings.filter(k => k.isQueen);

    const mLayout = assignRows(maleKings, k => k.start, k => k.end);
    const qLayout = assignRows(queens, k => k.start, k => k.end);

    const kingsRowCount = state.filters.kings ? mLayout.rows : 0;
    const queensRowCount = state.filters.queens ? qLayout.rows : 0;
    const apisRowCount = state.filters.apis ? 1 : 0;
    const buchisRowCount = state.filters.buchis ? 1 : 0;
    const eventRowCount = state.filters.events ? 1 : 0;

    const kingsY = TOP_PAD;
    const queensY = kingsY + kingsRowCount * (ROW_HEIGHT + KING_ROW_GAP) + (kingsRowCount ? 8 : 0);
    const apisY = queensY + queensRowCount * (ROW_HEIGHT + KING_ROW_GAP) + (queensRowCount ? 8 : 0);
    const buchisY = apisY + apisRowCount * (ROW_HEIGHT + 6) + (apisRowCount ? 8 : 0);
    const eventsY = buchisY + buchisRowCount * (ROW_HEIGHT + 6) + (buchisRowCount ? 14 : 0);
    const axisY = eventsY + eventRowCount * 40 + 10;
    const totalH = axisY + AXIS_HEIGHT + 10;

    const totalW = LEFT_PAD + (YEAR_MAX - YEAR_MIN) * state.pxPerYear + RIGHT_PAD;
    const svg = el("svg", {
      class: "timeline-svg",
      width: totalW,
      height: totalH,
      viewBox: `0 0 ${totalW} ${totalH}`,
    });

    // Defs: hatched pattern for coregency / interruption
    const defs = el("defs");
    const pat = el("pattern", { id: "hatch", patternUnits: "userSpaceOnUse", width: 6, height: 6, patternTransform: "rotate(45)" });
    pat.appendChild(el("rect", { width: 6, height: 6, fill: "transparent" }));
    pat.appendChild(el("line", { x1: 0, y: 0, y1: 0, x2: 0, y2: 6, stroke: "rgba(255,255,255,0.35)", "stroke-width": 2 }));
    defs.appendChild(pat);
    svg.appendChild(defs);

    // Background lanes
    const laneBg = (y, h, label) => {
      svg.appendChild(el("rect", { x: 0, y, width: totalW, height: h, fill: "rgba(255,255,255,0.015)" }));
      svg.appendChild(el("text", { x: 4, y: y + 12, fill: "rgba(180,165,140,0.4)", "font-size": 10, "font-family": "var(--font-en)" }, label));
    };
    if (kingsRowCount) laneBg(kingsY - 2, kingsRowCount * (ROW_HEIGHT + KING_ROW_GAP), "KINGS");
    if (queensRowCount) laneBg(queensY - 2, queensRowCount * (ROW_HEIGHT + KING_ROW_GAP), "QUEENS");
    if (apisRowCount) laneBg(apisY - 2, ROW_HEIGHT + 6, "APIS");
    if (buchisRowCount) laneBg(buchisY - 2, ROW_HEIGHT + 6, "BUCHIS");

    // Kings (male)
    if (state.filters.kings) {
      for (const k of maleKings) {
        const row = mLayout.map.get(k);
        const y = kingsY + row * (ROW_HEIGHT + KING_ROW_GAP);
        drawKingBar(svg, k, y);
      }
    }

    // Queens
    if (state.filters.queens) {
      for (const k of queens) {
        const row = qLayout.map.get(k);
        const y = queensY + row * (ROW_HEIGHT + KING_ROW_GAP);
        drawKingBar(svg, k, y);
      }
    }

    // Apis
    if (state.filters.apis) {
      for (const a of state.data.apis) drawBull(svg, a, apisY, "var(--apis)", "Apis");
    }
    // Buchis
    if (state.filters.buchis) {
      for (const b of state.data.buchis) drawBull(svg, b, buchisY, "var(--buchis)", "Buchis");
    }

    // Events
    if (state.filters.events) {
      for (const ev of state.data.events) drawEvent(svg, ev, eventsY);
    }

    // Axis
    drawAxis(svg, axisY);

    wrap.appendChild(svg);

    // Legend
    vp.appendChild(renderLegend());
  }

  function drawKingBar(svg, k, y) {
    const x1 = xOf(k.start);
    const x2 = xOf(k.end);
    const w = Math.max(2, x2 - x1);
    const color = k.color || "var(--king)";
    const g = el("g", { class: "king-bar", onclick: () => { state.selectedKing = k.id; state.view = "king"; render(); } });

    // Main reign rectangle
    g.appendChild(el("rect", { x: x1, y, width: w, height: ROW_HEIGHT, rx: 3, ry: 3, fill: color, "fill-opacity": 0.85, stroke: color, "stroke-width": 1 }));

    // Coregency / interruption
    if (k.coregencyStart && k.soloFrom) {
      const cx1 = xOf(k.coregencyStart);
      const cx2 = xOf(k.soloFrom);
      if (cx2 > cx1) {
        g.appendChild(el("rect", { x: cx1, y, width: cx2 - cx1, height: ROW_HEIGHT, rx: 3, ry: 3, fill: "url(#hatch)" }));
      }
    }
    if (k.interruption) {
      for (const int of k.interruption) {
        const ix1 = xOf(int.from);
        const ix2 = xOf(int.to);
        g.appendChild(el("rect", { x: ix1, y: y + 3, width: ix2 - ix1, height: ROW_HEIGHT - 6, fill: "rgba(0,0,0,0.55)", stroke: color, "stroke-width": 1, "stroke-dasharray": "2,2" }));
      }
    }

    // Label
    if (w > 45) {
      const label = (state.lang === "ja" ? k.nameJa : `Ptolemy ${k.number}`);
      const short = label.length * 7 > w ? `${k.number}` : label;
      g.appendChild(el("text", { class: "king-label", x: x1 + 6, y: y + ROW_HEIGHT / 2 + 4 }, short));
    }

    g.addEventListener("mouseenter", (e) => {
      const name = state.lang === "ja" ? k.nameJa : k.name;
      showTooltip(e, `<div class="tt-title">${name}</div>
        <div class="tt-meta">${fmtRange(k.start, k.end)} · ${k.epithet || ""}</div>
        <div>${state.lang === "ja" ? k.summary : (k.summaryEn || k.summary)}</div>
        ${k.source ? `<div class="tt-src">${k.source}</div>` : ""}`);
    });
    g.addEventListener("mousemove", moveTooltip);
    g.addEventListener("mouseleave", hideTooltip);

    svg.appendChild(g);
  }

  function drawBull(svg, b, y, color, kind) {
    if (b.birth == null && b.death == null) return; // nothing plottable
    const g = el("g", { class: "bull-bar" });
    // life bar (only if both ends known)
    if (b.birth != null && b.death != null) {
      const x1 = xOf(b.birth);
      const x2 = xOf(b.death);
      g.appendChild(el("rect", { x: x1, y: y + 6, width: Math.max(2, x2 - x1), height: ROW_HEIGHT - 12, rx: 2, ry: 2, fill: color, "fill-opacity": 0.55, stroke: color, "stroke-width": 1 }));
    }
    // installation marker
    if (b.installed != null) {
      const ix = xOf(b.installed);
      g.appendChild(el("line", { x1: ix, y1: y + 3, x2: ix, y2: y + ROW_HEIGHT - 3, stroke: "#fff", "stroke-width": 1.5 }));
    }
    // death marker
    if (b.death != null) {
      g.appendChild(el("circle", { cx: xOf(b.death), cy: y + ROW_HEIGHT / 2, r: 3.5, fill: color, stroke: "#fff", "stroke-width": 1 }));
    }
    // birth-only edge case (bull known only from birth inscription)
    if (b.birth != null && b.death == null) {
      g.appendChild(el("circle", { cx: xOf(b.birth), cy: y + ROW_HEIGHT / 2, r: 3.5, fill: "none", stroke: color, "stroke-width": 1.5 }));
    }

    g.addEventListener("mouseenter", (e) => {
      const name = state.lang === "ja" ? b.name : (b.nameEn || b.name);
      const title = b.stela ? `${kind} [${b.stela}]: ${name}` : `${kind}: ${name}`;
      const installedTxt = b.installed != null
        ? ` · ${state.lang === "ja" ? "即位" : "installed"} ${fmtYear(b.installed)}`
        : ` · ${state.lang === "ja" ? "即位年不詳" : "install not recorded"}`;
      showTooltip(e, `<div class="tt-title">${title}</div>
        <div class="tt-meta">${state.lang === "ja" ? "生" : "born"} ${fmtYear(b.birth)}${installedTxt} · ${state.lang === "ja" ? "没" : "died"} ${fmtYear(b.death)}</div>
        ${b.note ? `<div>${b.note}</div>` : ""}
        ${b.source ? `<div class="tt-src">${b.source}</div>` : ""}`);
    });
    g.addEventListener("mousemove", moveTooltip);
    g.addEventListener("mouseleave", hideTooltip);
    svg.appendChild(g);
  }

  function drawEvent(svg, ev, y) {
    const x = xOf(ev.year);
    const color = `var(--event-${ev.category})`;
    const g = el("g", { class: "event-marker" });
    g.appendChild(el("line", { x1: x, y1: y - 4, x2: x, y2: y + 14, stroke: color, "stroke-width": 1 }));
    g.appendChild(el("circle", { cx: x, cy: y + 6, r: 5, fill: color }));
    g.addEventListener("mouseenter", (e) => {
      const title = state.lang === "ja" ? ev.title : (ev.titleEn || ev.title);
      showTooltip(e, `<div class="tt-title">${fmtYear(ev.year)} · ${title}</div>
        ${ev.note ? `<div>${ev.note}</div>` : ""}
        ${ev.source ? `<div class="tt-src">${ev.source}</div>` : ""}`);
    });
    g.addEventListener("mousemove", moveTooltip);
    g.addEventListener("mouseleave", hideTooltip);
    svg.appendChild(g);
  }

  function drawAxis(svg, y) {
    const axis = el("g", { class: "axis" });
    axis.appendChild(el("line", { x1: LEFT_PAD, y1: y, x2: xOf(YEAR_MAX), y2: y, stroke: "var(--fg-muted)", "stroke-width": 1 }));
    for (let yr = Math.ceil(YEAR_MIN / 25) * 25; yr <= YEAR_MAX; yr += 25) {
      const x = xOf(yr);
      const isMajor = yr % 50 === 0;
      axis.appendChild(el("line", { x1: x, y1: y, x2: x, y2: y + (isMajor ? 8 : 5), stroke: "var(--fg-muted)", "stroke-width": 1, class: isMajor ? "tick-major" : "" }));
      if (isMajor) {
        axis.appendChild(el("text", { x, y: y + 22, "text-anchor": "middle" }, `${-yr}`));
      }
    }
    axis.appendChild(el("text", { x: xOf(YEAR_MAX) - 2, y: y + 22, "text-anchor": "end", fill: "var(--fg-muted)" }, "BCE"));
    svg.appendChild(axis);
  }

  function renderLegend() {
    const legend = el("div", { class: "legend" });
    const items = [
      ["var(--king)", state.lang === "ja" ? "王（実線）" : "King (solid)"],
      ["url(#none)", state.lang === "ja" ? "共同統治（斜線）" : "Coregency (hatched)"],
      ["var(--king-queen)", state.lang === "ja" ? "女王" : "Queen"],
      ["var(--apis)", state.lang === "ja" ? "アピス牛（│＝即位、●＝没）" : "Apis (│ = installed, ● = death)"],
      ["var(--buchis)", state.lang === "ja" ? "ブキス牛" : "Buchis"],
      ["var(--event-military)", state.lang === "ja" ? "軍事" : "Military"],
      ["var(--event-political)", state.lang === "ja" ? "政治" : "Political"],
      ["var(--event-religious)", state.lang === "ja" ? "宗教／勅令" : "Religious / decree"],
      ["var(--event-revolt)", state.lang === "ja" ? "反乱・内戦" : "Revolt / civil war"],
    ];
    for (const [color, label] of items) {
      legend.appendChild(el("span", { class: "legend-item" }, [
        el("span", { class: "swatch", style: `background:${color}` }),
        document.createTextNode(label),
      ]));
    }
    return legend;
  }

  // ---------- king detail view ----------
  function renderKingDetail() {
    const vp = document.getElementById("viewport");
    vp.innerHTML = "";
    const k = state.data.kings.find(x => x.id === state.selectedKing);
    if (!k) { vp.appendChild(el("p", {}, "Select a king from the sidebar.")); return; }

    const container = el("div", { class: "detail-view" });

    container.appendChild(el("h1", {}, k.name));
    container.appendChild(el("div", { class: "king-ja" }, k.nameJa));
    const meta = el("div", { class: "king-meta" });
    meta.append(
      document.createTextNode(`${state.lang === "ja" ? "治世" : "Reign"}: ${fmtRange(k.start, k.end)}`),
      el("br"),
      document.createTextNode(`${state.lang === "ja" ? "称号" : "Epithet"}: ${state.lang === "ja" ? (k.epithetJa || k.epithet) : k.epithet}`),
    );
    if (k.satrapFrom) {
      meta.append(el("br"), document.createTextNode(`${state.lang === "ja" ? "サトラップ就任" : "Satrap from"}: ${fmtYear(k.satrapFrom)}`));
    }
    container.appendChild(meta);

    // Summary
    container.appendChild(el("h2", {}, state.lang === "ja" ? "概要" : "Overview"));
    container.appendChild(el("p", {}, state.lang === "ja" ? k.summary : (k.summaryEn || k.summary)));
    if (k.source) container.appendChild(el("p", { class: "src" }, `Source: ${k.source}`));

    // Mini timeline for this king: events + Apis/Buchis overlapping reign
    const contextStart = Math.min(k.start, k.satrapFrom || k.start) - 2;
    const contextEnd = k.end + 2;
    container.appendChild(el("h2", {}, state.lang === "ja" ? "治世内タイムライン" : "Reign timeline"));
    container.appendChild(renderMiniTimeline(k, contextStart, contextEnd));

    // Events during reign
    const relEvents = state.data.events.filter(e => e.year >= k.start - 1 && e.year <= k.end + 1);
    if (relEvents.length) {
      container.appendChild(el("h2", {}, state.lang === "ja" ? "治世中の主要な出来事" : "Major events during reign"));
      const ul = el("ul");
      for (const ev of relEvents) {
        const li = el("li");
        li.appendChild(el("span", { class: `tag tag-${ev.category}` }, ev.category));
        li.appendChild(document.createTextNode(`${fmtYear(ev.year)} — ${state.lang === "ja" ? ev.title : (ev.titleEn || ev.title)}`));
        if (ev.note) li.appendChild(el("div", {}, ev.note));
        if (ev.source) li.appendChild(el("span", { class: "src" }, ev.source));
        ul.appendChild(li);
      }
      container.appendChild(ul);
    }

    // Apis overlapping reign (handle entries with partial dates)
    const overlapsReign = (a) => {
      const start = a.birth != null ? a.birth : a.death;
      const end = a.death != null ? a.death : a.birth;
      if (start == null || end == null) return false;
      return end >= k.start && start <= k.end;
    };
    const relApis = state.data.apis.filter(overlapsReign);
    if (relApis.length) {
      container.appendChild(el("h2", {}, state.lang === "ja" ? "治世に重なるアピス牛" : "Apis bulls overlapping reign"));
      const ul = el("ul");
      for (const a of relApis) {
        const li = el("li");
        li.appendChild(document.createTextNode(`${state.lang === "ja" ? a.name : (a.nameEn || a.name)} — ${fmtYear(a.birth)} ～ ${fmtYear(a.death)}`));
        if (a.note) li.appendChild(el("div", {}, a.note));
        if (a.source) li.appendChild(el("span", { class: "src" }, a.source));
        ul.appendChild(li);
      }
      container.appendChild(ul);
    }

    // Buchis overlapping reign
    const relBuchis = state.data.buchis.filter(overlapsReign);
    if (relBuchis.length) {
      container.appendChild(el("h2", {}, state.lang === "ja" ? "治世に重なるブキス牛" : "Buchis bulls overlapping reign"));
      const ul = el("ul");
      for (const b of relBuchis) {
        const li = el("li");
        li.appendChild(document.createTextNode(`${state.lang === "ja" ? b.name : (b.nameEn || b.name)} — ${fmtYear(b.birth)} ～ ${fmtYear(b.death)}`));
        if (b.note) li.appendChild(el("div", {}, b.note));
        if (b.source) li.appendChild(el("span", { class: "src" }, b.source));
        ul.appendChild(li);
      }
      container.appendChild(ul);
    }

    vp.appendChild(container);
  }

  function renderMiniTimeline(king, yrStart, yrEnd) {
    const pxPerYr = 10;
    const width = (yrEnd - yrStart) * pxPerYr + 40;
    const height = 120;
    const svg = el("svg", { class: "timeline-svg", width, height });
    const toX = (y) => 20 + (y - yrStart) * pxPerYr;

    // axis
    svg.appendChild(el("line", { x1: 20, y1: height - 30, x2: width - 20, y2: height - 30, stroke: "var(--fg-muted)" }));
    for (let y = Math.ceil(yrStart / 5) * 5; y <= yrEnd; y += 5) {
      const x = toX(y);
      const major = y % 10 === 0;
      svg.appendChild(el("line", { x1: x, y1: height - 30, x2: x, y2: height - 26 + (major ? 3 : 0), stroke: "var(--fg-muted)" }));
      if (major) svg.appendChild(el("text", { x, y: height - 10, "text-anchor": "middle", fill: "var(--fg-muted)", "font-size": 10, "font-family": "var(--font-en)" }, `${-y}`));
    }

    // reign bar
    const ry = 18;
    svg.appendChild(el("rect", { x: toX(king.start), y: ry, width: (king.end - king.start) * pxPerYr, height: 18, fill: king.color || "var(--king)", rx: 2 }));
    if (king.coregencyStart && king.soloFrom) {
      svg.appendChild(el("rect", { x: toX(king.coregencyStart), y: ry, width: (king.soloFrom - king.coregencyStart) * pxPerYr, height: 18, fill: "url(#hatch)" }));
    }
    if (king.interruption) for (const int of king.interruption) {
      svg.appendChild(el("rect", { x: toX(int.from), y: ry + 2, width: (int.to - int.from) * pxPerYr, height: 14, fill: "rgba(0,0,0,0.55)", stroke: king.color || "var(--king)", "stroke-dasharray": "2,2" }));
    }
    svg.appendChild(el("text", { x: toX(king.start) + 4, y: ry + 13, fill: "#1a1410", "font-size": 11, "font-weight": 600 }, state.lang === "ja" ? king.nameJa : king.name));

    // events
    for (const ev of state.data.events) {
      if (ev.year < yrStart || ev.year > yrEnd) continue;
      const x = toX(ev.year);
      const color = `var(--event-${ev.category})`;
      const g = el("g");
      g.appendChild(el("circle", { cx: x, cy: 50, r: 4, fill: color }));
      g.appendChild(el("line", { x1: x, y1: 50, x2: x, y2: ry, stroke: color, "stroke-width": 1 }));
      g.addEventListener("mouseenter", (e) => showTooltip(e, `<div class="tt-title">${fmtYear(ev.year)} · ${state.lang === "ja" ? ev.title : (ev.titleEn || ev.title)}</div>${ev.note ? `<div>${ev.note}</div>` : ""}`));
      g.addEventListener("mousemove", moveTooltip);
      g.addEventListener("mouseleave", hideTooltip);
      svg.appendChild(g);
    }

    // apis
    for (const a of state.data.apis) {
      if (a.birth == null || a.death == null) continue;
      if (a.death < yrStart || a.birth > yrEnd) continue;
      const x1 = toX(Math.max(a.birth, yrStart));
      const x2 = toX(Math.min(a.death, yrEnd));
      svg.appendChild(el("rect", { x: x1, y: 62, width: Math.max(2, x2 - x1), height: 8, fill: "var(--apis)", "fill-opacity": 0.7 }));
    }
    // buchis
    for (const b of state.data.buchis) {
      if (b.birth == null || b.death == null) continue;
      if (b.death < yrStart || b.birth > yrEnd) continue;
      const x1 = toX(Math.max(b.birth, yrStart));
      const x2 = toX(Math.min(b.death, yrEnd));
      svg.appendChild(el("rect", { x: x1, y: 74, width: Math.max(2, x2 - x1), height: 8, fill: "var(--buchis)", "fill-opacity": 0.7 }));
    }

    // defs for hatch
    const defs = el("defs");
    const pat = el("pattern", { id: "hatch", patternUnits: "userSpaceOnUse", width: 6, height: 6, patternTransform: "rotate(45)" });
    pat.appendChild(el("rect", { width: 6, height: 6, fill: "transparent" }));
    pat.appendChild(el("line", { x1: 0, y: 0, y1: 0, x2: 0, y2: 6, stroke: "rgba(255,255,255,0.35)", "stroke-width": 2 }));
    defs.appendChild(pat);
    svg.appendChild(defs);

    const wrap = el("div", { class: "mini-timeline" });
    wrap.appendChild(svg);
    return wrap;
  }

  // ---------- render ----------
  function render() {
    renderHeader();
    renderSidebar();
    if (state.view === "king" && state.selectedKing) renderKingDetail();
    else renderTimeline();
  }

  // ---------- init ----------
  (async () => {
    try {
      await loadData();
      render();
    } catch (err) {
      document.getElementById("viewport").innerHTML = `<p style="color:#ff9a9a">データ読み込みエラー: ${err.message}<br>ローカルで開いている場合はブラウザの CORS 制限です。<code>python3 -m http.server</code> で配信してください。</p>`;
      console.error(err);
    }
  })();
})();
