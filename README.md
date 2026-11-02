# DevPilot: AI-Powered Code Intelligence & Repository Platform

[![FastAPI](https://img.shields.io/badge/FastAPI-0.111+-009688.svg?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18.3-61DAFB.svg?style=flat&logo=react&logoColor=black)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.7-3178C6.svg?style=flat&logo=typescript&logoColor=white)](https://www.typescriptlang.org)
[![TailwindCSS](https://img.shields.io/badge/TailwindCSS-3.4-38B2AC.svg?style=flat&logo=tailwind-css&logoColor=white)](https://tailwindcss.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791.svg?style=flat&logo=postgresql&logoColor=white)](https://www.postgresql.org)
[![Redis](https://img.shields.io/badge/Redis-7-DC382D.svg?style=flat&logo=redis&logoColor=white)](https://redis.io)

DevPilot is an AI-powered software development and code intelligence platform. It enables engineering teams to deeply analyze Git repositories, evaluate AST complexity, discover security vulnerabilities (OWASP, CWE, hardcoded secrets), generate interactive architecture dependency graphs, and interact contextually with codebases via multi-model AI assistants.

---

## Table of Contents

- [Project Overview](#project-overview)
- [Main Features](#main-features)
- [Technology Stack](#technology-stack)
- [Architecture Overview](#architecture-overview)
- [Directory Structure](#directory-structure)
- [Installation Instructions](#installation-instructions)
- [Environment Configuration](#environment-configuration)
- [Backend Startup](#backend-startup)
- [Frontend Startup](#frontend-startup)
- [Docker Infrastructure](#docker-infrastructure)
- [API Documentation Access](#api-documentation-access)
- [Verification & Testing](#verification--testing)
- [Development Roadmap](#development-roadmap)

---

## Project Overview

Modern software repositories quickly grow into complex networks of interdependent modules, making it difficult to maintain quality, ensure security compliance, and onboard developers. DevPilot acts as an automated engineering co-pilot that continuously indexes, analyzes, and explains your codebase.

### Phase 1: Foundation & Architecture Setup (Current)
- Established clean, modular full-stack architecture.
- Built Linear-inspired dark dashboard with reactive state management.
- Configured FastAPI backend with CORS, centralized exception handlers, typed schemas, and versioning (`/api/v1`).
- Implemented PostgreSQL session management with SQLAlchemy 2.0 declarative base and Alembic migration tracking.
- Structured provider-agnostic AI engine architecture (Google Gemini & OpenAI GPT).
- Prepared background worker queuing scaffolding with Celery and Redis.
- Orchestrated containerized database and caching services with Docker Compose.

---

## Main Features

| Feature | Phase | Description |
| :--- | :--- | :--- |
| **Linear Dark Dashboard** | Phase 1 | High-density charcoal surface UI with subtle borders, restrained blue-violet accents, and responsive layout. |
| **API Health & Diagnostics** | Phase 1 | Real-time endpoint health checks verifying PostgreSQL and Redis connectivity. |
| **Provider-Agnostic AI Engine** | Phase 1 (Stub) | Unified interface for Google Gemini, OpenAI, and custom LLM inference. |
| **Static Code & AST Analyzer** | Phase 1 (Stub) | Abstract syntax tree analysis, cyclomatic score calculation, and lint verification. |
| **Security Auditing** | Phase 1 (Stub) | OWASP Top 10, CWE rule enforcement, and secret leak prevention architecture. |
| **GitHub Integration** | Phase 2 | OAuth2 authentication, webhook sync, and continuous repository indexing. |
| **Architecture Visualizer** | Phase 2 | Interactive component coupling graph and dependency flow diagrams. |
| **AI Repository Assistant** | Phase 2 | Context-aware code assistant capable of answering questions and suggesting refactors. |

---

## Technology Stack

### Frontend
- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite 6
- **Styling**: Tailwind CSS (custom dark charcoal & violet color tokens)
- **Animations**: Framer Motion
- **Icons**: Lucide React
- **Routing**: React Router v6
- **State Management**: Zustand

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Server**: Uvicorn (ASGI)
- **Validation**: Pydantic v2 & Pydantic-Settings
- **ORM**: SQLAlchemy 2.0
- **Database Driver**: Psycopg 3 & Psycopg2-binary
- **Database Migrations**: Alembic

### Persistence & Caching
- **Relational Database**: PostgreSQL 16
- **Cache & Message Broker**: Redis 7
- **Background Processing**: Celery (architecture prepared)

### Infrastructure & DevOps
- **Containers**: Docker & Docker Compose
- **Web Server / Proxy**: Nginx (multi-stage production builds)

---

## Architecture Overview

```
DevPilot/
├── frontend/             # React 18 + Vite + Tailwind CSS SPA
│   ├── src/
│   │   ├── components/   # Common buttons, badges, cards, sidebar, top nav
│   │   ├── pages/        # Dashboard overview, repos, analysis, security, settings
│   │   ├── hooks/        # Keyboard shortcuts (Ctrl+K), live API health hook
│   │   ├── services/     # Backend fetch client
│   │   ├── store/        # Zustand global application state
│   │   └── types/        # TypeScript interfaces
├── backend/              # FastAPI Application
│   ├── app/
│   │   ├── api/v1/       # Versioned REST endpoints (/health, /)
│   │   ├── core/         # Config, logging, centralized exception handlers
│   │   ├── database/     # SQLAlchemy engine, session maker, connection tester
│   │   ├── models/       # Declarative base & ORM models
│   │   ├── schemas/      # Pydantic validation models
│   │   ├── engines/      # AI providers (Gemini/OpenAI) & Static analyzers
│   │   ├── integrations/ # GitHub OAuth & Redis clients
│   │   └── workers/      # Celery task definitions
│   ├── tests/            # Pytest test suite
│   └── alembic/          # Database migration scripts
├── infrastructure/       # Multi-stage Dockerfiles and Nginx configs
├── docs/                 # Architectural specifications and diagrams
├── scripts/              # PowerShell development automation scripts
├── docker-compose.yml    # Development PostgreSQL 16 & Redis 7 services
└── .env.example          # Environment template
```

---

## Installation Instructions

### Prerequisites
- Node.js (v18+ or v20+) and npm
- Python 3.11+
- Git
- Docker & Docker Compose (optional for local DB/cache)

### 1. Clone Repository
```powershell
git clone <repository-url> T:\PremPFS
cd T:\PremPFS
```

### 2. Configure Environment Variables
Copy the template to `.env`:
```powershell
Copy-Item .env.example .env
```
Adjust database or API credentials if required.

---

## Backend Startup

### 1. Create and Activate Virtual Environment
```powershell
python -m venv backend\.venv
.\backend\.venv\Scripts\Activate.ps1
```

### 2. Install Dependencies
```powershell
pip install -r backend\requirements.txt
```

### 3. Run Pytest Suite
```powershell
pytest backend\tests -v
```

### 4. Start Backend Server
```powershell
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
The backend starts at `http://localhost:8000`.

---

## Frontend Startup

### 1. Install Node Dependencies
```powershell
cd frontend
npm install
```

### 2. Run Development Server
```powershell
npm run dev
```
The frontend is accessible at `http://localhost:5173`.

### 3. Production Build
```powershell
npm run build
```

---

## Docker Infrastructure

To launch containerized PostgreSQL 16 and Redis 7:

```powershell
# Start PostgreSQL & Redis services in background
docker compose up -d

# Verify health status of containers
docker compose ps

# View container logs
docker compose logs -f

# Stop services
docker compose down
```

Persistent data is stored in the Docker volumes `postgres_data` and `redis_data`.

---

## API Documentation Access

Once the backend is running, explore the interactive documentation:

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **OpenAPI Schema**: [http://localhost:8000/api/v1/openapi.json](http://localhost:8000/api/v1/openapi.json)

### Core Endpoints
- `GET /api/v1/health` &rarr; `{"status": "healthy", "application": "DevPilot", "version": "1.0.0"}`
- `GET /api/v1/` &rarr; `{"message": "Welcome to DevPilot API", "version": "1.0.0"}`
- `GET /api/v1/health/diagnostics` &rarr; Detailed PostgreSQL, Redis, and AI provider status.

---

## Verification & Testing

Verify that both frontend and backend function properly:

```powershell
# Backend test execution
.\backend\.venv\Scripts\pytest.exe backend\tests -v

# Frontend build execution
cd frontend
npm run build
```

---

## Development Roadmap

- [x] **Phase 1: Project Foundation & Architecture Setup**
  - Modular directory layout
  - Linear dark UI shell with Zustand state management
  - FastAPI application structure, CORS, versioned routes
  - SQLAlchemy 2.0 + Alembic migrations setup
  - Provider-agnostic AI engine and code analyzer interfaces
  - Docker Compose infrastructure for Postgres & Redis
- [ ] **Phase 2: GitHub Integration & Continuous Repository Sync**
  - GitHub App & OAuth integration
  - Webhook handlers for push, commit, and PR events
  - Celery background worker pipeline for cloning and caching repos
- [ ] **Phase 3: Code Intelligence & Static Analysis Engine**
  - Tree-sitter / AST parsing for Python, TypeScript, Go, Rust
  - Complexity metrics (cyclomatic & cognitive)
  - Dead code, dependency drift, and code smell identification
- [ ] **Phase 4: Security Vulnerability Engine**
  - OWASP Top 10 rule engine
  - Secret scanning (entropy analysis & regex patterns)
  - Dependency CVE cross-referencing
- [ ] **Phase 5: Interactive Architecture & AI Co-Pilot**
  - Dependency graph visualization with zoomable canvas
  - Google Gemini & OpenAI multi-turn repository chat assistant
  - Automated PR intelligence and architecture change summaries
