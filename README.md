# DSAR - Data Subject Access Request System

A small full-stack project for managing Data Subject Access Requests (DSARs) under GDPR. It lets users submit access/deletion/rectification requests, lets an admin process them, and exports the user's personal data (JSON or CSV) with sensitive fields masked.

## What it does

- Submit a DSAR request from a simple web form (name, email, request type, identifier)
- Admin views all requests and processes them one by one
- Backend scans the database tables for data matching the requester
- Exports found data as JSON or CSV, with PII (emails, phones, SSN, addresses) masked
- Tracks request status: pending → processing → completed / rejected

## Stack

- **Backend:** FastAPI, SQLAlchemy, PostgreSQL
- **Frontend:** React (Create React App)
- **DevOps:** Docker + Docker Compose

## Run it

```bash
# 1. Start the stack
docker compose up --build

# 2. Load sample data into the database
docker compose exec backend python ingest.py

# 3. Open the app
# Frontend: http://localhost:3000
# API docs:  http://localhost:5000/docs
```

The frontend talks to `http://localhost:5000`. If you change the API URL, set `REACT_APP_API_URL` in the frontend environment.

## Project structure

```
backend/
  app.py           # FastAPI API + DB models
  dsar_engine.py   # data discovery, masking, export
  ingest.py        # loads CSV data into Postgres
  requirements.txt # Python dependencies
  Dockerfile
  data/            # sample banking datasets

frontend/
  src/
    App.js         # request form + request list
    services/api.js # axios client
    components/DsarButton.js
    App.css
frontend/package.json

docker-compose.yml # Postgres, pgAdmin, backend, frontend
.env               # database credentials
```

## Main API endpoints

| Method | Endpoint | What it does |
|--------|----------|--------------|
| GET | `/health` | health check |
| POST | `/api/dsar/requests` | create a DSAR request |
| GET | `/api/dsar/requests` | list all requests |
| POST | `/api/dsar/requests/{id}/process` | process a pending request |
| GET | `/api/dsar/requests/{id}/export?format=json\|csv` | download the data export |

## Notes

- This is a learning/demo project, not production-ready. Add auth, rate limiting, and proper secret management before using it with real data.
- Default Postgres credentials are in `.env` (change them before any real use).

Built as a senior project on GDPR compliance and data engineering basics.
