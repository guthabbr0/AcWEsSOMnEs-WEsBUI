# Awesome WebUI Changelog

All notable Awesome WebUI (fork-specific) changes are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
