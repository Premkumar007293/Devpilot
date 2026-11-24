# Release Process

## Scope
This document governs the controlled beta release process for DevPilot.

## Versioning
The project follows semantic versioning:

- MAJOR: breaking changes or major architecture rewrite
- MINOR: backward-compatible improvements or feature additions
- PATCH: bug fixes and small compatibility fixes

Current beta version: 0.1.0-beta

## Release Gates
A release is only ready for beta when:

1. Backend tests pass.
2. Frontend production build passes.
3. SQLite local setup works without Docker.
4. Security-sensitive routes are protected by authenticated access.
5. Critical route exposure issues are resolved.
6. Feedback collection and onboarding flows are available.
7. Release notes and known limitations are published.
8. A deployment approval process is explicitly configured.

## Required validation before release
- Backend: `python -m pytest -q`
- Frontend: `npm run build`
- Health: backend `/api/v1/health` responds successfully
- Migration check: Alembic migrations apply in a clean environment
- Configuration check: `.env.example` matches the real environment contract

## Approval process
- Beta release requires explicit maintainer approval.
- No automatic deployment to production or public beta without review.
- Environment secrets must remain in GitHub Actions secrets or secure hosting env vars.
- Logs must not print secrets or tokens.

## Known beta limitations
- Real public beta deployment is still pending configuration and access.
- Some workflows require live GitHub app credentials for full validation.
- AI features are optional and credential-gated.

## Rollback plan
- Revert to previous version tag.
- Restore the prior database snapshot.
- Rebuild the vector index if necessary.
- Re-ingest repositories if upstream source content changed.
