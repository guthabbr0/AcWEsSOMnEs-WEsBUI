# Awesome WebUI Changelog

All notable Awesome WebUI (fork-specific) changes are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
