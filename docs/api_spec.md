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

### 4. Interactive Documentation
- **Swagger UI**: `/docs`
- **ReDoc**: `/redoc`
- **OpenAPI Schema**: `/api/v1/openapi.json`
