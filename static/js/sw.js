// Savage Homeschool OS - Service Worker

const CACHE_NAME = 'savage-homeschool-v1';
const urlsToCache = [
    '/',
    '/static/css/custom.css',
    '/static/js/app.js',
    '/static/css/bootstrap.min.css',
    '/static/js/bootstrap.bundle.min.js',
    '/static/css/all.min.css',
    '/static/webfonts/fa-solid-900.woff2',
    '/static/webfonts/fa-regular-400.woff2',
    '/static/webfonts/fa-brands-400.woff2'
];

// Install event
self.addEventListener('install', function(event) {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(function(cache) {
                console.log('Opened cache');
                return cache.addAll(urlsToCache);
            })
    );
});

// Fetch event
self.addEventListener('fetch', function(event) {
    event.respondWith(
        caches.match(event.request)
            .then(function(response) {
                // Return cached version or fetch from network
                return response || fetch(event.request);
            })
    );
});

// Activate event
self.addEventListener('activate', function(event) {
    event.waitUntil(
        caches.keys().then(function(cacheNames) {
            return Promise.all(
                cacheNames.map(function(cacheName) {
                    if (cacheName !== CACHE_NAME) {
                        console.log('Deleting old cache:', cacheName);
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
});

// Background sync for offline data
self.addEventListener('sync', function(event) {
    if (event.tag === 'background-sync') {
        event.waitUntil(doBackgroundSync());
    }
});

function doBackgroundSync() {
    // Sync offline data when connection is restored
    return fetch('/api/sync-offline-data', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            offlineData: getOfflineData()
        })
    })
    .then(function(response) {
        if (response.ok) {
            clearOfflineData();
            console.log('Offline data synced successfully');
        }
    })
    .catch(function(error) {
        console.error('Background sync failed:', error);
    });
}

function getOfflineData() {
    // Get offline data from IndexedDB or localStorage
    return JSON.parse(localStorage.getItem('offlineData') || '[]');
}

function clearOfflineData() {
    localStorage.removeItem('offlineData');
}

// Push notifications
self.addEventListener('push', function(event) {
    const options = {
        body: event.data ? event.data.text() : 'New notification from Savage Homeschool OS',
        icon: '/static/images/icon-192x192.png',
        badge: '/static/images/badge-72x72.png',
        vibrate: [100, 50, 100],
        data: {
            dateOfArrival: Date.now(),
            primaryKey: 1
        },
        actions: [
            {
                action: 'explore',
                title: 'View',
                icon: '/static/images/checkmark.png'
            },
            {
                action: 'close',
                title: 'Close',
                icon: '/static/images/xmark.png'
            }
        ]
    };

    event.waitUntil(
        self.registration.showNotification('Savage Homeschool OS', options)
    );
});

// Notification click event
self.addEventListener('notificationclick', function(event) {
    event.notification.close();

    if (event.action === 'explore') {
        event.waitUntil(
            clients.openWindow('/')
        );
    }
}); 