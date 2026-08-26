# LoanVerify — AI-Powered Loan Data Verification Copilot

> **Intain FinTech Challenge 2026 — Full Stack Track**

A full-stack application that ingests messy loan records, detects data-quality issues, uses AI to explain and resolve exceptions, and creates a traceable verified record with audit logging and hash chaining.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    React Frontend                       │
│  Dashboard · Upload · Validation · Audit · AI Copilot  │
└──────────────────────┬──────────────────────────────────┘
                       │ REST API
┌──────────────────────▼──────────────────────────────────┐
│                  FastAPI Backend                        │
│  Auth (JWT) · Uploads · Validation · Audit · AI Copilot │
└───┬──────────────┬───────────────┬──────────────────────┘
    │              │               │
┌───▼───┐   ┌─────▼─────┐   ┌────▼────┐
│ SQLite│   │  Ingestion │   │ OpenAI  │
│  DB   │   │  Service   │   │   API   │
└───────┘   └───────────┘   └─────────┘
```

## ✨ Features

- **Data Ingestion** — Upload CSV/Excel loan tapes with auto-detection of column mappings
- **Field Normalization** — Maps 50+ messy column names to a standard schema
- **30+ Validation Rules** — Checks for outliers, missing fields, invalid formats, range violations
- **AI Copilot** — GPT-powered explanations for each data quality exception
- **SHA-256 Hash Chain** — Every record hashes the previous, creating a tamper-evident chain
- **Audit Trail** — Immutable log of all actions (uploads, explanations, resolutions)
- **Role-Based Access** — Analyst (upload/view), Reviewer (resolve exceptions), Admin (full access)
- **Quality Score** — 0–100 score computed from exception severity and count
- **Dashboard** — Overview stats, exception breakdown, recent uploads

## 🚀 Quick Start

### Backend

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Seed demo users
python seed.py

# Start the server
uvicorn app.main:app --reload --port 8000
```

API docs: [http://localhost:8000/docs](http://localhost:8000/docs)

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

App: [http://localhost:3000](http://localhost:3000)

### Demo Accounts

| Username | Password | Role |
|----------|----------|------|
| `analyst` | `demo123` | Upload & view data |
| `reviewer` | `demo123` | Resolve exceptions |
| `admin` | `demo123` | Full access |

### Sample Data

Upload `backend/sample_data/loan_tape_sample.csv` — a 30-record loan tape with intentionally introduced data quality issues (missing fields, extreme values, invalid formats).

## 🔧 API Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/auth/register` | Register user | — |
| POST | `/api/auth/login` | Login | — |
| GET | `/api/auth/me` | Current user | ✓ |
| POST | `/api/uploads` | Upload loan tape | Analyst+ |
| GET | `/api/uploads` | List uploads | ✓ |
| GET | `/api/uploads/:id` | Upload summary | ✓ |
| GET | `/api/uploads/:id/records` | Loan records | ✓ |
| GET | `/api/uploads/:id/exceptions` | Validation exceptions | ✓ |
| POST | `/api/exceptions/:id/explain` | AI explanation | ✓ |
| POST | `/api/exceptions/:id/resolve` | Resolve/dismiss | Reviewer+ |
| GET | `/api/audit/logs` | Audit trail | Reviewer+ |
| GET | `/api/audit/dashboard` | Dashboard stats | ✓ |
| GET | `/api/audit/chain-verify/:id` | Verify hash chain | Reviewer+ |

## 🧠 How the Validation Engine Works

1. **Column Detection** — Maps 50+ column name variants to 13 standard fields
2. **Type Coercion** — Converts strings to appropriate types (int/float/string)
3. **Rule Evaluation** — Each record passes through all validation rules
4. **Exception Generation** — Violations create `ValidationException` records with severity levels
5. **AI Explanation** — OpenAI generates human-readable explanations for each exception
6. **Quality Scoring** — Score = 100 − (weighted deductions per record)

## 🔗 Hash Chain

Each loan record computes a SHA-256 hash from its normalized data + the previous record's hash:

```
record[n].hash = SHA256(record[n-1].hash || sorted(field=value pairs))
```

The chain starts from "GENESIS" and any tampering with a single record breaks the chain from that point forward.

## 🎯 Tech Stack

- **Frontend:** React 18, Tailwind CSS, React Router, React Dropzone
- **Backend:** FastAPI, SQLAlchemy (async), Pydantic, python-jose (JWT)
- **AI:** OpenAI GPT-4o-mini (with mock fallback when no API key)
- **Database:** SQLite (async via aiosqlite)
- **Hashing:** SHA-256 (Python hashlib)

---

**Built for Intain FinTech Challenge 2026 🏆**
