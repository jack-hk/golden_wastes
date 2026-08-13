'use strict';

const storageKey = 'golden-wastes-random-facts-seen';

function getSeenFacts() {
  try {
    const seen = JSON.parse(sessionStorage.getItem(storageKey) || '[]');
    return Array.isArray(seen) ? seen : [];
  } catch {
    return [];
  }
}

function saveSeenFacts(seen) {
  try {
    sessionStorage.setItem(storageKey, JSON.stringify(seen));
  } catch {
    // The fact picker still works when browser storage is unavailable.
  }
}

function showRandomFact(container) {
  const facts = Array.from(
    container.querySelectorAll('[data-random-fact-item]'),
  );
  if (!facts.length) return;

  let seen = getSeenFacts().filter(
    (index) => Number.isInteger(index) && index >= 0 && index < facts.length,
  );
  let unseen = facts
    .map((fact, index) => index)
    .filter((index) => !seen.includes(index));
  const reroll = container.querySelector('[data-random-fact-reroll]');
  const empty = container.querySelector('[data-random-fact-empty]');

  facts.forEach((fact) => {
    fact.hidden = true;
  });

  if (!unseen.length) {
    seen = [];
    unseen = facts.map((fact, index) => index);
  }

  empty.hidden = true;
  const index = unseen[Math.floor(Math.random() * unseen.length)];
  facts[index].hidden = false;
  seen.push(index);
  saveSeenFacts(seen);
  reroll.disabled = false;
}

function initializeRandomFacts() {
  document.querySelectorAll('[data-random-fact]').forEach((container) => {
    const reroll = container.querySelector('[data-random-fact-reroll]');
    reroll.addEventListener('click', () => showRandomFact(container));
    showRandomFact(container);
  });
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initializeRandomFacts, {
    once: true,
  });
} else {
  initializeRandomFacts();
}
