# DevPilot API Specification (v1)

Base URL: `/api/v1`

## Endpoints

### 1. Health Status
- **Method**: `GET`
- **Path**: `/api/v1/health`
- **Description**: Returns general application health and liveness confirmation.
- **Response** (`200 OK`):
  ```json
  {
    "status": "healthy",
    "application": "DevPilot",
    "version": "1.0.0"
  }
  ```

### 2. API Root Welcome
- **Method**: `GET`
- **Path**: `/api/v1/`
- **Description**: Returns welcome message and version indicator.
- **Response** (`200 OK`):
  ```json
  {
    "message": "Welcome to DevPilot API",
    "version": "1.0.0"
  }
  ```

### 3. System Diagnostics
- **Method**: `GET`
- **Path**: `/api/v1/health/diagnostics`
- **Description**: Deep connectivity diagnostic check across database, Redis cache, and AI providers.
- **Response** (`200 OK`):
  ```json
  {
    "status": "healthy",
    "application": "DevPilot",
    "version": "1.0.0",
    "environment": "development",
    "database": {
      "connected": true,
      "error": null,
      "engine": "PostgreSQL"
    },
    "redis": {
      "connected": true,
      "error": null
    },
    "ai_providers": {
      "gemini_configured": false,
      "openai_configured": false
    }
  }
  ```

---

## Phase 2: Core Intelligence Endpoints

### 4. Organizations API

#### Create Organization
- **Method**: `POST`
- **Path**: `/api/v1/organizations`
- **Request Body**:
  ```json
  {
    "name": "Acme Engineering",
    "slug": "acme-engineering",
    "description": "Core software architecture team"
  }
  ```
- **Response** (`201 Created`):
  ```json
  {
    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "name": "Acme Engineering",
    "slug": "acme-engineering",
    "description": "Core software architecture team",
    "created_at": "2026-11-02T11:20:00Z",
    "updated_at": "2026-11-02T11:20:00Z",
    "member_count": 0,
    "repository_count": 0
  }
  ```

#### List Organizations
- **Method**: `GET`
- **Path**: `/api/v1/organizations?skip=0&limit=20`
- **Response** (`200 OK`): Paginated collection (`items`, `total`, `skip`, `limit`).

#### Retrieve Organization
- **Method**: `GET`
- **Path**: `/api/v1/organizations/{org_id}`
- **Response** (`200 OK`): Single organization object or `404 Not Found`.

#### Update Organization
- **Method**: `PATCH`
- **Path**: `/api/v1/organizations/{org_id}`
- **Request Body**: Partial attributes (`name`, `slug`, `description`).
- **Response** (`200 OK`): Updated organization object.

#### Delete Organization
- **Method**: `DELETE`
- **Path**: `/api/v1/organizations/{org_id}`
- **Response** (`204 No Content`). Cascades to members, repositories, and scan jobs.

#### Organization Members
- **Method**: `GET` / `POST`
- **Path**: `/api/v1/organizations/{org_id}/members`
- **Request Body** (POST):
  ```json
  {
    "user_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "role": "MEMBER"
  }
  ```
- Roles: `OWNER`, `ADMIN`, `MEMBER`.

---

### 5. Repository Management API

#### Create Repository Record
- **Method**: `POST`
- **Path**: `/api/v1/repositories`
- **Request Body**:
  ```json
  {
    "organization_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "name": "devpilot-core",
    "full_name": "acme/devpilot-core",
    "description": "Code intelligence orchestrator",
    "provider": "github",
    "external_id": "12345678",
    "html_url": "https://github.com/acme/devpilot-core",
    "default_branch": "main",
    "is_private": true,
    "is_active": true
  }
  ```
- **Response** (`201 Created`).

#### List Repositories
- **Method**: `GET`
- **Path**: `/api/v1/repositories?organization_id={uuid}&provider=github&is_active=true&is_private=false&search={query}&skip=0&limit=20`
- **Response** (`200 OK`): Paginated collection.

#### Retrieve Repository
- **Method**: `GET`
- **Path**: `/api/v1/repositories/{repo_id}`
- **Response** (`200 OK`).

#### Update Repository Metadata
- **Method**: `PATCH`
- **Path**: `/api/v1/repositories/{repo_id}`
- **Response** (`200 OK`).

#### Delete Repository Record
- **Method**: `DELETE`
- **Path**: `/api/v1/repositories/{repo_id}`
- **Response** (`204 No Content`).

#### Ask Repository Question (RAG)
- **Method**: `POST`
- **Path**: `/api/v1/repositories/{repo_id}/ask?question={text}`
- **Description**: Retrieves repository file context, builds a grounded prompt, and answers using the local RAG pipeline.
- **Response** (`200 OK`): Includes `answer`, `citations`, and `retrieval_count`.

---

### 6. Scan Job Management API

#### Create Scan Job
- **Method**: `POST`
- **Path**: `/api/v1/scans?dispatch_async=true`
- **Request Body**:
  ```json
  {
    "repository_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "scan_type": "full"
  }
  ```
- Scan Types: `full`, `security`, `ast`, `complexity`.
- **Response** (`201 Created`): Initial status `PENDING` or `QUEUED`.

#### List Scan Jobs
- **Method**: `GET`
- **Path**: `/api/v1/scans?repository_id={uuid}&status=RUNNING&scan_type=full&skip=0&limit=20`
- **Response** (`200 OK`): Paginated collection.

#### Retrieve Scan Job Details
- **Method**: `GET`
- **Path**: `/api/v1/scans/{scan_id}`
- **Response** (`200 OK`).

#### Update Scan Status & Progress
- **Method**: `PATCH`
- **Path**: `/api/v1/scans/{scan_id}`
- **Request Body**:
  ```json
  {
    "status": "RUNNING",
    "progress": 65,
    "error_message": null
  }
  ```
- **Response** (`200 OK`).

#### Cancel Scan Job
- **Method**: `POST`
- **Path**: `/api/v1/scans/{scan_id}/cancel`
- **Response** (`200 OK`): Marks status as `CANCELLED` and records `completed_at`.

---

## Phase 3: GitHub Authentication & Repository Integration

### 7. GitHub OAuth Initialization
- **Method**: `GET`
- **Path**: `/api/v1/auth/github`
- **Description**: Returns a GitHub authorization URL and a signed CSRF state token.
- **Response** (`200 OK`):
  ```json
  {
    "authorization_url": "https://github.com/login/oauth/authorize?...",
    "state": "nonce:timestamp:signature"
  }
  ```

### 8. OAuth Callback
- **Method**: `POST`
- **Path**: `/api/v1/auth/github/callback`
- **Request Body**:
  ```json
  {
    "code": "github_oauth_code",
    "state": "nonce:timestamp:signature"
  }
  ```
- **Response** (`200 OK`): JWT access token and authenticated user payload.

### 9. Current User
- **Method**: `GET`
- **Path**: `/api/v1/auth/me`
- **Headers**: `Authorization: Bearer <jwt>`
- **Response** (`200 OK`): Authenticated user profile.

### 10. Logout
- **Method**: `POST`
- **Path**: `/api/v1/auth/logout`
- **Headers**: `Authorization: Bearer <jwt>`
- **Response** (`200 OK`): Logout acknowledgment.

### 11. Accessible GitHub Repositories
- **Method**: `GET`
- **Path**: `/api/v1/github/repositories`
- **Headers**: `Authorization: Bearer <jwt>`
- **Response** (`200 OK`): List of repositories visible to the authenticated GitHub account.

---

## Interactive Documentation
- **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) (or `http://127.0.0.1:8080/docs`)
- **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
- **OpenAPI Schema**: `/api/v1/openapi.json`
