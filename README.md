# Awesome WebUI 👋
>This `README.md` is also available in other languages:
<br>\- 🇺🇸 English <small>[You are currently here!]</small>
<br>\- 🇷🇺 [Русский](readme.ru.md)

> "I wish using Open WebUI sucked a little less!"

So, I am here to fix that. Awesome WebUI is a **fork** of [Open WebUI](https://github.com/open-webui/open-webui) focused on improving the experience for both admins and users. Let us get into the details.
<small>(hah, you see what I did there?)</small>

# List of Changes
## Admin Panel
### #1. Models Tab

![model list showing openai models: gpt 5, gpt 5.1, gpt 5.2, codex](preview/image.png)
```diff
+ Added the ability to multi-select models
+ Middle-clicking a model opens its editor in a new tab
+ Multi-select now supports bulk changes for icon, name, access, and enable/disable state
```

### #2. Connections Tab
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
- [ ] `HIGH` Invite-code system
- [ ] `HIGH` Ability to change registration from the website (OAuth providers, etc.)
- [ ] `MEDIUM` System notice and MOTD
- [ ] `LOW` Custom emojis
- [ ] `LOW` Notification sounds for channels
- [ ] `LOW` Discord OAuth

### User Interface
- [ ] `LOW` Add GIFs to channels
- [ ] `LOW` Notification changes for channels
- [ ] `LOW` Integrate GIF search with emojis and custom emojis

### General
- [ ] `?` Add migration support for files (such as DB) from default Open WebUI
- [ ] `XLOW` Add translations for new features
