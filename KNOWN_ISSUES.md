# Known Issues

## Current Status
- **Resolved Configuration Mismatch:** Previous port 8001 / port 8000 discrepancies and duplicate callback endpoints have been resolved. The canonical callback URL is `http://localhost:8000/api/v1/github/callback`.
- **GitHub Developer Settings Requirement:** The registered OAuth App on GitHub must specify `http://localhost:8000/api/v1/github/callback` as its Authorization callback URL. Any divergence (e.g. port 8001, trailing slashes, or frontend paths) triggers GitHub's `"The redirect_uri is not associated with this application"` or browser `ERR_CONNECTION_REFUSED`.
- Real GitHub OAuth app credentials are required for true end-to-end repository connection and live verification.
- Public production deployment is not authorized or validated in this environment.
- Fresh-machine Windows validation is still recommended for a clean install or security review.

## Product/Engineering Notes
- The frontend and backend both run locally and pass automated validation; this confirms the code path is stable for local dev.
- Advanced AI engineering endpoints remain repository-aware and grounded in source, but live AI provider output still depends on configured credentials.
- Secret handling and OAuth binding are implemented in code, but a live GitHub app must still be configured with the canonical callback URL to complete live verification.

## Unresolved Items
- Real external deployment environment access.
- Production-grade organization quotas, analytics, and public launch workflows.
- Live repository sync verification against a real GitHub organization or private repo using valid user permissions.
