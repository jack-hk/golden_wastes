'use strict';

const notificationStorageKey =
  'golden-wastes-home-map-notification-dismissed-v2';

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
  const map = document.querySelector('.interactive-map');
  if (!notification || !map || hasSeenNotification()) return;

  const allowedViews = (notification.dataset.allowedViews || '')
    .split(',')
    .map((view) => view.trim().toLowerCase());
  const viewport =
    window.innerWidth < 768
      ? 'mobile'
      : window.innerWidth < 1200
        ? 'tablet'
        : 'desktop';
  if (!allowedViews.includes(viewport)) return;

  notification.hidden = false;
  requestAnimationFrame(() => {
    notification.classList.add('is-visible', 'is-flashing');
  });

  const hidePermanently = () => {
    rememberNotification();
    notification.classList.remove('is-visible');
    notification.hidden = true;
  };

  const scrollToMap = () => {
    map.scrollIntoView({
      behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches
        ? 'auto'
        : 'smooth',
      block: 'start',
    });
  };

  notification.addEventListener('animationend', () => {
    notification.classList.remove('is-flashing');
  });
  notification
    .querySelector('[data-home-map-notification-action]')
    ?.addEventListener('click', scrollToMap);

  notification
    .querySelector('[data-home-map-notification-close]')
    ?.addEventListener('click', (event) => {
      event.stopPropagation();
      hidePermanently();
    });

  const observer = new IntersectionObserver(
    (entries) => {
      if (!entries.some((entry) => entry.isIntersecting)) return;
      hidePermanently();
      observer.disconnect();
    },
    { threshold: 0.05 },
  );
  observer.observe(map);
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initializeHomeMapNotification, {
    once: true,
  });
} else {
  initializeHomeMapNotification();
}
