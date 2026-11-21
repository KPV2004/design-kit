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
          <option value="loading">Loading</option><option value="Error">Error</option>
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
