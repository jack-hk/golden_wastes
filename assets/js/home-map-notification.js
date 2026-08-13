'use strict';

const notificationStorageKey = 'golden-wastes-home-map-notification-seen';
const desktopMedia = window.matchMedia('(min-width: 1200px)');

function hasSeenNotification() {
  try {
    return localStorage.getItem(notificationStorageKey) === 'true';
  } catch {
    return false;
  }
}

function rememberNotification() {
  try {
    localStorage.setItem(notificationStorageKey, 'true');
  } catch {
    // The notification can still be shown when browser storage is unavailable.
  }
}

function initializeHomeMapNotification() {
  const notification = document.querySelector('[data-home-map-notification]');
  if (!notification || !desktopMedia.matches || hasSeenNotification()) return;

  rememberNotification();
  notification.hidden = false;
  requestAnimationFrame(() => notification.classList.add('is-visible'));

  window.setTimeout(() => {
    notification.classList.remove('is-visible');
    window.setTimeout(() => {
      notification.hidden = true;
    }, 250);
  }, 4000);
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initializeHomeMapNotification, {
    once: true,
  });
} else {
  initializeHomeMapNotification();
}
