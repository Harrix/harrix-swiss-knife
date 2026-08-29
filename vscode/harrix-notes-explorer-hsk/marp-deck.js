/**
 * Marp deck parse + HTML for preview / present mode.
 * Subset aligned with harrix-notes-android MarpDeckParser / MarpHtml.
 */

const FRONTMATTER_RE = /^---\r?\n([\s\S]*?)\r?\n---\r?\n?/;
const HR_RE = /^(\*{3,}|-{3,}|_{3,})\s*$/;
const IMAGE_RE_SOURCE = '!\\[([^\\]]*)]\\(([^)]+)\\)';
const COMMENT_RE = /<!--([\s\S]*?)-->/g;
const DIRECTIVE_RE = /^_?([A-Za-z][\w-]*)\s*:\s*(.*)$/;
const FENCE_RE = /^(`{3,}|~{3,})/;

/**
 * @param {string} source
 * @returns {boolean}
 */
function isMarpMarkdown(source) {
  const fm = FRONTMATTER_RE.exec(String(source || '').replace(/^\uFEFF/, ''));
  if (!fm) {
    return false;
  }
  const block = fm[1];
  for (const line of block.split(/\r?\n/)) {
    const m = /^type\s*:\s*(.*)$/i.exec(line.trim());
    if (m && unquote(m[1]).toLowerCase() === 'marp') {
      return true;
    }
    const p = /^marp\s*:\s*(.*)$/i.exec(line.trim());
    if (p) {
      const v = unquote(p[1]).toLowerCase();
      if (['true', 'yes', 'on', '1'].includes(v)) {
        return true;
      }
    }
  }
  return false;
}

/**
 * @param {string} source
 */
function parseDeck(source) {
  let text = String(source || '');
  if (text.charCodeAt(0) === 0xfeff) {
    text = text.slice(1);
  }
  const fm = FRONTMATTER_RE.exec(text);
  const yaml = fm ? fm[1] : '';
  const body = fm ? text.slice(fm[0].length) : text;
  const global = parseDirectiveBlock(yaml);
  const parts = splitSlides(body);
  const slides = (parts.length ? parts : ['']).map(parseSlide);
  return { global, slides };
}

/**
 * @param {string} markdown
 * @param {(md: string) => string} renderMarkdown
 * @returns {string}
 */
function renderMarpPreviewHtml(markdown, renderMarkdown) {
  const deck = parseDeck(markdown);
  const sections = deck.slides.map((slide, index) => {
    const html = renderMarkdown(slide.bodyMarkdown || ' ');
    const cls = ['hne-marp-slide'];
    if (index === 0) {
      cls.push('active');
    }
    const extra = mergedClass(deck.global, slide.local);
    if (extra) {
      cls.push(extra);
    }
    return `<section class="${cls.join(' ')}" data-index="${index}">${html}</section>`;
  });
  return `<div class="hne-marp-deck">${sections.join('\n')}</div>`;
}

/**
 * @param {string} markdown
 * @param {(md: string) => string} renderMarkdown
 * @param {{ chrome?: boolean }} [opts]
 */
function renderMarpPresentHtml(markdown, renderMarkdown, opts = {}) {
  const deck = parseDeck(markdown);
  const chrome = opts.chrome !== false;
  const slidesHtml = deck.slides
    .map((slide, index) => {
      const html = renderMarkdown(slide.bodyMarkdown || ' ');
      const active = index === 0 ? ' active' : '';
      const extra = mergedClass(deck.global, slide.local);
      const bgs = slide.backgrounds
        .filter((bg) => !bg.split)
        .map(
          (bg) =>
            `background-image:url('${cssUrl(bg.src)}');background-size:${bg.size};background-position:center;background-repeat:no-repeat;`,
        )
        .join('');
      const split = slide.backgrounds.find((bg) => bg.split);
      const splitHtml = split
        ? `<div class="split-bg" style="justify-content:${split.split === 'left' ? 'flex-start' : 'flex-end'}"><div class="split-pane" style="width:${split.splitPercent || 50}%;background-image:url('${cssUrl(split.src)}');background-size:${split.size};background-position:center;background-repeat:no-repeat;"></div></div>`
        : '';
      return `<section class="slide${active} ${extra}" style="${bgs}" data-index="${index}">${splitHtml}<div class="content">${html}</div></section>`;
    })
    .join('\n');
  const chromeHtml = chrome
    ? `<div class="chrome"><button type="button" id="prev">‹</button><span id="counter"></span><button type="button" id="next">›</button></div>`
    : '';
  return `<!DOCTYPE html><html><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width, initial-scale=1"/>
<style>
html,body{margin:0;height:100%;background:#111;font-family:system-ui,sans-serif;overflow:hidden}
.deck{height:100%;display:flex;align-items:center;justify-content:center;padding-bottom:${chrome ? 48 : 0}px;box-sizing:border-box}
.stage{width:min(100vw,calc((100vh - ${chrome ? 48 : 0}px)*16/9));aspect-ratio:16/9;position:relative;overflow:hidden;background:#fff;box-shadow:0 8px 32px rgba(0,0,0,.35)}
.slide{position:absolute;inset:0;display:none;flex-direction:column;box-sizing:border-box}
.slide.active{display:flex}
.slide.lead .content{margin:auto;text-align:center}
.slide.invert{background:#111!important;color:#f3f3f3!important}
.split-bg{position:absolute;inset:0;display:flex;pointer-events:none}
.split-pane{height:100%}
.content{position:relative;z-index:1;flex:1;overflow:auto;padding:5% 6%;font-size:clamp(16px,2.4vw,28px);line-height:1.35}
.content img{max-width:100%;height:auto}
.content pre{background:rgba(127,127,127,.15);padding:12px;border-radius:8px;overflow:auto;white-space:pre-wrap}
.chrome{position:fixed;left:0;right:0;bottom:0;height:48px;display:flex;align-items:center;justify-content:center;gap:12px;background:#1e1e1e;color:#eee}
.chrome button{min-width:44px;min-height:40px;font-size:20px;border:0;border-radius:8px;background:transparent;color:inherit}
</style></head><body>
<div class="deck"><div class="stage">${slidesHtml}</div></div>
${chromeHtml}
<script>
(function(){
  var slides=document.querySelectorAll('.slide');
  var i=0;
  function show(n){if(n<0)n=0;if(n>slides.length-1)n=slides.length-1;i=n;for(var s=0;s<slides.length;s++)slides[s].classList.toggle('active',s===i);var c=document.getElementById('counter');if(c)c.textContent=(i+1)+' / '+slides.length;}
  document.getElementById('prev')&&document.getElementById('prev').addEventListener('click',function(e){e.stopPropagation();show(i-1);});
  document.getElementById('next')&&document.getElementById('next').addEventListener('click',function(e){e.stopPropagation();show(i+1);});
  document.addEventListener('keydown',function(e){if(e.key==='ArrowRight'||e.key===' '){e.preventDefault();show(i+1);}if(e.key==='ArrowLeft'){e.preventDefault();show(i-1);}});
  document.addEventListener('click',function(e){if(e.target.closest&&e.target.closest('.chrome,a,button'))return;if(e.clientX<window.innerWidth/2)show(i-1);else show(i+1);});
  var startX=0;
  document.addEventListener('touchstart',function(e){if(e.touches.length===1)startX=e.touches[0].clientX;},{passive:true});
  document.addEventListener('touchend',function(e){var dx=e.changedTouches[0].clientX-startX;if(dx>48)show(i-1);else if(dx<-48)show(i+1);},{passive:true});
  show(0);
})();
</script></body></html>`;
}

function mergedClass(global, local) {
  return `${global.classNames || ''} ${local.classNames || ''}`.trim();
}

function splitSlides(body) {
  const slides = [];
  let current = [];
  let inFence = false;
  for (const rawLine of body.split(/\r?\n/)) {
    const line = rawLine.trimEnd();
    if (FENCE_RE.test(line.trim())) {
      inFence = !inFence;
      current.push(rawLine);
      continue;
    }
    if (!inFence && HR_RE.test(line.trim())) {
      slides.push(current.join('\n'));
      current = [];
      continue;
    }
    current.push(rawLine);
  }
  slides.push(current.join('\n'));
  return slides.map((s) => s.replace(/^\n+|\n+$/g, ''));
}

function parseSlide(raw) {
  const comments = [];
  const without = String(raw || '').replace(COMMENT_RE, (_, inner) => {
    comments.push(inner);
    return '';
  });
  let local = emptyDirectives();
  const notes = [];
  for (const comment of comments) {
    if (isDirectiveComment(comment)) {
      local = mergeDirectives(local, parseDirectiveBlock(comment));
    } else if (comment.trim()) {
      notes.push(comment.trim());
    }
  }
  const { backgrounds, body } = extractBackgrounds(without);
  return {
    bodyMarkdown: rewriteInlineImageAlts(body).trim(),
    notes: notes.join('\n'),
    local,
    backgrounds,
  };
}

function emptyDirectives() {
  return {
    paginate: null,
    header: '',
    footer: '',
    classNames: '',
    backgroundColor: '',
    color: '',
    size: '',
    theme: '',
  };
}

function isDirectiveComment(comment) {
  let found = false;
  for (const line of comment.split(/\r?\n/)) {
    const trimmed = line.trim();
    if (!trimmed) {
      continue;
    }
    if (DIRECTIVE_RE.test(trimmed)) {
      found = true;
    } else {
      return false;
    }
  }
  return found;
}

function parseDirectiveBlock(text) {
  const d = emptyDirectives();
  for (const rawLine of String(text || '').split(/\r?\n/)) {
    const m = DIRECTIVE_RE.exec(rawLine.trim());
    if (!m) {
      continue;
    }
    const key = m[1].toLowerCase();
    const value = unquote(m[2]);
    if (key === 'paginate') {
      d.paginate = parseBool(value);
    } else if (key === 'header') {
      d.header = value;
    } else if (key === 'footer') {
      d.footer = value;
    } else if (key === 'class') {
      d.classNames = value;
    } else if (key === 'backgroundcolor' || key === 'background-color') {
      d.backgroundColor = value;
    } else if (key === 'color') {
      d.color = value;
    } else if (key === 'size') {
      d.size = value;
    } else if (key === 'theme') {
      d.theme = value;
    }
  }
  return d;
}

function mergeDirectives(base, extra) {
  return {
    paginate: extra.paginate != null ? extra.paginate : base.paginate,
    header: extra.header || base.header,
    footer: extra.footer || base.footer,
    classNames: [base.classNames, extra.classNames].filter(Boolean).join(' '),
    backgroundColor: extra.backgroundColor || base.backgroundColor,
    color: extra.color || base.color,
    size: extra.size || base.size,
    theme: extra.theme || base.theme,
  };
}

function extractBackgrounds(markdown) {
  const backgrounds = [];
  const body = String(markdown || '').replace(new RegExp(IMAGE_RE_SOURCE, 'g'), (all, alt, src) => {
    const tokens = tokenizeAlt(alt);
    if (tokens.some((t) => t.toLowerCase() === 'bg')) {
      backgrounds.push(imageBackgroundFromTokens(src.trim(), tokens));
      return '';
    }
    return all;
  });
  return { backgrounds, body };
}

function rewriteInlineImageAlts(markdown) {
  return String(markdown || '').replace(new RegExp(IMAGE_RE_SOURCE, 'g'), (_all, alt, src) => {
    const cleaned = tokenizeAlt(alt)
      .filter((t) => !isMarpImageKeyword(t))
      .join(' ');
    return `![${cleaned}](${src})`;
  });
}

function tokenizeAlt(alt) {
  return String(alt || '')
    .trim()
    .split(/\s+/)
    .filter(Boolean);
}

function isMarpImageKeyword(token) {
  const t = String(token).toLowerCase();
  if (['bg', 'cover', 'contain', 'fit', 'auto', 'left', 'right'].includes(t)) {
    return true;
  }
  if (/^(left|right):\d+%$/.test(t) || /^(w|h|width|height):.+/.test(t) || /^\d+%$/.test(t)) {
    return true;
  }
  return false;
}

function imageBackgroundFromTokens(src, tokens) {
  let size = 'cover';
  let split = '';
  let splitPercent;
  for (const token of tokens) {
    const t = token.toLowerCase();
    if (['cover', 'contain', 'fit', 'auto'].includes(t)) {
      size = t === 'fit' ? 'contain' : t;
    } else if (t === 'left' || t === 'right') {
      split = t;
    } else if (t.startsWith('left:') || t.startsWith('right:')) {
      split = t.split(':')[0];
      splitPercent = Number.parseInt(t.split(':')[1], 10);
    }
  }
  return { src, size, split, splitPercent };
}

function parseBool(value) {
  const v = String(value).trim().toLowerCase();
  if (['true', 'yes', 'on', '1'].includes(v)) {
    return true;
  }
  if (['false', 'no', 'off', '0'].includes(v)) {
    return false;
  }
  return null;
}

function unquote(value) {
  let v = String(value ?? '').trim();
  if (v.length >= 2 && ((v.startsWith('"') && v.endsWith('"')) || (v.startsWith("'") && v.endsWith("'")))) {
    v = v.slice(1, -1);
  }
  return v.trim();
}

function cssUrl(value) {
  return String(value).replace(/'/g, '%27').replace(/\n/g, '');
}

/**
 * @param {string} markdown
 * @param {{ markedSrc: string, cspSource: string }} opts
 */
function renderMarpPresentWebview(markdown, opts) {
  const deck = parseDeck(markdown);
  const slides = deck.slides.map((slide) => ({
    md: slide.bodyMarkdown,
    classNames: mergedClass(deck.global, slide.local),
    backgrounds: slide.backgrounds,
  }));
  const payload = JSON.stringify(slides).replace(/</g, '\\u003c');
  const markedSrc = opts.markedSrc;
  const csp = opts.cspSource;
  return `<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; img-src ${csp} https: http: data:; script-src ${csp} 'unsafe-inline'; style-src 'unsafe-inline';"/>
<style>
html,body{margin:0;height:100%;background:#111;font-family:system-ui,sans-serif;overflow:hidden}
.deck{height:100%;display:flex;align-items:center;justify-content:center;padding-bottom:48px;box-sizing:border-box}
.stage{width:min(100vw,calc((100vh - 48px)*16/9));aspect-ratio:16/9;position:relative;overflow:hidden;background:#fff;box-shadow:0 8px 32px rgba(0,0,0,.35)}
.slide{position:absolute;inset:0;display:none;flex-direction:column;box-sizing:border-box}
.slide.active{display:flex}
.slide.lead .content{margin:auto;text-align:center}
.slide.invert{background:#111!important;color:#f3f3f3!important}
.split-bg{position:absolute;inset:0;display:flex;pointer-events:none}
.split-pane{height:100%}
.content{position:relative;z-index:1;flex:1;overflow:auto;padding:5% 6%;font-size:clamp(16px,2.4vw,28px);line-height:1.35}
.content img{max-width:100%;height:auto}
.content pre{background:rgba(127,127,127,.15);padding:12px;border-radius:8px;overflow:auto;white-space:pre-wrap}
.chrome{position:fixed;left:0;right:0;bottom:0;height:48px;display:flex;align-items:center;justify-content:center;gap:12px;background:#1e1e1e;color:#eee}
.chrome button{min-width:44px;min-height:40px;font-size:20px;border:0;border-radius:8px;background:transparent;color:inherit}
</style>
</head>
<body>
<div class="deck"><div class="stage" id="stage"></div></div>
<div class="chrome"><button type="button" id="prev">‹</button><span id="counter"></span><button type="button" id="next">›</button></div>
<script src="${markedSrc}"></script>
<script>
(function(){
  var slides = ${payload};
  var stage = document.getElementById('stage');
  var i = 0;
  function parseMd(md){
    if (window.marked && typeof marked.parse === 'function') return marked.parse(md || '');
    if (window.marked && typeof marked === 'function') return marked(md || '');
    return (md || '').replace(/[&<>]/g, function(c){ return ({'&':'&amp;','<':'&lt;','>':'&gt;'})[c]; });
  }
  function bgStyle(slide){
    var cover = (slide.backgrounds || []).filter(function(b){ return !b.split; }).pop();
    if (!cover) return '';
    return "background-image:url('"+String(cover.src).replace(/'/g,'%27')+"');background-size:"+cover.size+";background-position:center;background-repeat:no-repeat;";
  }
  function splitHtml(slide){
    var split = (slide.backgrounds || []).find(function(b){ return b.split; });
    if (!split) return '';
    var side = split.split === 'left' ? 'flex-start' : 'flex-end';
    var pct = split.splitPercent || 50;
    return '<div class="split-bg" style="justify-content:'+side+'"><div class="split-pane" style="width:'+pct+'%;background-image:url(\\''+String(split.src).replace(/'/g,'%27')+'\\');background-size:'+split.size+';background-position:center;background-repeat:no-repeat;"></div></div>';
  }
  function show(n){
    if (n < 0) n = 0;
    if (n > slides.length - 1) n = slides.length - 1;
    i = n;
    var s = slides[i] || { md: '', classNames: '', backgrounds: [] };
    stage.innerHTML = '<section class="slide active '+(s.classNames||'')+'" style="'+bgStyle(s)+'">'+splitHtml(s)+'<div class="content">'+parseMd(s.md)+'</div></section>';
    var c = document.getElementById('counter');
    if (c) c.textContent = (i + 1) + ' / ' + slides.length;
  }
  document.getElementById('prev').addEventListener('click', function(e){ e.stopPropagation(); show(i-1); });
  document.getElementById('next').addEventListener('click', function(e){ e.stopPropagation(); show(i+1); });
  document.addEventListener('keydown', function(e){
    if (e.key === 'ArrowRight' || e.key === ' ' || e.key === 'PageDown') { e.preventDefault(); show(i+1); }
    if (e.key === 'ArrowLeft' || e.key === 'PageUp') { e.preventDefault(); show(i-1); }
    if (e.key === 'F11') { e.preventDefault(); document.documentElement.requestFullscreen && document.documentElement.requestFullscreen(); }
  });
  document.addEventListener('click', function(e){
    if (e.target.closest && e.target.closest('.chrome,a,button')) return;
    if (e.clientX < window.innerWidth / 2) show(i-1); else show(i+1);
  });
  var startX = 0;
  document.addEventListener('touchstart', function(e){ if (e.touches.length === 1) startX = e.touches[0].clientX; }, {passive:true});
  document.addEventListener('touchend', function(e){
    var dx = e.changedTouches[0].clientX - startX;
    if (dx > 48) show(i-1); else if (dx < -48) show(i+1);
  }, {passive:true});
  show(0);
})();
</script>
</body></html>`;
}

module.exports = {
  isMarpMarkdown,
  parseDeck,
  renderMarpPreviewHtml,
  renderMarpPresentHtml,
  renderMarpPresentWebview,
};
