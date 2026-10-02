// The service worker that lets the site be installed as an app. It goes to
// the network first for everything, so a reader online always gets the
// current pages and figures, and keeps a copy of what was read so a page
// opened before still opens without a connection. Downloads (PDF, slides,
// CSV) are not kept, and nothing from other sites is touched.
var CACHE = 'sir-v1';
self.addEventListener('install', function () { self.skipWaiting(); });
self.addEventListener('activate', function (e) {
  e.waitUntil(caches.keys().then(function (keys) {
    return Promise.all(keys.filter(function (k) { return k !== CACHE; }).map(function (k) { return caches.delete(k); }));
  }).then(function () { return self.clients.claim(); }));
});
self.addEventListener('fetch', function (e) {
  var req = e.request, url = new URL(req.url);
  if (req.method !== 'GET' || url.origin !== location.origin || /\.(pdf|pptx|csv)$/i.test(url.pathname)) return;
  e.respondWith(fetch(req).then(function (res) {
    if (res.ok && res.type === 'basic') { var copy = res.clone(); caches.open(CACHE).then(function (c) { c.put(req, copy); }); }
    return res;
  }).catch(function () {
    return caches.match(req).then(function (hit) {
      return hit || (req.mode === 'navigate' ? caches.match(new URL('./', self.registration.scope).href) : undefined) || Response.error();
    });
  }));
});
