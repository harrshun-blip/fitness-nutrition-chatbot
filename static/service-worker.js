// Pulse service worker — caches the app shell so the PWA installs and the UI
// loads instantly (and offline). Chat responses still require a network call.

const CACHE = "pulse-shell-v1";
const SHELL = [
  ".",
  "index.html",
  "styles.css",
  "app.js",
  "manifest.webmanifest",
  "icons/icon-192.png",
  "icons/icon-512.png",
];

self.addEventListener("install", (event) => {
  event.waitUntil(caches.open(CACHE).then((c) => c.addAll(SHELL)));
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k)))
    )
  );
  self.clients.claim();
});

self.addEventListener("fetch", (event) => {
  const { request } = event;

  // Never cache API calls — always hit the network.
  if (request.url.includes("/api/")) return;

  // Cache-first for the app shell, falling back to network.
  event.respondWith(
    caches.match(request).then((cached) => cached || fetch(request))
  );
});
