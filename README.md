# Awesome WebUI 👋

> This `README.md` is also available in other languages:
> <br>\- 🇺🇸 English <small>[You are currently here!]</small>
> <br>\- 🇷🇺 [Русский](README.RU.MD)

> "I wish using Open WebUI sucked a little less!"

So, I am here to fix that. Awesome WebUI is a **fork** of [Open WebUI](https://github.com/open-webui/open-webui) focused on improving the experience for both admins and users. Let us get into the awesome changes.
<small>(hah, you see what I did there?)</small>

# Install & Run

## Docker Compose

This is the easiest way to run Awesome WebUI with persistent data:

```bash
git clone https://github.com/mehhovcki-dev/awesome-webui.git
cd awesome-webui
cp .env.example .env
docker compose up -d --build
```

Open `http://localhost:3000`.

The default compose file stores data in Docker volumes:

- `open-webui` -> `/app/backend/data`
- `ollama` -> `/root/.ollama`

Keep these enabled in `.env` if you configure SSO/OAuth, connections, notices, custom emojis, or other admin settings from the UI:

```env
ENABLE_PERSISTENT_CONFIG=true
ENABLE_OAUTH_PERSISTENT_CONFIG=true
```

## Run From Source

Use this when developing the frontend/backend locally.

```bash
git clone https://github.com/mehhovcki-dev/awesome-webui.git
cd awesome-webui
cp .env.example .env
npm install
```

Backend:

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
bash start.sh
```

Frontend dev server, in another terminal:

```bash
npm run dev
```

Open the frontend URL printed by Vite, usually `http://localhost:5173`.

For a production-style frontend build:

```bash
npm run build
```

## Migrate From Open WebUI

If you already run Open WebUI, you can copy its persistent data into Awesome WebUI before the first Awesome WebUI start. Stop both instances first so `webui.db` is not being written while it is copied.

Local/source installs:

```bash
python3 scripts/migrate_open_webui_data.py \
  --source /path/to/open-webui/backend/data \
  --target backend/data
```

Docker volume installs:

```bash
docker run --rm \
  -v open-webui:/from:ro \
  -v awesome-webui:/to \
  -v "$PWD/scripts:/scripts:ro" \
  python:3.11-slim \
  python /scripts/migrate_open_webui_data.py --source /from --target /to
```

The tool copies chats, users, files, uploads, vector DB data, admin config, connections, OAuth/SSO config, notices, emojis, sounds, and other persistent Open WebUI data. If the Awesome WebUI target already has data, it writes a backup archive before overwriting files. After copying, start Awesome WebUI once and let its startup migrations upgrade `webui.db`.

Useful flags:

```bash
--dry-run      # preview what would be copied
--skip-cache   # skip cache/ to make the migration smaller
--backup-dir   # choose where target backups are written
```

If users get logged out after migration, reuse the same `WEBUI_SECRET_KEY` from the old Open WebUI instance.

# Awesome WebUI 0.2.1 Update Log

Awesome WebUI 0.2.1 is a polish and stabilization release for the 0.2.x port. It focuses on moderation, connection key pools, channel emoji behavior, search proxies, migration tooling, and mobile fixes.

```diff
+ Added a global moderation center, appeal notifications, user risk signals, and connection change audit logging
+ Improved website bans so banned users are kicked out quickly, login stays blocked, and admins can unban more easily
+ Added Open WebUI data migration tooling for moving existing persistent data into Awesome WebUI
+ Added web-search proxy support
+ Added OpenAI-compatible API key pools with first/random/sticky-until-failure/switch-each-message strategies
+ Fixed Key Pool authentication so it keeps the same methods as Single Key: None, Bearer, Session, OAuth, and Entra ID
+ Improved Add/Edit Connection authentication UX with a clearer Single Key / Key Pool switch
+ Improved channel emoji parsing, custom emoji replacement, duplicate picker behavior, and emoji-only message sizing
+ Added Discord-style channel message editing and keyboard shortcuts
+ Fixed pinned-message state syncing after unpinning
+ Fixed model Access menu failures and the model quick-change {name} label bug
+ Fixed mobile Notes duplicate toolbars, sidebar reopen positioning, and model-health name wrapping
+ Removed the experimental Website customization section from the 0.2.1 release line
```

# Awesome WebUI 0.2.0 Update Log

Awesome WebUI 0.2.0 rebases the fork onto Open WebUI `0.9.6` while preserving the Awesome WebUI feature set from the `0.8.11` era.

```diff
+ Ported Awesome WebUI onto Open WebUI 0.9.6
+ Preserved Awesome admin settings: Authorization, SSO Management, Notices, Custom Emojis, and Notification Sounds
+ Restored Discord OAuth login/registration and provider-level login/signup allowlists
+ Restored invite-only registration, invite code generation, copying, deletion, prefixing, expiry, reuse, and max-use controls
+ Restored guest notification and MOTD surfaces
+ Restored custom emoji rendering, emoji picker integration, and status emoji layering behavior
+ Restored notification sounds, with admin-uploaded sounds selectable by users in Settings > Audio
+ Restored user presence/status persistence instead of forcing users invisible after reloads
+ Restored model health monitoring and model-health API/page integration
+ Added user moderation bans for website access, model chat access, and channel typing restrictions with visible reasons
+ Added Open WebUI-styled moderation UI for admins
+ Improved ban targeting for models/channels with selectable lists instead of raw ID entry
+ Improved Add/Edit Connection modal layout with grouped sections for endpoint, authentication, routing, models, tags, and advanced options
+ Improved Awesome WebUI admin UX for Custom Emojis, Notification Sounds, and SSO Management with compact close-control layouts
+ Added a custom compact notification sound player instead of native browser audio controls
+ Reworked Custom Emojis into a Discord-inspired asset list with inline edit, copy, uploader, and delete controls
+ Reworked SSO Management provider cards so enabled providers sort first and OAuth fields avoid browser autocomplete
+ Improved connection persistence guidance for SSO/OAuth and admin-managed provider settings
+ Hardened invite and config persistence paths for the 0.9.6 config system
+ Added migration support for the Awesome/Open WebUI multi-head Alembic history
```

# List of Changes

## Admin Panel

### #1. Models Tab

![model list showing openai models: gpt 5, gpt 5.1, gpt 5.2, codex](preview/image.png)

```diff
+ Added the ability to multi-select models
+ Middle-clicking a model opens its editor in a new tab
+ Multi-select now supports bulk changes for icon, name, access, and enable/disable state
```

### #2. Awesome WebUI Tab (Authorization + SSO Management)

![preview of authorization settings in Awesome WebUI tab](preview/image3.png)

```diff
+ Added a dedicated "Awesome WebUI" admin tab with "Authorization" and "SSO Management" sections
+ Added auth method controls: Registration, Email+Password signup, SSO logins, and SSO account creation
+ Added provider-level SSO access control for login/signup with quick "All/None" actions
```

![preview of invite-only settings in Awesome WebUI tab](preview/image4.png)

```diff
+ Added invite-only access controls with creator scope (Admin Only / Selected Groups / All Users)
+ Added invite defaults: code length, expiry presets + custom date/time, prefix, reusable toggle, and max uses
+ Added invite code management actions (generate, copy, delete)
```

![preview of sso management settings in Awesome WebUI tab](preview/image5.png)

```diff
+ Added full SSO Management for OAuth providers directly from admin UI
+ Added provider toggles and editable OAuth settings (Google, Microsoft, GitHub, Discord, OIDC, Feishu)
+ Added advanced OAuth runtime settings (merge by email, timeout, audience)
```

### #2.1 Notices (System Notice + MOTD)

![preview of notices interface in Awesome WebUI](preview/image6.png)

```diff
+ Added a "Notices" section inside Awesome WebUI for managing guest and user-facing notifications
+ Added Guest Notification controls (enable/disable, custom title, custom description with Markdown support)
+ Added MOTD controls (enable/disable and custom MOTD text) for signed-in users
```

<p>
  <img src="preview/image7.png" alt="guest notification showcase on auth page" width="49%" />
  <img src="preview/image8.png" alt="motd showcase for signed-in users" width="49%" />
</p>

```diff
+ Guest Notification now appears above the sign-in/sign-up header for unauthenticated users
+ MOTD appears as a bottom-right message card for registered users with dismiss actions
```

### #3. Connections Tab

<small>
* - "provider" is used here as another term for "connection".
<br>¹ - untested feature, please report any issues.
<br>² - using SOCKS proxies adds dependency: `aiohttp-socks`.
</small>

![preview of changes to the connections list](preview/image1.png)

```diff
+ Split layout into 3 sections (OpenAI, Ollama, Additional Settings)
+ Added left-aligned "Add Connection" actions and clearer "Added Connections" list grouping
+ Made provider* base URLs clickable
+ Added preview of each provider's* tags and prefix
```

![preview of changes to the connections list](preview/image2.png)

```diff
+ Added support for proxies (HTTP/SOCKS4/SOCKS5) for provider* connections¹²
+ Added support for additional JSON merged into requests
```

## TODO Roadmap

Planned improvements and QoL changes. If you want to suggest something for Awesome WebUI, [post an idea here](https://github.com/mehhovcki-dev/awesome-webui/discussions/categories/ideas).

Priority guide: `HIGH` (soon), `MEDIUM`, `LOW`, `XLOW` (later).

### Admin Panel

- [x] `HIGH` Invite-code system
- [x] `HIGH` Ability to change registration from the website (OAuth providers, etc.)
- [x] `MEDIUM` System notice and MOTD
- [x] `LOW` Custom emojis
- [x] `LOW` Notification sounds for channels
- [x] `LOW` Discord OAuth

### User Interface

- [x] `LOW` Add GIFs to channels
- [x] `LOW` Notification changes for channels
- [x] `LOW` Integrate GIF search with emojis and custom emojis

### General

- [x] `?` Add migration support for files (such as DB) from default Open WebUI
- [x] `XLOW` Add translations for new features
