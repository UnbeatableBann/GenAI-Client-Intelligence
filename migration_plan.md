# Implementation Plan: GenAI Client Intelligence Migration

## Goal Description

The objective is to migrate the existing monolithic Streamlit GenAI Client Intelligence prototype into a robust, production-inspired full-stack architecture on the `dev` branch. The new stack consists of a React 19 (Vite, Tailwind, Shadcn) frontend and a FastAPI (Python 3.12, PostgreSQL, Redis) backend.

Crucially, this is a **migration, not a rewrite**. We must preserve 100% of the existing AI workflows, prompts, validation logic, PDF generation, and UI capabilities. The business logic will exclusively live in the backend service layer, while the frontend strictly handles presentation and API consumption.

## User Review Required

> [!WARNING]
> **Database Authentication Setup**
> The specification requires `users` and `approved_reports` tables. Since the Streamlit app didn't have user authentication, I plan to implement a dummy/placeholder "demo user" mechanism in the FastAPI backend to satisfy the foreign keys without over-complicating the migration with JWT/OAuth scopes. Please let me know if you expect a full auth implementation instead.
> [!IMPORTANT]
> **Directory Structure Replacement**
> As per the specification, I will create `frontend/`, `backend/`, and `docker/` directories at the repository root. I will move the existing `backend/` Python files into the new `backend/app/services/` layer and phase out `app.py`.

## Open Questions

> [!CAUTION]
> **Redis Implementation Strategy**
> The specification mentions using Redis for API Cache and Session Cache. Should we rely on `fastapi-cache2` for endpoint caching, or do you prefer a custom Redis integration for manual rate-limiting and conversation state? (I propose `fastapi-cache2` + direct `redis-py` for session states).

---

## Proposed Changes

### Infrastructure & DevOps

All containerization and local-development scaffolding.

#### [NEW] `docker-compose.yml`

Will orchestrate: `frontend` (Node), `backend` (FastAPI), `postgres`, and `redis`.

#### [NEW] `docker/frontend/Dockerfile` & `docker/backend/Dockerfile`

Multi-stage optimized builds. Backend will use Uvicorn/Gunicorn.

#### [NEW] `.github/workflows/ci-cd.yml`

A GitHub Actions pipeline with sequential steps: Linting -> Testing -> Docker Builds -> Railway/Cloudflare deployment.

---

### Backend (FastAPI + PostgreSQL + Redis)

Restructuring the existing Python logic into an API-first monolithic architecture.

#### [NEW] `backend/app/main.py`

The FastAPI application entry point, including CORS middleware, Redis initialization, and router inclusion.

#### [NEW] `backend/app/api/v1/endpoints/`

- `reports.py`: `POST /analyze`, `GET /reports/{id}`, `POST /reports/{id}/approve`
- `chat.py`: `POST /chat`
- `export.py`: `POST /pdf`, `POST /share`

#### [NEW] `backend/app/database/models.py`

SQLAlchemy 2 models mapping to the required tables: `User`, `Conversation`, `Report`, `ApprovedReport`, `PdfReport`.

#### [MODIFY] `backend/app/services/`

We will migrate the *existing* logic into:

- `pipeline_service.py` (from `pipeline.py`)
- `assistant_service.py` (from `assistant.py`)
- `pdf_service.py` (from `pdf/generator.py`)
We will enforce async behaviors and remove any Streamlit dependencies (e.g., `st.session_state` calls replaced by DB/Redis reads).

---

### Frontend (React 19 + Vite + Tailwind)

A completely decoupled presentation layer consuming the FastAPI endpoints.

#### [NEW] `frontend/package.json`

Dependencies: React 19, React Router, TanStack Query, Axios, Lucide-React, PDF.js, React Hook Form, Zod.

#### [NEW] `frontend/src/api/client.ts`

Axios wrapper configured to hit the FastAPI backend with centralized error handling.

#### [NEW] `frontend/src/pages/Dashboard.tsx`

Replicates the Streamlit layout: Upload Conversation -> Generated Report view.

#### [NEW] `frontend/src/components/Report/`

- `WeeklySummary.tsx`, `HealthGrid.tsx`, `PriorityRisks.tsx`, `CoachActionPlan.tsx`
- `PdfPreview.tsx` (using PDF.js to render the base64/blob from the API).
- `ChatAssistant.tsx` (TanStack Query mutations to `POST /chat`).

---

## Verification Plan

### Automated Tests

1. **Backend Tests:** Write Pytest suites (`backend/tests/`) using `TestClient` to mock the LLM service and verify that given the same prompt, the FastAPI endpoints output the exact same Pydantic schemas as the legacy Streamlit code.
   - Run via: `cd backend && uv run pytest`
2. **Frontend Tests:** Use Vitest to ensure components render the data correctly.

### Manual Verification

1. Run `docker-compose up -d --build`.
2. Navigate to `http://localhost:5173`.
3. Upload `sample_conversation.txt`.
4. Visually verify the UI perfectly matches the old Streamlit UI, including the Health Grid, PDF preview, and Coach Assistant.
5. Verify that generating the PDF produces an identical ReportLab document.
