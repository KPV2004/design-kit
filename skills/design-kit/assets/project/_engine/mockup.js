/* ============================================================
   Mockup engine — do not edit per project.
   Reads from mock.html:
     const tokens = {...}       color scales (same names/hex as design.md)
     const usageTokens = {...}  usage-token defaults (design.md §2.4, resolved hex)
     const themes  = {...}      theme variants (design.md §2.9): name → {token: hex} overrides
     const icons  = {...}       icon map (same as design.md §6)
     <main id="screens"> <section class="screen" id="<screen-id>:mock" data-title data-module data-device data-notes data-hint> ...
   Screen IDs end with ":mock" and pair with the wireframe screen of the same base id.
   The same file runs in two modes:
     shell  (default)   toolbar + device frame (iframe) + notes sidebar
     frame  (?frame=1)  the screens themselves, loaded inside the shell's iframe
   Global API used by screen markup: showScreen('id:mock')
   Component kit: mk-* classes in mockup.css; the gallery below renders into #component-gallery.
   ============================================================ */
(function () {
  'use strict';
  const FRAME = new URLSearchParams(location.search).has('frame');
  window.FRAME = FRAME;
  document.documentElement.classList.add(FRAME ? 'is-frame' : 'is-shell');   // set before first paint

  /* ---------- Theme engine — runs before paint in both modes.
     Colors are CSS variables (--c-<token> = "R G B"), so a theme is just a
     set of variable overrides. Dark keeps brand-700 (white text stays AA). ---------- */
  const hexCh = h => { const n = parseInt(h.slice(1), 16); return `${(n >> 16) & 255} ${(n >> 8) & 255} ${n & 255}`; };
  const THEMES = (typeof themes === 'object' && themes) || { Default: null };
  const TOKEN_KEYS = [];
  if (typeof tokens === 'object') for (const [n, sc] of Object.entries(tokens)) for (const k of Object.keys(sc)) TOKEN_KEYS.push(`${n}-${k}`);
  if (typeof usageTokens === 'object') TOKEN_KEYS.push(...Object.keys(usageTokens));
  function applyTokenMap(map) {
    for (const [t, v] of Object.entries(map || {})) {
      if (typeof v === 'string' && /^#[0-9a-fA-F]{6}$/.test(v)) document.documentElement.style.setProperty('--c-' + t, hexCh(v));
      else document.documentElement.style.removeProperty('--c-' + t);
    }
  }
  function applyTheme(name) {
    if (!(name in THEMES)) name = 'Default';
    // Defaults live in mock.html's static :root block (so design tools can edit them live);
    // a theme only writes its own overrides as inline variables. Default = clear all overrides.
    const clear = {};
    if (typeof tokens === 'object') for (const [n, sc] of Object.entries(tokens)) for (const k of Object.keys(sc)) clear[`${n}-${k}`] = null;
    if (typeof usageTokens === 'object') for (const t of Object.keys(usageTokens)) clear[t] = null;
    applyTokenMap(clear);
    if (THEMES[name]) applyTokenMap(THEMES[name]);
    // .theme-dark lets mk-* components swap 700-on-50 tints (below AA on dark surfaces) for body text
    const surf = (THEMES[name] || {})['bg-surface'] || (typeof usageTokens === 'object' && usageTokens['bg-surface']) || '#ffffff';
    const lin = c => { c /= 255; return c <= 0.03928 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4; };
    const [r, g, b] = hexCh(surf).split(' ').map(Number);
    document.documentElement.classList.toggle('theme-dark', 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b) < 0.2);
    try { localStorage.setItem('mk-theme', name); } catch {}
    return name;
  }
  function storedTheme() { try { const s = localStorage.getItem('mk-theme'); return s && s in THEMES ? s : 'Default'; } catch { return 'Default'; } }
  applyTheme(storedTheme());

  const SHELL = `<div id="shell">
  <div id="tb" class="sticky top-0 z-50">
    <div class="flex flex-wrap items-center gap-2 px-3 py-2">
      <button id="tb-toggle" aria-expanded="true" title="Collapse/expand toolbar">▾</button>
      <span class="font-semibold mr-1" id="app-title">[App] mockup</span>
      <div class="tb-body flex flex-wrap items-center gap-2">
        <button onclick="step(-1)" aria-label="Previous screen">◀</button>
        <select id="screen-select" aria-label="Select screen"></select>
        <button onclick="step(1)" aria-label="Next screen">▶</button>
        <span class="ml-2 text-muted">Viewport:</span>
        <button data-vp="desktop" aria-pressed="true">Desktop</button>
        <button data-vp="tablet" aria-pressed="false">Tablet</button>
        <button data-vp="mobile" aria-pressed="false">Mobile</button>
        <span class="ml-2 text-muted">State:</span>
        <select id="state-select" aria-label="Screen state">
          <option value="default">Default</option><option value="empty">Empty</option>
          <option value="loading">Loading</option><option value="error">Error</option>
        </select>
        <span class="ml-2 text-muted">Theme:</span>
        <select id="theme-select" aria-label="Mockup theme"></select>
        <label class="ml-2 flex items-center gap-1 cursor-pointer"><input type="checkbox" id="anno-toggle" checked> Pins</label>
        <label class="flex items-center gap-1 cursor-pointer"><input type="checkbox" id="notes-toggle" checked> Notes</label>
      </div>
    </div>
  </div>
  <div id="stage" class="vp-desktop">
    <div id="device"><iframe id="frame" title="Mockup screen"></iframe></div>
    <aside id="notes">
      <h2 id="n-title" class="font-semibold text-base"></h2>
      <p id="n-meta" class="text-zinc-500 text-xs mb-3"></p>
      <div id="n-list" class="space-y-2"></div>
      <div id="n-hint" class="mt-4 hidden"><p class="font-medium text-xs text-muted mb-1">How to try this screen</p><p class="text-xs bg-page rounded p-2"></p></div>
    </aside>
  </div>
</div>`;

  document.addEventListener('DOMContentLoaded', () => {
    if (!FRAME) document.body.insertAdjacentHTML('afterbegin', SHELL);
    document.body.classList.add('font-sans');

  const screens = [...document.querySelectorAll('#screens > .screen')];
  const ids = screens.map(s => s.id);
  const byId = id => screens.find(s => s.id === id);
  const firstId = () => ids.includes(location.hash.slice(1)) ? location.hash.slice(1) : ids[0];

  if (FRAME) {
    /* ---------- Frame mode: the actual screens ---------- */
    let curState = 'default';
    function applyState(st) {
      curState = st;
      const scr = document.querySelector('.screen.active'); if (!scr) return;
      const variants = scr.querySelectorAll('[data-state]'); if (!variants.length) return;
      const has = [...variants].some(v => v.dataset.state === st);
      variants.forEach(v => v.classList.toggle('show', v.dataset.state === (has ? st : 'default')));
    }
    window.showScreen = function (id) {
      if (!byId(id)) return;
      screens.forEach(s => s.classList.toggle('active', s.id === id));
      applyState(curState);
      window.scrollTo(0, 0);
      if (location.hash !== '#' + id) history.replaceState(null, '', '#' + id);
      parent.postMessage({ type: 'screen', id }, '*');
    };
    window.addEventListener('message', e => {
      const d = e.data || {};
      if (d.type === 'go') showScreen(d.id);
      if (d.type === 'state') applyState(d.value);
      if (d.type === 'anno') document.body.classList.toggle('hide-anno', !d.value);
      if (d.type === 'theme') applyTheme(d.value);
      // live --c-* values (channels string) mirrored from the shell — realtime theme/design edits
      if (d.type === 'theme-vars' && d.map) for (const [t, v] of Object.entries(d.map)) document.documentElement.style.setProperty('--c-' + t, v);
    });
    window.addEventListener('hashchange', () => showScreen(location.hash.slice(1)));

    // Design-system swatches with contrast vs white / dark text
    (function renderSwatches() {
      const wrap = document.getElementById('swatches'); if (!wrap) return;
      const lum = h => { const c=[1,3,5].map(i=>parseInt(h.slice(i,i+2),16)/255).map(x=>x<=0.03928?x/12.92:((x+0.055)/1.055)**2.4); return 0.2126*c[0]+0.7152*c[1]+0.0722*c[2]; };
      const ratio = (a,b) => { const [x,y]=[lum(a),lum(b)].sort((m,n)=>n-m); return (x+0.05)/(y+0.05); };
      Object.entries(tokens).forEach(([name, scale]) => {
        const row = document.createElement('div');
        row.innerHTML = `<p class="font-medium mb-2">${name}</p><div class="flex flex-wrap gap-2"></div>`;
        Object.entries(scale).forEach(([k, hex]) => {
          const w = ratio(hex,'#ffffff'), d = ratio(hex,'#0f172a');
          const c = document.createElement('div');
          c.className = 'w-28 rounded-md p-2 text-xs';
          c.style.background = hex; c.style.color = w >= d ? '#ffffff' : '#0f172a';
          c.innerHTML = `<div class="font-semibold">${name}-${k}</div><div>${hex}</div><div>on white ${w.toFixed(1)} · on dark ${d.toFixed(1)}</div>`;
          row.querySelector('div').appendChild(c);
        });
        wrap.appendChild(row);
      });
    })();
    // Icon map preview
    (function renderIcons() {
      const grid = document.getElementById('icon-grid'); if (!grid) return;
      const prefixes = [...new Set(Object.values(icons).map(n => n.split(':')[0]))];
      document.getElementById('icon-set').textContent = '· ' + prefixes.join(', ') + (prefixes.length > 1 ? ' ⚠ mixed icon sets' : '');
      grid.innerHTML = Object.entries(icons).map(([k, n]) =>
        `<div class="border border-neutral-200 rounded-md p-3 text-center"><iconify-icon icon="${n}" width="24" class="text-neutral-700"></iconify-icon>
         <div class="text-xs mt-1 font-medium">${k}</div><div class="text-[11px] text-neutral-500 break-all">${n}</div></div>`).join('');
    })();
    // Component gallery — every mk-* component with copyable markup. Icons come from the project's
    // `icons` map (add/edit/delete/search/retry/empty) so the gallery never introduces a second set.
    (function renderComponents() {
      const wrap = document.getElementById('component-gallery'); if (!wrap) return;
      const ic = (k, w = 20) => icons[k] ? `<iconify-icon icon="${icons[k]}" width="${w}" aria-hidden="true"></iconify-icon>` : '';
      const G = [
        ['Buttons', [
          ['Variants', `<div class="flex flex-wrap gap-2">
  <button class="mk-btn mk-btn-primary">${ic('add')}New order</button>
  <button class="mk-btn mk-btn-secondary">Cancel</button>
  <button class="mk-btn mk-btn-ghost">View all</button>
  <button class="mk-btn mk-btn-danger">${ic('delete')}Delete</button>
</div>`],
          ['Sizes & states', `<div class="flex flex-wrap items-center gap-2">
  <button class="mk-btn mk-btn-primary mk-btn-sm">Small</button>
  <button class="mk-btn mk-btn-primary mk-btn-lg">Large</button>
  <button class="mk-btn mk-btn-primary" disabled>Disabled</button>
  <button class="mk-btn mk-btn-primary" aria-busy="true">Saving…</button>
  <button class="mk-btn mk-btn-secondary mk-btn-icon" aria-label="Edit" title="Edit">${ic('edit')}</button>
</div>`],
        ]],
        ['Form fields', [
          ['Text field', `<div class="mk-field">
  <label for="g-sup" class="mk-label mk-req">Supplier</label>
  <input id="g-sup" class="mk-input" value="Siam Steel Co., Ltd." aria-describedby="g-sup-h">
  <p id="g-sup-h" class="mk-help">As shown on the tax invoice</p>
</div>`],
          ['Error & disabled', `<div class="grid sm:grid-cols-2 gap-4">
  <div class="mk-field">
    <label for="g-amt" class="mk-label mk-req">Amount (THB)</label>
    <input id="g-amt" class="mk-input" value="0" aria-invalid="true" aria-describedby="g-amt-e">
    <p id="g-amt-e" class="mk-error">Enter an amount above 0</p>
  </div>
  <div class="mk-field">
    <label for="g-no" class="mk-label">PO no.</label>
    <input id="g-no" class="mk-input" value="Generated on save" disabled>
  </div>
</div>`],
          ['Select & textarea', `<div class="grid sm:grid-cols-2 gap-4">
  <div class="mk-field"><label for="g-st" class="mk-label">Status</label>
    <select id="g-st" class="mk-select"><option>All statuses</option><option>Pending approval</option></select></div>
  <div class="mk-field"><label for="g-nt" class="mk-label">Notes</label>
    <textarea id="g-nt" class="mk-textarea" placeholder="Delivery instructions"></textarea></div>
</div>`],
          ['Choice controls', `<div class="flex flex-wrap gap-4 items-center">
  <label class="mk-check"><input type="checkbox" checked> Send copy to supplier</label>
  <label class="mk-radio"><input type="radio" name="g-r" checked> Net 30</label>
  <label class="mk-radio"><input type="radio" name="g-r"> Net 60</label>
  <button class="mk-switch" role="switch" aria-checked="true" onclick="this.setAttribute('aria-checked', this.getAttribute('aria-checked') !== 'true')">Email alerts</button>
</div>`],
          ['Filter chips', `<div class="flex flex-wrap gap-2" role="group" aria-label="Filter by status">
  <button class="mk-chip" aria-pressed="true">Pending</button>
  <button class="mk-chip" aria-pressed="false">Approved</button>
  <button class="mk-chip" aria-pressed="false">Rejected</button>
</div>`],
        ]],
        ['Data display', [
          ['Table', `<div class="mk-card p-0 overflow-x-auto">
<table class="mk-table">
  <thead><tr><th>PO no.</th><th>Supplier</th><th class="num">Amount (THB)</th><th>Status</th></tr></thead>
  <tbody>
    <tr aria-selected="true"><td class="tabular-nums">PO-2611-0042</td><td>Siam Steel Co., Ltd.</td><td class="num">128,450.00</td><td><span class="mk-badge mk-badge-warning">Pending approval</span></td></tr>
    <tr><td class="tabular-nums">PO-2611-0041</td><td>Bangkok Office Supplies (Head Office)</td><td class="num">9,900.00</td><td><span class="mk-badge mk-badge-success">Approved</span></td></tr>
  </tbody>
</table></div>`],
          ['Badges', `<div class="flex flex-wrap gap-2">
  <span class="mk-badge">Draft</span><span class="mk-badge mk-badge-info">Posted</span>
  <span class="mk-badge mk-badge-success">Approved</span><span class="mk-badge mk-badge-warning">Pending approval</span>
  <span class="mk-badge mk-badge-danger">Rejected</span>
</div>`],
          ['Stats, avatar, progress', `<div class="grid sm:grid-cols-3 gap-3 items-center">
  <div class="mk-stat"><span class="text-sm text-muted">Open POs</span><b>128</b></div>
  <div class="flex items-center gap-2"><span class="mk-avatar">SK</span><span class="text-sm">Somchai K.</span></div>
  <div class="mk-progress" role="progressbar" aria-valuenow="60" aria-valuemin="0" aria-valuemax="100" aria-label="Budget used"><i style="width:60%"></i></div>
</div>`],
        ]],
        ['Navigation', [
          ['Side nav', `<nav class="w-56 space-y-1" aria-label="Main">
  <a href="#" class="mk-nav-item" aria-current="page">Purchase orders</a>
  <a href="#" class="mk-nav-item">Suppliers</a>
  <a href="#" class="mk-nav-item">Reports</a>
</nav>`],
          ['Tabs', `<div class="mk-tabs" role="tablist">
  <button class="mk-tab" role="tab" aria-selected="true">Details</button>
  <button class="mk-tab" role="tab" aria-selected="false">Line items (4)</button>
  <button class="mk-tab" role="tab" aria-selected="false">History</button>
</div>`],
          ['Breadcrumb & pagination', `<div class="space-y-3">
  <nav class="mk-breadcrumb" aria-label="Breadcrumb"><a href="#">Purchasing</a><a href="#">Purchase orders</a><span aria-current="page">PO-2611-0042</span></nav>
  <nav class="mk-pagination" aria-label="Pagination">
    <button class="mk-page" disabled aria-label="Previous page">‹</button><button class="mk-page" aria-current="page">1</button>
    <button class="mk-page">2</button><button class="mk-page">3</button><button class="mk-page" aria-label="Next page">›</button>
    <span class="text-muted ml-2">1–50 of 12,431</span>
  </nav>
</div>`],
        ]],
        ['Overlays & feedback', [
          ['Confirm dialog', `<div class="relative h-64">
<div class="mk-scrim mk-inline">
  <div class="mk-modal" role="dialog" aria-modal="true" aria-labelledby="g-dlg">
    <h2 id="g-dlg" class="text-lg font-semibold mb-2">Delete PO-2611-0042?</h2>
    <p class="text-sm text-muted mb-5">The order and its 4 line items are removed. This can't be undone.</p>
    <div class="flex justify-end gap-2"><button class="mk-btn mk-btn-secondary">Cancel</button><button class="mk-btn mk-btn-danger">Delete order</button></div>
  </div>
</div></div>`],
          ['Alerts', `<div class="space-y-2">
  <div class="mk-alert" role="status">Approval limit is 500,000 THB per order</div>
  <div class="mk-alert mk-alert-success" role="status">PO-2611-0042 approved</div>
  <div class="mk-alert mk-alert-warning" role="status">Supplier tax ID expires on 31/12/2026</div>
  <div class="mk-alert mk-alert-danger" role="alert"><span class="flex-1">Couldn't load orders — check your connection</span><button class="underline inline-flex items-center gap-1">${ic('retry', 16)}Retry</button></div>
</div>`],
          ['Menu, toast, tooltip', `<div class="flex flex-wrap items-start gap-6">
  <div class="mk-menu" role="menu">
    <button class="mk-menu-item" role="menuitem">${ic('edit', 16)}Edit</button>
    <button class="mk-menu-item mk-danger" role="menuitem">${ic('delete', 16)}Delete</button>
  </div>
  <div class="mk-toast" role="status">Order saved <button class="underline">Undo</button></div>
  <span class="mk-tooltip" role="tooltip">Export to Excel</span>
</div>`],
        ]],
        ['States', [
          ['Loading', `<div class="mk-card space-y-3" aria-busy="true" aria-label="Loading orders">
  <div class="mk-skeleton w-1/3"></div><div class="mk-skeleton"></div><div class="mk-skeleton w-5/6"></div>
</div>`],
          ['Empty', `<div class="mk-card mk-empty">
  <span class="text-neutral-400">${ic('empty', 48)}</span>
  <p class="font-medium">No purchase orders yet</p>
  <p class="text-sm text-muted mb-2">Create your first order to start tracking spend</p>
  <button class="mk-btn mk-btn-primary">${ic('add')}New order</button>
</div>`],
        ]],
      ];
      const esc = t => t.replace(/&/g, '&amp;').replace(/</g, '&lt;');
      // Copy shows icon keys' real names, so pasted markup still passes verify's icon-map check.
      wrap.innerHTML = G.map(([g, items], gi) => `<section class="space-y-3"><h3 class="font-semibold">${g}</h3>
        <div class="grid lg:grid-cols-2 gap-4">${items.map(([name, html], k) => `<div class="mk-card space-y-3">
          <div class="flex items-center"><span class="text-sm font-medium">${name}</span>
            <button class="mk-btn mk-btn-ghost mk-btn-sm ml-auto" data-copy="cg-${gi}-${k}">Copy</button></div>
          <div>${html}</div><pre id="cg-${gi}-${k}">${esc(html)}</pre></div>`).join('')}</div></section>`).join('');
      wrap.addEventListener('click', async e => {
        const b = e.target.closest('[data-copy]'); if (!b) return;
        const text = document.getElementById(b.dataset.copy).textContent;
        try { await navigator.clipboard.writeText(text); } catch {}
        b.textContent = 'Copied'; setTimeout(() => b.textContent = 'Copy', 1500);
      });
    })();
    showScreen(firstId());
  } else {
    /* ---------- Shell mode: toolbar, device frame, notes ---------- */
    const $ = id => document.getElementById(id);
    const shell = $('shell'), stage = $('stage'), frame = $('frame'), sel = $('screen-select'), tb = $('tb');
    let current = null, vp = 'desktop';

    // Grouped dropdown by module
    const groups = {};
    screens.forEach(s => (groups[s.dataset.module || 'Other'] ||= []).push(s));
    Object.entries(groups).forEach(([g, list]) => {
      const og = document.createElement('optgroup'); og.label = g;
      list.forEach(s => { const o = document.createElement('option'); o.value = s.id; o.textContent = `${ids.indexOf(s.id)+1}. ${s.dataset.title || s.id}`; og.appendChild(o); });
      sel.appendChild(og);
    });

    const setTbh = () => document.documentElement.style.setProperty('--tbh', tb.offsetHeight + 'px');
    new ResizeObserver(setTbh).observe(tb);

    function setViewport(v, fromUser) {
      const locked = byId(current)?.dataset.device === 'mobile';
      if (locked) v = 'mobile'; else if (fromUser) vp = v; else v = vp;
      stage.className = 'vp-' + v;
      document.querySelectorAll('[data-vp]').forEach(b => {
        b.setAttribute('aria-pressed', String(b.dataset.vp === v));
        b.disabled = locked && b.dataset.vp !== 'mobile';
      });
    }
    function renderNotes(id) {
      const s = byId(id);
      $('n-title').textContent = s.dataset.title || id;
      $('n-meta').textContent = `#${id} · ${s.dataset.module || ''} · ${s.dataset.device === 'mobile' ? 'native mobile' : 'responsive'}`;
      const notes = (s.dataset.notes || '').split('|').map(x => x.trim()).filter(Boolean);
      $('n-list').innerHTML = notes.length
        ? notes.map((n, i) => `<p><span class="anno">${i+1}</span> ${n}</p>`).join('')
        : '<p class="text-muted">No notes</p>';
      const hint = s.dataset.hint || '';
      $('n-hint').classList.toggle('hidden', !hint);
      $('n-hint').querySelector('p:last-child').textContent = hint;
    }
    function sync(id) {
      current = id; sel.value = id; renderNotes(id); setViewport(null, false);
      if (location.hash !== '#' + id) history.replaceState(null, '', '#' + id);
    }
    window.showScreen = function (id) { if (!byId(id)) return; sync(id); frame.contentWindow?.postMessage({ type: 'go', id }, '*'); };
    window.step = d => showScreen(ids[(ids.indexOf(current) + d + ids.length) % ids.length]);

    window.addEventListener('message', e => { const d = e.data || {}; if (d.type === 'screen' && d.id !== current && byId(d.id)) sync(d.id); });
    frame.addEventListener('load', () => {
      frame.contentWindow.postMessage({ type: 'state', value: $('state-select').value }, '*');
      frame.contentWindow.postMessage({ type: 'anno', value: $('anno-toggle').checked }, '*');
      frame.contentWindow.postMessage({ type: 'theme', value: themeSel.value }, '*');
      frame.contentWindow.postMessage({ type: 'go', id: current }, '*');
    });
    sel.onchange = () => showScreen(sel.value);
    document.querySelectorAll('[data-vp]').forEach(b => b.onclick = () => setViewport(b.dataset.vp, true));
    // Theme picker — apply locally (persists) and inside the frame
    const themeSel = $('theme-select');
    Object.keys(THEMES).forEach(n => { const o = document.createElement('option'); o.value = n; o.textContent = n; themeSel.appendChild(o); });
    themeSel.value = storedTheme();
    themeSel.onchange = () => { applyTheme(themeSel.value); frame.contentWindow?.postMessage({ type: 'theme', value: themeSel.value }, '*'); };
    // Realtime bridge: any --c-* change on the shell document (theme picker, live design-tool
    // edits on :root) is mirrored into the frame — CSS does not cross the iframe boundary.
    let varRaf = 0;
    const postVars = () => {
      cancelAnimationFrame(varRaf);
      varRaf = requestAnimationFrame(() => {
        if (!frame.contentWindow) return;
        const cs = getComputedStyle(document.documentElement);
        const map = {};
        for (const t of TOKEN_KEYS) { const v = cs.getPropertyValue('--c-' + t).trim(); if (v) map[t] = v; }
        frame.contentWindow?.postMessage({ type: 'theme-vars', map }, '*');
      });
    };
    new MutationObserver(postVars).observe(document.documentElement, { attributes: true, attributeFilter: ['style'] });
    const defaultsEl = document.getElementById('theme-defaults');
    if (defaultsEl) new MutationObserver(postVars).observe(defaultsEl, { characterData: true, childList: true, subtree: true });
    postVars();
    $('state-select').onchange = e => frame.contentWindow.postMessage({ type: 'state', value: e.target.value }, '*');
    $('anno-toggle').onchange = e => frame.contentWindow.postMessage({ type: 'anno', value: e.target.checked }, '*');
    $('notes-toggle').onchange = e => shell.classList.toggle('no-notes', !e.target.checked);
    $('tb-toggle').onclick = () => { const c = tb.classList.toggle('collapsed'); $('tb-toggle').textContent = c ? '▸' : '▾'; $('tb-toggle').setAttribute('aria-expanded', String(!c)); };
    document.addEventListener('keydown', e => { if (e.target.closest('select,input')) return; if (e.key === 'ArrowRight') step(1); if (e.key === 'ArrowLeft') step(-1); });

    const start = firstId();
    sync(start);
    frame.src = location.pathname.split('/').pop() + '?frame=1#' + start;
    setTbh();
  }

  });
})();
