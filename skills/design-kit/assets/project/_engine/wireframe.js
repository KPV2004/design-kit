/* ============================================================
   Wireframe engine — do not edit per project.
   Reads from wireframes.html:
     const WF = { app, version }                    (config)
     <template id data-title data-module data-device data-notes>   (screens)
       frames inside a template: .frame-desktop / .frame-tablet / .frame-mobile
     <script type="text/plain" class="diagram" data-title>         (diagrams)
   Provides: overview grid, single-screen view with zoom/pan, Diagrams page,
   pinned feedback comments (localStorage) and markdown export.
   Global API used by screen markup: showScreen('id')
   ============================================================ */
(function () {
  'use strict';

  /* ---------- 1. Skeleton (toolbar, views, dialog) ---------- */
  const SKELETON = `
<div id="tb" class="sticky top-0 z-50 bg-slate-800 text-slate-100 text-sm">
  <div class="flex flex-wrap items-center gap-2 px-4 py-2">
    <span id="tb-title" class="font-semibold mr-2"></span>
    <button data-act="overview">Overview</button>
    <button data-act="diagrams">Diagrams</button>
    <select id="screen-select" class="bg-slate-700 rounded px-2 py-1" aria-label="Select screen"></select>
    <button data-act="prev" aria-label="Previous screen">◀</button>
    <button data-act="next" aria-label="Next screen">▶</button>
    <span class="w-px h-5 bg-slate-600 mx-1"></span>
    <button id="c-mode" aria-pressed="false" title="Pin comments: click on the wireframe (C)">💬 Comments</button>
    <button data-act="export" title="Export comments as markdown">Export (<span id="c-count">0</span>)</button>
    <span id="c-warn" class="text-amber-300 text-xs hidden">Can't save in this browser — export before closing the page</span>
    <span id="dev-ctl" class="flex items-center ml-2" role="group" aria-label="Device filter (D)">
      <button class="seg" data-dev="all">All</button><button class="seg" data-dev="desktop">Desktop</button><button class="seg" data-dev="tablet">Tablet</button><button class="seg" data-dev="mobile">Mobile</button>
    </span>
    <div class="ml-auto flex items-center gap-2">
      <span id="zoom-ctl" class="flex items-center gap-1" title="Ctrl/⌘ + scroll or pinch to zoom · hold Space and drag to pan">
        <button data-act="zoom-out" aria-label="Zoom out (-)">−</button>
        <button data-act="zoom-fit" id="zoom-label" class="min-w-[64px]" aria-label="Fit to screen (0)">Fit</button>
        <button data-act="zoom-in" aria-label="Zoom in (+)">+</button>
        <button data-act="zoom-100" aria-label="Actual size (1)">100%</button>
      </span>
      <label id="thumb-ctl" class="flex items-center gap-1">Thumbnails <input type="range" id="thumb-zoom" min="0.15" max="0.6" step="0.05" aria-label="Thumbnail size"></label>
      <label class="flex items-center gap-1 cursor-pointer"><input type="checkbox" id="anno-toggle" checked> Notes</label>
    </div>
  </div>
</div>

<div id="overview" class="view p-6"><div id="modules" class="space-y-8"></div></div>

<div id="diagrams" class="view p-6">
  <div class="flex gap-6 items-start">
    <nav id="dg-list" class="w-56 shrink-0 space-y-1 text-sm"></nav>
    <div class="flex-1 min-w-0">
      <h2 id="dg-title" class="font-semibold text-lg"></h2>
      <p class="text-xs text-slate-500 mb-2">Boxes matching a screen ID are clickable — click to open that wireframe</p>
      <div id="dg-wrap" class="zoom-wrap"><div id="dg-outer"><div id="dg-inner" class="zoom-inner"><div id="dg-graph"></div></div></div></div>
    </div>
    <aside class="w-80 shrink-0 bg-white rounded-lg p-4 text-sm">
      <div class="flex items-center justify-between mb-2"><h3 class="font-semibold">Comments on this diagram</h3>
        <button class="text-xs underline" data-act="add-general">+ Add comment</button></div>
      <div id="dg-comments" class="space-y-2"></div>
    </aside>
  </div>
</div>

<div id="single" class="view p-6">
  <div class="flex gap-6 items-start">
    <div id="sg-wrap" class="zoom-wrap flex-1 min-w-0"><div id="sg-outer"><div id="sg-inner" class="zoom-inner"></div></div></div>
    <aside class="w-80 shrink-0 bg-white rounded-lg p-4 text-sm overflow-y-auto" style="max-height:calc(100vh - var(--tbh,48px) - 48px)">
      <h2 id="s-title" class="font-semibold text-base"></h2>
      <p id="s-meta" class="text-slate-500 text-xs mb-3"></p>
      <div id="s-notes" class="space-y-1"></div>
      <hr class="my-4">
      <div class="flex items-center justify-between mb-2"><h3 class="font-semibold">Comments / change requests</h3>
        <button class="text-xs underline" data-act="add-general">+ Comment on whole page</button></div>
      <p class="text-xs text-slate-500 mb-2">Press 💬, then click a spot on the wireframe to pin a comment</p>
      <div id="s-comments" class="space-y-2"></div>
    </aside>
  </div>
</div>

<dialog id="export" class="rounded-lg p-0 w-[min(720px,95vw)] backdrop:bg-black/40">
  <div class="p-5 space-y-3">
    <h2 class="font-semibold text-lg">Export comments</h2>
    <p class="text-sm text-slate-500">Paste this into a chat with Claude, or download the .md and attach it — Claude applies every item to all affected files</p>
    <textarea id="export-text" class="w-full h-80 border rounded p-2 font-mono text-xs" readonly></textarea>
    <div class="flex flex-wrap gap-2 justify-end">
      <button class="border rounded px-3 py-1.5" data-act="clear-done">Clear done items</button>
      <button class="border rounded px-3 py-1.5" data-act="download">Download .md</button>
      <button class="bg-slate-800 text-white rounded px-3 py-1.5" data-act="copy" id="copy-btn">Copy</button>
      <button class="border rounded px-3 py-1.5" data-act="close-export">Close</button>
    </div>
  </div>
</dialog>`;

  document.addEventListener('DOMContentLoaded', init);

  function init() {
    document.body.classList.add('bg-slate-100', 'text-slate-700', 'font-sans');
    document.body.insertAdjacentHTML('afterbegin', SKELETON);
    const $ = id => document.getElementById(id);
    // `const WF` in the content file is a global lexical binding (not on window)
    const cfg = (typeof WF !== 'undefined' && WF) || { app: 'App', version: '1.0' };

    /* ---------- 2. Content model ---------- */
    const tpls = [...document.querySelectorAll('template[id]')];
    const ids = tpls.map(t => t.id);
    const tplById = id => tpls.find(t => t.id === id);
    const diagrams = [...document.querySelectorAll('script.diagram')].map(s => ({ title: s.dataset.title, def: s.textContent.trim() }));
    let current = null, currentDiagram = null, commentMode = false, selCid = null;
    $('tb-title').textContent = `${cfg.app} wireframes v${cfg.version}`;
    document.title = `${cfg.app} — Wireframes v${cfg.version}`;
    const setTbh = () => document.documentElement.style.setProperty('--tbh', $('tb').offsetHeight + 'px');
    new ResizeObserver(setTbh).observe($('tb'));

    /* ---------- 2b. Device filter ---------- */
    const FRAMES = '.frame-desktop,.frame-tablet,.frame-mobile';
    const DEVICES = ['all', 'desktop', 'tablet', 'mobile'];
    const DEV_NAME = { desktop: 'Desktop', tablet: 'Tablet', mobile: 'Mobile' };
    const deviceOf = f => f.classList.contains('frame-mobile') ? 'mobile' : f.classList.contains('frame-tablet') ? 'tablet' : 'desktop';
    let devFilter = 'all';
    try { devFilter = DEVICES.includes(localStorage.getItem('wf-device')) ? localStorage.getItem('wf-device') : 'all'; } catch {}
    const hasDevice = root => devFilter === 'all' || [...root.querySelectorAll(FRAMES)].some(f => deviceOf(f) === devFilter);
    const emptyNote = (big) => {
      const d = document.createElement('div'); d.className = 'dev-empty';
      d.innerHTML = big ? '—' : `No ${DEV_NAME[devFilter]} frame on this screen<br><button class="underline mt-2" data-dev="all">Show all</button>`;
      return d;
    };
    function setDevice(dev) {
      devFilter = dev;
      try { localStorage.setItem('wf-device', dev); } catch {}
      DEVICES.forEach(d => document.body.classList.toggle('dev-' + d, d === dev && d !== 'all'));
      document.querySelectorAll('[data-dev]').forEach(b => b.matches('.seg') && b.setAttribute('aria-pressed', String(b.dataset.dev === dev)));
      if (current) { markEmptyStage(); zSingle.fit(); }
      else if (document.getElementById('overview').classList.contains('active')) showOverview();
    }
    function markEmptyStage() {
      $('sg-inner').querySelector(':scope > .dev-empty')?.remove();
      if (!hasDevice($('sg-inner'))) $('sg-inner').appendChild(emptyNote(false));
    }

    /* ---------- 3. Zoom & pan ---------- */
    const ZMIN = 0.1, ZMAX = 3;
    function makeZoom(wrap, outer, inner) {
      let mode = 'fit', z = 1;
      const natural = () => { inner.style.transform = 'none'; return { w: inner.scrollWidth, h: inner.scrollHeight }; };
      function apply() {
        const n = natural();
        if (mode === 'fit') z = Math.min(1, (wrap.clientWidth - 4) / n.w);
        z = Math.max(ZMIN, Math.min(ZMAX, z));
        inner.style.transform = `scale(${z})`;
        inner.style.setProperty('--ps', (1 / z).toFixed(3));
        outer.style.width = n.w * z + 'px'; outer.style.height = n.h * z + 'px';
        $('zoom-label').textContent = mode === 'fit' ? `Fit ${Math.round(z * 100)}%` : `${Math.round(z * 100)}%`;
      }
      function set(next, anchor) {
        const r = wrap.getBoundingClientRect();
        const ax = anchor ? anchor.clientX - r.left : wrap.clientWidth / 2;
        const ay = anchor ? anchor.clientY - r.top : wrap.clientHeight / 2;
        const px = (wrap.scrollLeft + ax) / z, py = (wrap.scrollTop + ay) / z;
        mode = 'manual'; z = Math.max(ZMIN, Math.min(ZMAX, next)); apply();
        wrap.scrollLeft = px * z - ax; wrap.scrollTop = py * z - ay;
      }
      wrap.addEventListener('wheel', e => {
        if (!(e.ctrlKey || e.metaKey)) return;
        e.preventDefault(); set(z * Math.exp(-e.deltaY * 0.0025), e);
      }, { passive: false });
      // Space + drag (or middle mouse) to pan
      let drag = null;
      wrap.addEventListener('mousedown', e => {
        if (!(document.body.classList.contains('space-held') || e.button === 1)) return;
        e.preventDefault(); drag = { x: e.clientX, y: e.clientY, l: wrap.scrollLeft, t: wrap.scrollTop }; wrap.classList.add('panning');
      });
      window.addEventListener('mousemove', e => { if (drag) { wrap.scrollLeft = drag.l - (e.clientX - drag.x); wrap.scrollTop = drag.t - (e.clientY - drag.y); } });
      window.addEventListener('mouseup', () => { drag = null; wrap.classList.remove('panning'); });
      new ResizeObserver(() => { if (wrap.offsetParent) apply(); }).observe(wrap);
      return { apply, set, fit() { mode = 'fit'; apply(); wrap.scrollTo(0, 0); }, by(f) { set(z * f); }, get z() { return z; } };
    }
    const zSingle = makeZoom($('sg-wrap'), $('sg-outer'), $('sg-inner'));
    const zDiagram = makeZoom($('dg-wrap'), $('dg-outer'), $('dg-inner'));
    const activeZoom = () => current ? zSingle : currentDiagram != null ? zDiagram : null;
    const STEPS = [0.1, 0.25, 0.33, 0.5, 0.67, 0.75, 0.9, 1, 1.25, 1.5, 2, 3];
    const stepZoom = dir => { const zm = activeZoom(); if (!zm) return;
      const next = dir > 0 ? STEPS.find(s => s > zm.z + 0.001) : [...STEPS].reverse().find(s => s < zm.z - 0.001);
      if (next) zm.set(next); };

    /* ---------- 4. Feedback storage ---------- */
    const STORE = 'wf-feedback:' + location.pathname;
    let comments = [];
    try { comments = JSON.parse(localStorage.getItem(STORE) || '[]'); } catch { $('c-warn').classList.remove('hidden'); }
    function save() {
      try { localStorage.setItem(STORE, JSON.stringify(comments)); } catch { $('c-warn').classList.remove('hidden'); }
      $('c-count').textContent = comments.filter(c => !c.done).length;
    }
    const keyOf = () => current ? 'screen:' + current : currentDiagram != null ? 'diagram:' + diagrams[currentDiagram].title : null;
    const listFor = key => comments.filter(c => c.key === key);
    const TYPES = ['Fix', 'Add', 'Remove', 'Question'];
    const esc = t => String(t).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/"/g, '&quot;');

    function newComment(extra) {
      const key = keyOf(); if (!key) return;
      const c = { id: Date.now().toString(36) + Math.random().toString(36).slice(2, 6), key, type: 'Fix', text: '', done: false, at: new Date().toISOString(), ...extra };
      comments.push(c); selCid = c.id; save(); refreshComments();
      setTimeout(() => document.querySelector(`[data-cid="${c.id}"] textarea`)?.focus(), 0);
    }
    function nearText(el) {
      let s = (el.innerText || '').replace(/\s+/g, ' ').trim();
      if (!s) { let p = el; while (p && !s) { p = p.parentElement; s = (p?.querySelector('.wf-label')?.innerText || '').trim(); if (p?.matches?.(FRAMES)) break; } }
      return s.replace(/\s*\d+$/, '').slice(0, 40);
    }
    function commentHTML(c, n) {
      const where = c.frame ? `${c.frame} · near "${c.near || '-'}"` : 'Whole page';
      return `<div class="c-item border rounded p-2 space-y-1 ${c.id === selCid ? 'sel' : ''}" data-cid="${c.id}">
        <div class="flex items-center gap-2 text-xs"><span class="pin-tag ${c.done ? 'done' : ''}">${n}</span>
          <span class="text-slate-500 truncate" title="${esc(where)}">${esc(where)}</span>
          <button class="ml-auto text-slate-400 hover:text-red-600" data-c="del" aria-label="Delete comment">✕</button></div>
        <div class="flex items-center gap-2 text-xs">
          <select data-c="type" class="border rounded px-1 py-0.5">${TYPES.map(t => `<option ${t === c.type ? 'selected' : ''}>${t}</option>`).join('')}</select>
          <label class="flex items-center gap-1"><input type="checkbox" data-c="done" ${c.done ? 'checked' : ''}> Done</label></div>
        <textarea data-c="text" rows="3" class="w-full border rounded p-1.5 text-sm" placeholder="What should change and how, e.g. move the button to the top right, add a phone field">${esc(c.text)}</textarea>
      </div>`;
    }
    function highlight() {
      document.querySelectorAll('.c-item').forEach(e => e.classList.toggle('sel', e.dataset.cid === selCid));
      document.querySelectorAll('.pin').forEach(e => e.classList.toggle('sel', e.dataset.cid === selCid));
    }
    function refreshComments() {
      const key = keyOf(); if (!key) return;
      const list = listFor(key), wrap = current ? $('s-comments') : $('dg-comments');
      wrap.innerHTML = list.length ? list.map((c, i) => commentHTML(c, i + 1)).join('') : '<p class="text-slate-400 text-xs">No comments yet</p>';
      wrap.querySelectorAll('[data-cid]').forEach(el => {
        const c = comments.find(x => x.id === el.dataset.cid);
        el.addEventListener('focusin', () => { if (selCid !== c.id) { selCid = c.id; highlight(); } });
        el.querySelector('[data-c=text]').oninput = e => { c.text = e.target.value; save(); };
        el.querySelector('[data-c=type]').onchange = e => { c.type = e.target.value; save(); };
        el.querySelector('[data-c=done]').onchange = e => { c.done = e.target.checked; save(); refreshComments(); };
        el.querySelector('[data-c=del]').onclick = () => { comments = comments.filter(x => x.id !== c.id); save(); refreshComments(); };
      });
      if (current) renderPins();
    }
    // Hidden (filtered) frames stay in the DOM, so pin frameIndex values remain stable
    const framesInStage = () => [...document.querySelectorAll('#sg-inner ' + FRAMES.split(',').join(', #sg-inner '))];
    function renderPins() {
      document.querySelectorAll('#sg-inner .pin').forEach(p => p.remove());
      const frames = framesInStage();
      listFor('screen:' + current).forEach((c, i) => {
        if (c.frameIndex == null || !frames[c.frameIndex]) return;
        const pin = document.createElement('div');
        pin.className = 'pin' + (c.done ? ' done' : '') + (c.id === selCid ? ' sel' : '');
        pin.dataset.cid = c.id; pin.textContent = i + 1;
        pin.style.left = c.x + '%'; pin.style.top = c.y + '%';
        pin.onclick = e => { e.stopPropagation(); selCid = c.id; highlight(); document.querySelector(`.c-item[data-cid="${c.id}"] textarea`)?.focus(); };
        frames[c.frameIndex].appendChild(pin);
      });
    }
    // Capture phase: while commenting, clicks place pins instead of navigating
    $('sg-inner').addEventListener('click', e => {
      if (!commentMode || document.body.classList.contains('space-held')) return;
      const frame = e.target.closest(FRAMES); if (!frame || e.target.closest('.pin')) return;
      e.preventDefault(); e.stopPropagation();
      const r = frame.getBoundingClientRect();
      newComment({
        frame: deviceOf(frame),
        frameIndex: framesInStage().indexOf(frame),
        x: +((e.clientX - r.left) / r.width * 100).toFixed(1),
        y: +((e.clientY - r.top) / r.height * 100).toFixed(1),
        near: nearText(e.target),
      });
    }, true);
    function toggleCommentMode() {
      commentMode = !commentMode;
      $('c-mode').setAttribute('aria-pressed', String(commentMode));
      document.body.classList.toggle('commenting', commentMode);
      if (commentMode && !current) showScreen(ids[0]);
    }

    /* ---------- 5. Export ---------- */
    function exportMarkdown() {
      const now = new Date(), pad = n => String(n).padStart(2, '0');
      const d = `${pad(now.getDate())}/${pad(now.getMonth() + 1)}/${now.getFullYear()} ${pad(now.getHours())}:${pad(now.getMinutes())}`;
      const open = comments.filter(c => !c.done);
      let md = `# Wireframe feedback — ${cfg.app} — v${cfg.version}\n> Exported ${d} · ${open.length} open items · file ${decodeURIComponent(location.pathname.split('/').pop())}\n`;
      const order = k => k.startsWith('screen:') ? ids.indexOf(k.slice(7)) : 1000 + diagrams.findIndex(x => 'diagram:' + x.title === k);
      [...new Set(comments.map(c => c.key))].sort((a, b) => order(a) - order(b)).forEach(k => {
        if (k.startsWith('screen:')) { const id = k.slice(7); md += `\n## [${id}] ${tplById(id)?.dataset.title || '(screen removed)'}\n`; }
        else md += `\n## Diagram: ${k.slice(8)}\n`;
        listFor(k).forEach((c, i) => {
          const where = c.frame ? ` · ${c.frame} · near "${c.near || '-'}" · position (${c.x}%, ${c.y}%)` : '';
          md += `${i + 1}. ${c.done ? '✅ ' : ''}**${c.type}**${where} — ${c.text.trim().replace(/\n+/g, ' ') || '(no details)'}\n`;
        });
      });
      if (!comments.length) md += '\n(no comments yet)\n';
      return md;
    }
    async function copyExport() {
      const t = $('export-text');
      try { await navigator.clipboard.writeText(t.value); } catch { t.select(); document.execCommand('copy'); }
      $('copy-btn').textContent = 'Copied ✓'; setTimeout(() => $('copy-btn').textContent = 'Copy', 1500);
    }
    function downloadExport() {
      const a = document.createElement('a');
      a.href = URL.createObjectURL(new Blob([$('export-text').value], { type: 'text/markdown' }));
      a.download = `${cfg.app.replace(/[^\w\u0E00-\u0E7F-]+/g, '-')}-wireframe-feedback.md`; a.click();
      setTimeout(() => URL.revokeObjectURL(a.href), 1000);
    }

    /* ---------- 6. Navigation & views ---------- */
    const sel = $('screen-select'), groups = {};
    tpls.forEach(t => (groups[t.dataset.module || 'Other'] ||= []).push(t));
    Object.entries(groups).forEach(([g, list]) => {
      const og = document.createElement('optgroup'); og.label = g;
      list.forEach(t => { const o = document.createElement('option'); o.value = t.id; o.textContent = `${ids.indexOf(t.id) + 1}. ${t.dataset.title}`; og.appendChild(o); });
      sel.appendChild(og);
    });
    function setView(v) {
      document.querySelectorAll('.view').forEach(e => e.classList.toggle('active', e.id === v));
      $('zoom-ctl').style.display = v === 'overview' ? 'none' : '';
      $('thumb-ctl').style.display = v === 'overview' ? '' : 'none';
      $('dev-ctl').style.display = v === 'diagrams' ? 'none' : '';
      window.scrollTo(0, 0);
    }
    function showOverview() {
      current = null; currentDiagram = null; setView('overview'); history.replaceState(null, '', location.pathname);
      const modWrap = $('modules'); modWrap.innerHTML = '';
      Object.entries(groups).forEach(([name, list]) => {
        const sec = document.createElement('section');
        sec.innerHTML = `<h2 class="font-semibold mb-3">${esc(name)} <span class="text-slate-400 text-sm">(${list.length} screens)</span></h2><div class="flex flex-wrap gap-6"></div>`;
        list.forEach(t => {
          const n = listFor('screen:' + t.id).filter(c => !c.done).length;
          const card = document.createElement('button');
          card.className = 'text-left bg-white rounded-lg p-2 shadow-sm hover:ring-2 hover:ring-slate-400';
          card.onclick = () => showScreen(t.id);
          card.innerHTML = `<div class="thumb"></div><div class="text-xs mt-2 flex items-center gap-1"><span class="text-slate-400">${ids.indexOf(t.id) + 1}.</span> ${esc(t.dataset.title)} <span class="text-slate-400">#${t.id}</span>${n ? `<span class="pin-tag ml-auto">💬 ${n}</span>` : ''}</div>`;
          const thumbEl = card.querySelector('.thumb');
          thumbEl.appendChild(t.content.cloneNode(true));
          if (!hasDevice(thumbEl)) thumbEl.appendChild(emptyNote(true));
          sec.querySelector('div').appendChild(card);
        });
        modWrap.appendChild(sec);
      });
    }
    function showScreen(id) {
      const t = tplById(id); if (!t) return;
      const changed = current !== id;
      current = id; currentDiagram = null; sel.value = id;
      $('sg-inner').innerHTML = ''; $('sg-inner').appendChild(t.content.cloneNode(true)); markEmptyStage();
      $('s-title').textContent = t.dataset.title;
      $('s-meta').textContent = `#${t.id} · ${t.dataset.module || ''} · ${t.dataset.device || 'desktop'}`;
      const notes = (t.dataset.notes || '').split('|').filter(Boolean);
      $('s-notes').innerHTML = notes.length ? notes.map((n, i) => `<p><span class="anno">${i + 1}</span> ${esc(n)}</p>`).join('') : '<p class="text-slate-400">No notes</p>';
      setView('single'); history.replaceState(null, '', '#' + id);
      requestAnimationFrame(() => changed ? zSingle.fit() : zSingle.apply());
      refreshComments();
    }
    const step = d => showScreen(ids[((current ? ids.indexOf(current) : -1) + d + ids.length) % ids.length]);

    /* ---------- 7. Diagrams ---------- */
    let mermaidReady = false;
    function showDiagrams(i = currentDiagram ?? 0) {
      current = null; setView('diagrams'); history.replaceState(null, '', '#diagrams');
      if (!diagrams.length) { $('dg-title').textContent = 'No diagrams yet'; return; }
      $('dg-list').innerHTML = diagrams.map((d, k) => {
        const n = listFor('diagram:' + d.title).filter(c => !c.done).length;
        return `<button class="w-full text-left px-3 py-2 rounded ${k === i ? 'bg-slate-800 text-white' : 'bg-white hover:bg-slate-200'}" data-dg="${k}">${esc(d.title)}${n ? ` <span class="pin-tag">${n}</span>` : ''}</button>`;
      }).join('');
      $('dg-list').querySelectorAll('[data-dg]').forEach(b => b.onclick = () => showDiagrams(+b.dataset.dg));
      renderDiagram(i);
    }
    async function renderDiagram(i) {
      currentDiagram = i;
      const d = diagrams[i], g = $('dg-graph');
      $('dg-title').textContent = d.title;
      refreshComments();
      if (!window.mermaid) { g.textContent = "Couldn't load Mermaid (internet connection required)"; return; }
      if (!mermaidReady) { mermaid.initialize({ startOnLoad: false, theme: 'neutral', fontFamily: '"IBM Plex Sans Thai", Tahoma, sans-serif' }); mermaidReady = true; }
      try {
        const { svg } = await mermaid.render('dg-svg-' + i + '-' + Date.now(), d.def);
        g.innerHTML = svg;
        g.querySelectorAll('g.node').forEach(n => {
          const m = n.id.match(/^flowchart-(.+)-\d+$/);
          if (m && ids.includes(m[1])) { n.classList.add('wf-link'); n.addEventListener('click', () => showScreen(m[1])); }
        });
      } catch (err) { g.innerHTML = `<pre class="text-red-600 text-xs whitespace-pre-wrap">Mermaid error: ${esc(err.message || err)}</pre>`; }
      requestAnimationFrame(() => zDiagram.fit());
    }

    /* ---------- 8. Wiring ---------- */
    const actions = {
      overview: showOverview, diagrams: () => showDiagrams(), prev: () => step(-1), next: () => step(1),
      export: () => { $('export-text').value = exportMarkdown(); $('export').showModal(); },
      'add-general': () => newComment({ frame: null }),
      'clear-done': () => { comments = comments.filter(c => !c.done); save(); $('export-text').value = exportMarkdown(); refreshComments(); },
      download: downloadExport, copy: copyExport, 'close-export': () => $('export').close(),
      'zoom-in': () => stepZoom(1), 'zoom-out': () => stepZoom(-1),
      'zoom-fit': () => activeZoom()?.fit(), 'zoom-100': () => activeZoom()?.set(1),
    };
    document.addEventListener('click', e => {
      const d = e.target.closest('[data-dev]'); if (d) { setDevice(d.dataset.dev); return; }
      const b = e.target.closest('[data-act]'); if (b && actions[b.dataset.act]) actions[b.dataset.act]();
    });
    $('c-mode').onclick = toggleCommentMode;
    sel.onchange = () => showScreen(sel.value);
    const thumb = $('thumb-zoom');
    thumb.value = tpls.every(t => t.dataset.device === 'mobile') ? 0.45 : 0.25;
    const applyThumb = () => document.documentElement.style.setProperty('--z', thumb.value);
    thumb.oninput = applyThumb; applyThumb();
    $('anno-toggle').onchange = e => document.body.classList.toggle('hide-anno', !e.target.checked);
    document.addEventListener('keydown', e => {
      if (e.target.closest('input,textarea,select,dialog')) return;
      if (e.code === 'Space' && activeZoom()) { e.preventDefault(); document.body.classList.add('space-held'); return; }
      const k = e.key;
      if (k === 'ArrowRight') step(1); else if (k === 'ArrowLeft') step(-1);
      else if (k === 'c' || k === 'C') toggleCommentMode();
      else if (k === 'd' || k === 'D') setDevice(DEVICES[(DEVICES.indexOf(devFilter) + 1) % DEVICES.length]);
      else if (k === '+' || k === '=') stepZoom(1); else if (k === '-') stepZoom(-1);
      else if (k === '0') activeZoom()?.fit(); else if (k === '1') activeZoom()?.set(1);
    });
    document.addEventListener('keyup', e => { if (e.code === 'Space') document.body.classList.remove('space-held'); });
    window.showScreen = showScreen; // used by onclick in screen markup

    save(); setTbh(); setDevice(devFilter);
    const route = () => { const h = location.hash.slice(1);
      h === 'diagrams' ? showDiagrams() : ids.includes(h) ? (h !== current && showScreen(h)) : showOverview(); };
    window.addEventListener('hashchange', route);
    route();
  }
})();
