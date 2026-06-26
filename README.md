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
