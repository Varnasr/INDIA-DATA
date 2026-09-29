/* Languages: English, Hindi, Urdu (right to left) and Telugu.

   Load this first, in <head>. It decides the language (?lang= in the address,
   else the reader's last choice, else English), sets <html lang> and dir,
   loads the dictionary and the script's font, and defines L().

   Two kinds of text are translated:
   - Sentences built by a page's script go through L('English template with
     {placeholders}', {placeholders: values}). The English template is the
     key; scripts/check_i18n.py fails CI if any key lacks a translation.
   - Fixed text in the markup is translated by L.apply(), which sir.js calls
     before the page's own script runs. A unit is an element whose children
     are all inline (a, b, strong, em, span, br, code...); its innerHTML is
     the key. Other elements have their own text nodes translated one by
     one, as are the children of an element marked data-i18n-each (a row of
     links whose addresses change from page to page). Attributes (aria-label, placeholder, title), the page title and
     the meta description are keys too. Mark anything that must stay as it
     is with data-no-i18n.

   Figures stay in Western digits with Indian grouping (6,62,063), and names
   of places, parties and people stay as the data spells them. */
(function () {
  'use strict';
  var LANGS = {
    en: { name: 'English', dir: 'ltr' },
    hi: { name: 'हिन्दी', dir: 'ltr', font: 'Noto+Sans+Devanagari:wght@400;600;700' },
    ur: { name: 'اردو', dir: 'rtl', font: 'Noto+Nastaliq+Urdu:wght@400;700' },
    te: { name: 'తెలుగు', dir: 'ltr', font: 'Noto+Sans+Telugu:wght@400;600;700' }
  };
  // Until a native reader has signed off the translations, the menu is not
  // shown and a language is reached only by a link carrying ?lang=. Set this
  // to true to put the menu in every page's header.
  var MENU = false;
  var here = document.currentScript ? document.currentScript.src : '';
  var base = here.slice(0, here.lastIndexOf('/') + 1);
  var params = new URLSearchParams(location.search);
  var asked = params.get('lang'), saved = null;
  try { saved = localStorage.getItem('sir-lang'); } catch (e) {}
  var lang = LANGS[asked] ? asked : (MENU && LANGS[saved] ? saved : 'en');
  if (LANGS[asked]) { try { localStorage.setItem('sir-lang', asked); } catch (e) {} }
  var collect = params.has('i18n-collect');
  var html = document.documentElement;
  html.lang = lang;
  html.dir = LANGS[lang].dir;
  html.setAttribute('data-lang', lang);
  window.SIR_DICT = window.SIR_DICT || {};
  if (lang !== 'en') {
    document.write('<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>' +
      '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=' + LANGS[lang].font + '&display=swap">' +
      '<script src="' + base + 'i18n/' + lang + '.js"><\/script>');
  }

  function norm(s) { return s.replace(/\s+/g, ' ').trim(); }
  var seen = {};
  var L = window.L = function (key, vars) {
    if (collect) seen[key] = 1;
    var s = (lang !== 'en' && window.SIR_DICT[key]) || key;
    if (vars) s = s.replace(/\{(\w+)\}/g, function (m, k) { return vars[k] != null ? vars[k] : m; });
    return s;
  };
  L.lang = lang;
  L.langs = LANGS;
  L.seen = seen;

  // ------------------------------------------------------ fixed text in markup
  var INLINE = { A: 1, B: 1, STRONG: 1, EM: 1, I: 1, SPAN: 1, BR: 1, CODE: 1, SUP: 1, SUB: 1, SMALL: 1, ABBR: 1, TIME: 1 };
  var SKIP = { SCRIPT: 1, STYLE: 1, SVG: 1, CANVAS: 1, TEXTAREA: 1, svg: 1, NOSCRIPT: 1 };
  var ATTRS = ['aria-label', 'placeholder', 'title'];
  var statics = {};
  function has(s) { return /[A-Za-z]/.test(s); }
  function tr(key) {
    if (collect) { statics[key] = 1; return null; }
    if (lang === 'en') return null;
    return window.SIR_DICT[key] || null;
  }
  function attrs(el) {
    ATTRS.forEach(function (a) {
      var v = el.getAttribute(a);
      if (v && has(v)) { var t = tr(norm(v)); if (t) el.setAttribute(a, t); }
    });
  }
  function isUnit(el) {
    for (var c = el.firstElementChild; c; c = c.nextElementSibling) {
      if (!INLINE[c.tagName] || c.hasAttribute('data-no-i18n')) return false;
      if (c.firstElementChild && !isUnit(c)) return false;
    }
    return true;
  }
  function walk(el) {
    if (SKIP[el.tagName] || el.hasAttribute('data-no-i18n')) return;
    attrs(el);
    if (el.firstElementChild && el.tagName !== 'BODY' && !el.hasAttribute('data-i18n-each') && isUnit(el) && has(el.textContent)) {
      var key = norm(el.innerHTML), t = tr(key);
      if (t) el.innerHTML = t;
      el.querySelectorAll('*').forEach(attrs);
      return;
    }
    for (var n = el.firstChild; n; n = n.nextSibling) {
      if (n.nodeType === 3) {
        var raw = n.nodeValue;
        if (!has(raw)) continue;
        var k = norm(raw), tt = tr(k);
        if (tt) n.nodeValue = raw.replace(k, tt);
      } else if (n.nodeType === 1) walk(n);
    }
  }
  L.apply = function (root) {
    root = root || document.body;
    var t = tr(norm(document.title)); if (t) document.title = t;
    var md = document.querySelector('meta[name="description"]');
    if (md) { var tm = tr(norm(md.content)); if (tm) md.content = tm; }
    walk(root);
    // The language menu, beside the other controls in the header.
    // It goes after the Bihar/Hyderabad switch, so a phone can put the two
    // side by side on the second line of the header.
    var ctl = document.querySelector('header.top .controls'), sw = document.querySelector('header.top .switch');
    if (ctl && (MENU || lang !== 'en') && !document.getElementById('lang')) {
      var opts = Object.keys(LANGS).map(function (k) { return '<option value="' + k + '"' + (k === lang ? ' selected' : '') + ' lang="' + k + '">' + LANGS[k].name + '</option>'; }).join('');
      var sel = '<select id="lang" aria-label="' + L('Language') + '" data-no-i18n>' + opts + '</select>';
      if (sw) sw.insertAdjacentHTML('afterend', sel); else ctl.insertAdjacentHTML('afterbegin', sel);
      document.getElementById('lang').addEventListener('change', function () {
        try { localStorage.setItem('sir-lang', this.value); } catch (e) {}
        var u = new URL(location.href); u.searchParams.set('lang', this.value); location.href = u.toString();
      });
    }
    // A translation is shown with a notice until a reviewer has read it.
    if (lang !== 'en' && !document.getElementById('i18n-note')) {
      var m = document.querySelector('main') || document.body;
      var en = new URL(location.href); en.searchParams.set('lang', 'en');
      m.insertAdjacentHTML('beforebegin', '<p id="i18n-note" class="i18n-note" role="note">' + L('This translation is awaiting review. Where it differs from the English page, the English page is correct.') + ' <a href="' + en.toString() + '" lang="en" dir="ltr">English</a></p>');
    }
    // Keep the chosen language when following a link to another page here.
    if (lang !== 'en') document.addEventListener('click', function (e) {
      var a = e.target.closest && e.target.closest('a[href]'); if (!a) return;
      var u = new URL(a.href, location.href);
      if (u.origin !== location.origin || u.searchParams.has('lang') || /\.(json|pdf|png|csv|docx|pptx)$/.test(u.pathname)) return;
      u.searchParams.set('lang', lang); a.href = u.toString();
    });
  };
  L.collected = function () { return { statics: Object.keys(statics), dynamic: Object.keys(seen) }; };
})();
