'use strict';

function adjustColor(color, percent) {
  const value = parseInt(color, 16);
  const adjustment = Math.round(2.55 * percent);
  const red = (value >> 16) + adjustment;
  const blue = ((value >> 8) & 0x00ff) + adjustment;
  const green = (value & 0x0000ff) + adjustment;
  const clamp = (channel) => Math.max(0, Math.min(255, channel));

  return (0x1000000 + clamp(red) * 0x10000 + clamp(blue) * 0x100 + clamp(green))
    .toString(16)
    .slice(1);
}

function initializeDiscordWidget(widget) {
  if (widget.dataset.initialized === 'true') return;
  widget.dataset.initialized = 'true';

  const id = widget.getAttribute('id');
  const color = widget.getAttribute('color') || '#5865f2';
  const buttonColor = widget.getAttribute('buttonColor') || color;
  const body = document.createElement('widget-body');
  const header = document.createElement('widget-header');
  const logo = document.createElement('widget-logo');
  const count = document.createElement('widget-header-count');
  const serverHeader = document.createElement('widget-server-header');
  const serverIcon = document.createElement('img');
  const serverName = document.createElement('span');
  const footer = document.createElement('widget-footer');
  const footerInfo = document.createElement('widget-footer-info');
  const joinButton = document.createElement('widget-button-join');
  let inviteUrl = widget.getAttribute('invite-url');
  const defaultLogo =
    'https://cdn.jsdelivr.net/gh/dip-land/discord_widget/discord-logo-white.svg';

  widget.style.height = widget.getAttribute('height') || '500px';
  widget.style.width = widget.getAttribute('width') || '350px';
  widget.style.setProperty('--color', color);
  widget.style.setProperty(
    '--bgColor',
    widget.getAttribute('backgroundColor') || '#0c0c0d',
  );
  widget.style.setProperty(
    '--textColor',
    widget.getAttribute('textColor') || '#fff',
  );
  widget.style.setProperty('--buttonColor', buttonColor);
  widget.style.setProperty(
    '--buttonHoverColor',
    widget.getAttribute('buttonHoverColor') ||
      `#${adjustColor(buttonColor.replace('#', ''), -10)}`,
  );
  widget.style.setProperty(
    '--statusColor',
    widget.getAttribute('statusColor') || '#858585',
  );

  try {
    const logoUrl = new URL(widget.getAttribute('logo') || defaultLogo);
    logo.style.backgroundImage = `url("${logoUrl.href}")`;
  } catch {
    body.textContent = 'Logo is a malformed URL.';
  }

  header.append(logo, count);
  serverIcon.src = '/uploads/discord-server-icon.png';
  serverIcon.alt = '';
  serverName.textContent = "Dice N' Slice";
  serverHeader.append(serverIcon, serverName);
  footerInfo.textContent = widget.getAttribute('footerText') || '';
  joinButton.textContent = 'Join';
  joinButton.setAttribute('role', 'link');
  joinButton.setAttribute('tabindex', '0');
  const openInvite = () => {
    if (inviteUrl) window.open(inviteUrl, '_blank', 'noopener,noreferrer');
  };
  joinButton.addEventListener('click', openInvite);
  joinButton.addEventListener('keydown', (event) => {
    if (event.key === 'Enter' || event.key === ' ') openInvite();
  });
  footer.append(footerInfo, joinButton);
  widget.append(header, serverHeader, body, footer);

  if (!id) {
    body.textContent = 'No Discord server ID was specified.';
    return;
  }

  fetch(`https://discord.com/api/guilds/${encodeURIComponent(id)}/widget.json`)
    .then((response) => {
      if (!response.ok)
        throw new Error(`Discord widget request failed: ${response.status}`);
      return response.json();
    })
    .then((data) => {
      const strong = document.createElement('strong');
      strong.textContent = String(data.presence_count || 0);
      count.append(strong, ' Members Online');

      if (data.instant_invite) {
        inviteUrl = data.instant_invite;
      }

      for (const user of data.members || []) {
        const member = document.createElement('widget-member');
        const avatar = document.createElement('widget-member-avatar');
        const avatarImage = document.createElement('img');
        const status = document.createElement(
          `widget-member-status-${user.status}`,
        );
        const name = document.createElement('widget-member-name');
        const statusText = document.createElement('widget-member-status-text');

        avatarImage.src = user.avatar_url;
        avatarImage.alt = '';
        status.classList.add('widget-member-status');
        name.textContent = user.username;
        statusText.textContent = user.game?.name || '';
        avatar.append(avatarImage, status);
        member.append(avatar, name, statusText);
        body.append(member);
      }
    })
    .catch(() => {
      body.textContent = 'The Discord member list is currently unavailable.';
    });
}

function initializeDiscordWidgets() {
  document.querySelectorAll('discord-widget').forEach(initializeDiscordWidget);
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initializeDiscordWidgets, {
    once: true,
  });
} else {
  initializeDiscordWidgets();
}
