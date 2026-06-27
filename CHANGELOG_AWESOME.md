# Awesome WebUI Changelog

All notable Awesome WebUI (fork-specific) changes are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.1] - 2026-06-27

### Added

- Added moderation appeal notifications so admins can see and react to ban appeals more easily.
- Added a global moderation center for reviewing bans, appeals, user risk, and moderation activity.
- Added user risk signals for moderation triage.
- Added connection change audit logging for admin visibility into connection edits.
- Added Open WebUI data migration helper script for easier migration from existing Open WebUI instances.
- Added web-search proxy support so search providers can route requests through configured proxies.
- Added API key pool support for OpenAI-compatible connections:
  - random key per request,
  - first key,
  - same key until failure,
  - switch key each message.
- Added channel keyboard shortcuts and Discord-style message editing behavior.
- Added large emoji rendering when a channel message contains only emoji.

### Changed

- Improved the Add/Edit Connection authentication UI with a `Single Key` / `Key Pool` switch.
- Updated Key Pool authentication so it shares the same methods as Single Key: `None`, `Bearer`, `Session`, `OAuth`, and `Entra ID`.
- Updated Key Pool behavior so multiple key inputs only appear for `Bearer` authentication.
- Improved channel emoji input handling and custom emoji replacement.
- Reworked channel emoji behavior to avoid treating every `:` as an emoji trigger.
- Improved custom emoji rendering so browser emoji can be replaced with configured SVG/image emoji where available.
- Improved model search/status feedback so users can tell when a model is actively searching.
- Improved moderation ban duration inputs with days, months, and minutes.
- Improved ban target selection for all models, DMs, and channels.
- Ported the custom audio player style into channel sound surfaces and added volume controls.
- Removed the experimental `Website` customization section from the 0.2.1 release line.

### Fixed

- Fixed Key Pool save/verify behavior for OpenAI-compatible connections.
- Fixed Key Pool accidentally forcing the authentication method back to `Bearer`.
- Fixed Single Key authentication methods being missing from Key Pool mode.
- Fixed a missing `WEB_SEARCH_PROXY_URL` config key.
- Fixed channel emoji regressions where invalid emoji could become malformed mention-like text.
- Fixed channel emoji regressions where valid `:emoji:` input could duplicate colons or fail to replace.
- Fixed duplicate emoji pickers appearing in channel input.
- Fixed pinned message state not syncing after unpinning from the top pinned-message surface.
- Fixed the model Access menu failing to open from the models page.
- Fixed the model quick-change menu showing `{name}` instead of `Name template`.
- Fixed banned users not being kicked out quickly enough after a website ban.
- Fixed stale ban views lingering after an admin unbanned a user.
- Fixed easier admin unban flows for website bans.
- Fixed mobile notes showing duplicate formatting toolbars.
- Fixed the mobile sidebar reopen area drifting offscreen.
- Fixed model health model names wrapping into unusable columns on mobile.

## [0.2.0] - 2026-06-25

### Added

- Ported Awesome WebUI onto Open WebUI `0.9.6`.
- Added user moderation bans:
  - website access bans,
  - model-specific chat bans,
  - channel typing bans,
  - duration/reason support,
  - user-visible ban reasons.
- Added an Open WebUI-styled moderation modal in the admin user list.
- Added selectable model/channel target lists for moderation bans instead of raw ID entry.
- Added model health monitoring and `/api/model-health` plus `/api/v1/model-health` routes.
- Added runtime-safe Alembic merge support for the Awesome WebUI and upstream migration histories.

### Changed

- Reworked Add/Edit Connection into grouped sections:
  - Connection,
  - Authentication,
  - Routing,
  - Models,
  - Tags,
  - Advanced.
- Reworked Awesome WebUI admin tools into compact, close-control layouts for Custom Emojis, Notification Sounds, and SSO Management.
- Replaced native notification sound previews with a compact custom audio player inspired by Discord-style file previews.
- Reworked Custom Emojis into a compact server-asset list with inline names, shortcodes, uploader metadata, copy, and delete actions.
- Reworked SSO Management provider cards so enabled providers sort first, configured providers stay near the top, and provider fields avoid browser autocomplete.
- Moved user notification sound choices to `Settings > Audio`.
- Changed notification sound flow so admins upload sounds and users select from the admin-managed library.
- Improved admin autosave behavior for Authorization, Notices, Custom Emojis, and Notification Sounds to avoid stale UI state overwriting focused edits.
- Updated README with Docker Compose and source install/run instructions.

### Fixed

- Restored Awesome WebUI admin settings after the 0.9.6 port:
  - Custom Emojis,
  - SSO Management,
  - Notices,
  - Authorization,
  - Notification Sounds.
- Restored Discord OAuth login/registration.
- Restored invite-only registration and invite code management.
- Restored guest notification and MOTD display.
- Fixed invite code creation under the 0.9.6 config system.
- Fixed SSO/OAuth runtime reload after admin config changes.
- Fixed persistent config handling guidance for SSO/OAuth.
- Fixed user presence/status being forced back to invisible after reloads or status changes.
- Fixed status emoji picker rendering behind modal backdrops.
- Fixed new users being unable to send messages in standard readable channels without explicit write grants.
- Restored model health surfaces that disappeared during the port.
- Preserved Awesome-specific connection fields such as proxy settings, prefix IDs, provider options, additional JSON, and model tags.

### Added

- Version update tracking now targets Awesome WebUI releases instead of upstream Open WebUI releases.
- Configurable GitHub release tracking via backend environment variables:
  - `WEBUI_GITHUB_REPOSITORY`
  - `WEBUI_GITHUB_URL`
  - `WEBUI_GITHUB_RELEASES_URL`
  - `WEBUI_GITHUB_RELEASES_LATEST_API_URL`
- Frontend release/update links now point to the Awesome WebUI repository.

### Changed

- `/api/version/updates` now parses release tags robustly (supports both `vX.Y.Z` and `X.Y.Z` tag naming).

## [0.1.1] - 2026-03-03

### Added

- Release automation groundwork:
  - GitHub release workflow for push-to-main and manual dispatch.
  - Optional PyPI publish workflow gate via `PYPI_PUBLISH` repository variable.
- Localization coverage for Awesome WebUI admin pages and settings labels across locales (English fallback keys added where missing).

### Changed

- Packaging updated for Awesome WebUI distribution:
  - Python package name set to `awesome-webui`.
  - Added `awesome-webui` CLI entrypoint.
  - Kept `open-webui` CLI entrypoint for backward compatibility.
- Version metadata resolution now supports both installed distribution names (`awesome-webui`, `open-webui`).

### Fixed

- Upstream sync/port merge conflicts resolved after rebasing fork customizations onto latest Open WebUI base.
- Restored `/static/static` assets from upstream baseline where required.

## [0.1.0] - 2026-03-03

### Added

- Initial Awesome WebUI release line.
- Dedicated Awesome WebUI admin area and feature set (authorization controls, notices, custom emojis, notification sounds, SSO management).
- GIF and emoji picker enhancements, including channel input integration and favorites workflows.
- Rich embed support work for common media/link providers.

### Changed

- Product naming and branding shifted from Open WebUI to Awesome WebUI in key user-facing surfaces.
