# Decisions Log

## 2026-11-03
- Keep the current architecture intact and extend it rather than replacing the platform.
- Preserve SQLite as the default local database and keep Redis/Celery optional.
- Treat GitHub OAuth and AI provider credentials as required external dependencies, not assumed defaults.
- Use repository file content and existing AST/RAG metadata as the evidence base for AI engineering workflows.
- Require all advanced AI outputs to clearly separate evidence, hypotheses, and uncertainty.

## Design Notes
- Repository-wide AI intelligence should be grounded in repository files and their graph relationships.
- Refactoring and test generation should never modify source files automatically.
- Authentication and repository access remain mandatory guards before AI or analysis endpoints return results.
- Final reports should be honest: PASS/PARTIAL/BLOCKED/NOT IMPLEMENTED only when verified.
