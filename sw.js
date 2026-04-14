// ═══════════════════════════════════════════════
// SERVICE WORKER - Nampula é a Cena PWA
// ═══════════════════════════════════════════════

const CACHE_NAME = 'nampula-cena-v1';
const CACHE_STATIC = [
  '/nampula-e-a-cena/',
  '/nampula-e-a-cena/index.html',
  '/nampula-e-a-cena/dados.json',
  '/nampula-e-a-cena/manifest.json',
  'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css'
];

// Instalar e guardar cache
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      console.log('[SW] Cache instalado');
      return cache.addAll(CACHE_STATIC);
    })
  );
  self.skipWaiting();
});

// Activar e limpar caches antigos
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(
        keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k))
      )
    )
  );
  self.clients.claim();
});

// Estratégia: Network First (tenta internet, se falhar usa cache)
self.addEventListener('fetch', event => {
  // Ignora requisições externas que não sejam FontAwesome
  if (!event.request.url.startsWith(self.location.origin) &&
      !event.request.url.includes('cdnjs.cloudflare.com')) {
    return;
  }

  event.respondWith(
    fetch(event.request)
      .then(response => {
        // Guarda cópia no cache
        const resClone = response.clone();
        caches.open(CACHE_NAME).then(cache => {
          cache.put(event.request, resClone);
        });
        return response;
      })
      .catch(() => {
        // Se sem internet, usa cache
        return caches.match(event.request).then(cached => {
          if (cached) return cached;
          // Fallback para a página principal
          return caches.match('/nampula-e-a-cena/index.html');
        });
      })
  );
});
