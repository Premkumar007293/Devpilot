# Beta Release Notes

## Release
DevPilot Beta 0.1.0-beta

## What is included
- Repository-aware local development without Docker
- SQLite-first setup with optional Redis/Celery
- GitHub OAuth and repository connection support
- Repository ingestion and source indexing
- Repository RAG and grounded developer Q&A
- Architecture analysis and explorer view
- Security, code, and repository insights
- Notification and global search support
- First-time onboarding and beta feedback collection

## What remains limited
- Live GitHub repository validation requires a valid GitHub app configuration.
- Full production deployment and public beta hosting remain pending.
- AI provider features are conditionally enabled and should be treated as optional.
- Analysis quality is intentionally evaluated with real-world repositories and manual review; it is not a guarantee of perfect accuracy.

## Known risks
- Large repositories may require more careful resource limits and ingestion tuning.
- AI context and retrieval quality depend on repository content and prompt design.
- Any private or sensitive repository must be analyzed only with explicit permission and secure environment variables.

## Upgrade advice
- Use SQLite for local development.
- Use PostgreSQL for beta-hosted or multi-user environments.
- Keep GitHub OAuth secrets and tokens in environment variables, not code.
- Re-run repository ingestion after any major update to the backend or indexing pipeline.

## Honest status
This release is a controlled beta and should be treated as a real validation milestone, not a stable 1.0 production release.
