# Windows Installation Verification

## Status
This verification is documented as PARTIAL because the project was not run in a fresh Windows environment during this session.

## Required local validation checklist
1. Ensure Git is installed.
2. Ensure Python 3.11+ is installed.
3. Ensure Node.js 18+ is installed.
4. Clone the repository.
5. Create a virtual environment.
6. Install backend dependencies.
7. Configure `.env` from `.env.example`.
8. Initialize the SQLite database.
9. Install frontend dependencies.
10. Start the backend.
11. Start the frontend.
12. Register or sign in.
13. Connect GitHub.
14. Analyze a repository.

## Expected behavior
- No Docker installation must be required.
- SQLite remains the default development database.
- Redis and Celery remain optional.
- Local startup must work using standard PowerShell commands.

## Known caveat
A clean Windows installation still needs real-world validation in a fresh environment before claiming full beta readiness.
