# Changelog

All notable changes to DevPilot are documented here.

## [0.1.0-beta] - 2026-11-03

### Added
- Docker-free local setup for Windows and macOS/Linux developers.
- SQLite-first development configuration with optional Redis/Celery support.
- GitHub OAuth flow and repository connection flow.
- Repository ingestion and metadata persistence.
- Repository-aware RAG and Q&A flow.
- Architecture analysis scaffolding and explorer UI.
- Notification and global search integration.
- Beta feedback API and onboarding flow.

### Changed
- Preserved the existing FastAPI + React architecture and premium dark UI.
- Kept PostgreSQL support for future beta production use without requiring Docker.
- Improved the backend health and diagnostics surface.

### Fixed
- Corrected GitHub bearer-token generation issues.
- Resolved route exposure issues for notifications and search endpoints.
- Improved API and frontend integration around repository architecture data.

### Known limitations
- Real GitHub OAuth and ingestion still require valid GitHub app credentials.
- Live beta deployment remains pending until environment access and approval are available.
- AI provider features are conditional on configured credentials and are not a substitute for a full analysis system.
- The beta release is intended for controlled external validation, not a claim of production stability.
