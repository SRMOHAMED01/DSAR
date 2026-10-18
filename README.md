# DSAR - Data Subject Access Request System

[![License](https://img.shields.io/badge/license-Educational-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-19.2+-61DAFB.svg)](https://reactjs.org/)

A modern, production-ready Data Subject Access Request (DSAR) management platform built to support GDPR compliance. The system automates data discovery, extraction, masking, and export for personal data subject requests (access, deletion, rectification).

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Development](#development)
- [API Documentation](#api-documentation)
- [Testing](#testing)
- [Data Model](#data-model)
- [Configuration](#configuration)
- [Security & Compliance](#security--compliance)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)

## 🎯 Overview

Under GDPR and similar data privacy regulations, organizations must respond to Data Subject Access Requests (DSARs) within strict timeframes. This system streamlines the DSAR workflow by:

1. **Automating intake** - Web-based form for request submission
2. **Data discovery** - Automatically identifies all personal data across database tables
3. **Secure processing** - Masks sensitive information in exports
4. **Export generation** - Produces structured JSON/CSV responses
5. **Lifecycle tracking** - Full audit trail from submission to completion

## ✨ Features

### Core Capabilities

- **Multi-type Request Support**: Access, deletion, and rectification DSARs (GDPR Articles 15, 17, 16)
- **Intelligent Data Discovery**: Automatically scans PostgreSQL schemas/tables to locate subject data based on email, customer ID, or name
- **Smart Data Masking**: Configurable PII masking (SSN, email, phone, address, etc.) in exported data
- **Multiple Export Formats**: JSON and CSV with proper formatting
- **Request Workflow Management**: States (pending → processing → completed/rejected) with full audit logging
- **Admin Dashboard**: Review, process, and export completed requests
- **Real-time Status Tracking**: Monitor request progress end-to-end

### Technical Excellence

- **Modern Backend**: FastAPI with async support, Pydantic v2 validation, automatic OpenAPI docs
- **Type Safety**: Full type hints and Pydantic models
- **Database ORM**: SQLAlchemy 2.0 with Alembic migration support
- **Structured Logging**: structlog for JSON-formatted logs (audit-ready)
- **Error Handling**: Comprehensive validation and graceful error management
- **CORS Support**: Configurable for production deployments
- **Health Monitoring**: Built-in `/health` endpoint for observability
- **Responsive UI**: Modern React 19 with CSS3, mobile-friendly
- **Containerized**: Docker-first with healthchecks and multi-stage builds

## 🏗️ Architecture

### System Design

```
┌─────────────────┐
│  React Frontend │  (Port 3000)
│   - Request UI  │
│  - Admin Panel  │
└────────┬────────┘
         │ HTTP/REST
┌────────▼────────┐
│  FastAPI Backend│  (Port 5000)
│  - API Routes   │
│  - Validation   │
└────────┬────────┘
         │
┌────────▼────────┐
│  DSAR Engine    │  (Core Logic)
│  - Discovery    │
│  - Masking      │
│  - Export       │
└────────┬────────┘
         │
┌────────▼────────┐
│  PostgreSQL DB  │  (Port 5432)
│  - dsar_requests│
│  - raw schemas  │
└─────────────────┘
```

### Data Flow

1. User submits DSAR via frontend form
2. FastAPI validates and persists request to PostgreSQL
3. Admin processes request → status changes to `processing`
4. DSAR Engine discovers matching records across all tables
5. Data is masked and exported (JSON/CSV)
6. Status updated to `completed`, export stored
7. User/admin downloads export

## 📦 Prerequisites

- **Docker** 20.10+ and **Docker Compose** v2+
- **Node.js** 18+ (for local frontend dev)
- **Python** 3.11+ (for local backend dev)
- **PostgreSQL** 15+ (if running without Docker)

## 🚀 Quick Start

### Using Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/SRMOHAMED01/DSAR.git
cd DSAR

# Start all services (builds images if needed)
docker compose up --build

# In a new terminal, ingest sample data
docker compose exec backend python ingest.py
```

### Access Services

| Service | URL | Credentials |
|---|---|---|
| **Frontend** | http://localhost:3000 | - |
| **Backend API** | http://localhost:5000 | - |
| **Swagger Docs** | http://localhost:5000/docs | - |
| **ReDoc Docs** | http://localhost:5000/redoc | - |
| **pgAdmin** | http://localhost:5050 | admin@dsar.com / 12345 |
| **Postgres** | localhost:5432 | See .env |

## 💻 Development

### Backend Development

```bash
cd backend

# Create virtual environment
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run with auto-reload
uvicorn app:app --reload --host 0.0.0.0 --port 5000
# Or
python run.py
```

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm start

# Build for production
npm run build

# Run tests
npm test
```

### Database Migrations (Alembic)

```bash
cd backend

# Initialize (if needed)
alembic init alembic

# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## 📖 API Documentation

Interactive API documentation is available at:

- **Swagger UI**: http://localhost:5000/docs
- **ReDoc**: http://localhost:5000/redoc

### Key Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Service health check |
| `POST` | `/api/dsar/requests` | Create new DSAR request |
| `GET` | `/api/dsar/requests` | List all requests (paginated) |
| `GET` | `/api/dsar/requests/{id}` | Get request by ID |
| `POST` | `/api/dsar/requests/{id}/process` | Process a pending request |
| `GET` | `/api/dsar/requests/{id}/export?format={json\|csv}` | Download processed export |

### Example Request

```bash
curl -X POST "http://localhost:5000/api/dsar/requests" \
  -H "Content-Type: application/json" \
  -d '{
    "requester_name": "Alice Johnson",
    "requester_email": "alice.johnson@example.com",
    "request_type": "access",
    "identifier": "alice.johnson@example.com",
    "identifier_type": "email",
    "details": {}
  }'
```

## 🧪 Testing

### Backend Unit Tests

```bash
cd backend

# Run all tests
pytest -v

# Run with coverage
pytest --cov=. --cov-report=term-missing

# Run specific test file
pytest tests/test_dsar_engine.py -v
```

### Manual API Testing

```bash
cd backend
python test_api.py
```

### Frontend Tests

```bash
cd frontend
npm test -- --watchAll=false --coverage
```

## 💾 Data Model

### DSAR Requests Table

| Field | Type | Description |
|---|---|---|
| `id` | UUID | Unique request identifier |
| `requester_name` | String | Requester full name |
| `requester_email` | String | Requester contact email |
| `request_type` | Enum | `access`, `deletion`, `rectification` |
| `status` | Enum | `pending`, `processing`, `completed`, `rejected` |
| `identifier` | String | Subject identifier (email/ID/name) |
| `identifier_type` | String | `email`, `customer_id`, `name` |
| `details` | JSON | Additional request details |
| `created_at` | Timestamp | Request submission time |
| `updated_at` | Timestamp | Last update time |
| `processed_at` | Timestamp | Processing completion time |
| `admin_notes` | Text | Admin comments/rejection reason |
| `export_path` | String | Path to generated export file |

### Sample Datasets

The system includes sample banking data:

- **bank_transactions_data_2.csv**: Transaction records (347K rows)
- **Comprehensive_Banking_Database.csv**: Customer profiles with PII

## ⚙️ Configuration

### Environment Variables

Create/update `.env` file in project root:

```env
# Database
POSTGRES_USER=Mohamed
POSTGRES_PASSWORD=12345
POSTGRES_DB=dsar_db
DATABASE_URL=postgresql://Mohamed:12345@db:5432/dsar_db

# Application
SECRET_KEY=your-secure-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Frontend
REACT_APP_API_URL=http://localhost:5000
```

### DSAR Engine Configuration

Maskable fields (configurable in `dsar_engine.py`):

```python
self.sensitive_fields = [
    "ssn", "social_security_number",
    "email", "phone", "phone_number",
    "address", "customer_id", "full_name", "name"
]
```

## 🔒 Security & Compliance

### Data Protection

- **PII Masking**: Sensitive data masked by default in exports (configurable per use case)
- **Audit Logging**: All actions logged with timestamps and context via structlog
- **Input Validation**: Pydantic models enforce strict validation
- **SQL Injection Protection**: Parameterized queries via SQLAlchemy
- **No Hardcoded Secrets**: Environment-based configuration
- **CORS Configurable**: Restrict origins in production

### GDPR Compliance Features

- **Article 15 (Access)**: Full data retrieval and structured export
- **Article 16 (Rectification)**: Request tracking (extendable for automated updates)
- **Article 17 (Erasure)**: Deletion request workflow (implement business logic as needed)
- **Audit Trail**: Immutable logging for compliance reporting
- **Data Minimization**: Masking support, export only relevant records
- **Timely Response Tracking**: Timestamps enable SLA monitoring

### Production Hardening Recommendations

1. Change default `SECRET_KEY` and DB credentials
2. Enable HTTPS/TLS termination
3. Implement authentication/authorization (JWT/OAuth2) for admin endpoints
4. Add rate limiting (e.g., SlowAPI)
5. Configure CORS for specific origins
6. Enable database encryption at rest
7. Set up log aggregation (ELK/Datadog)
8. Implement backup/retention policies for exports
9. Add RBAC for different user roles (requester, admin, DPO)

## 🚢 Deployment

### Docker Production

```bash
# Build and start in detached mode
docker compose up -d --build

# View logs
docker compose logs -f backend

# Scale backend
docker compose up -d --scale backend=2
```

### Cloud Deployment Options

- **Backend**: Render, Railway, Fly.io, AWS ECS, GCP Cloud Run
- **Frontend**: Vercel, Netlify, Cloudflare Pages
- **Database**: AWS RDS, Supabase, Neon, Cloud SQL
- **Files/Exports**: S3, Cloud Storage (for production export storage)

## 📈 Roadmap

- [ ] Alembic migrations setup
- [ ] JWT authentication & RBAC
- [ ] Email notifications (request submission/processing/completion)
- [ ] PDF export support (WeasyPrint/ReportLab)
- [ ] Bulk request processing
- [ ] Search/filtering in admin UI
- [ ] Data lineage tracking
- [ ] S3 integration for export storage
- [ ] Comprehensive unit/integration tests
- [ ] CI/CD pipeline (GitHub Actions)
- [ ] API rate limiting
- [ ] Multi-tenant support

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit changes: `git commit -m "feat: add your feature"`
4. Push to branch: `git push origin feature/your-feature`
5. Open a Pull Request

### Code Style

- **Python**: black, ruff, mypy
- **JavaScript/React**: ESLint, Prettier
- **Commits**: Conventional Commits format

## 📄 License

This project is licensed for educational and demonstration purposes. See the LICENSE file for details.

## 🙏 Acknowledgments

- Built as a senior project demonstrating modern data engineering, privacy engineering, and GDPR compliance
- FastAPI, React, SQLAlchemy, and PostgreSQL communities for excellent tooling
- Open-source privacy/compliance tooling ecosystem

---

**For support or questions, please open an issue on [GitHub](https://github.com/SRMOHAMED01/DSAR/issues).**
