# LoanVerify — AI-Powered Loan Data Verification Copilot

> **Intain FinTech Challenge 2026 — Full Stack Track**

A full-stack application that ingests messy loan records, detects data-quality issues, uses AI to explain and resolve exceptions, and creates a traceable verified record with audit logging and hash chaining.

---

## 📋 Table of Contents

- [Prerequisites](#-prerequisites)
- [Installation & Setup](#-installation--setup)
- [Running the App](#-running-the-app)
- [AI (Grok) Setup](#-ai-grok-setup)
- [Demo Accounts](#-demo-accounts)
- [Sample Data](#-sample-data)
- [Using the App](#-using-the-app)
- [API Reference](#-api-reference)
- [Troubleshooting](#-troubleshooting)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)

---

## ✅ Prerequisites

Before you begin, make sure you have the following installed:

| Requirement | Version | Mac/Linux | Windows |
|-------------|---------|-----------|---------|
| **Python** | 3.9+ | `python3 --version` | `python --version` |
| **Node.js** | 18+ | `node --version` | `node --version` |
| **npm** | 9+ | `npm --version` | `npm --version` |

### Installing Prerequisites

#### Mac/Linux

```bash
# Install Python (using Homebrew on Mac)
brew install python3

# Install Node.js (using Homebrew on Mac)
brew install node

# On Ubuntu/Debian Linux
sudo apt update
sudo apt install python3 python3-venv python3-pip
sudo apt install nodejs npm
```

#### Windows

```bash
# Download and install Python from https://www.python.org/downloads/
# ⚠️ During install, check "Add Python to PATH"

# Download and install Node.js from https://nodejs.org/

# Or use winget:
winget install Python.Python.3.12
winget install OpenJS.NodeJS.LTS
```

---

## 🛠️ Installation & Setup

### 1. Clone the Repository

#### Mac/Linux/Windows

```bash
git clone https://github.com/your-repo/loanverify.git
cd loanverify
```

### 2. Backend Setup

#### Mac/Linux

```bash
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Seed demo users
python seed.py
```

#### Windows

```cmd
cd backend

:: Create virtual environment
python -m venv venv

:: Activate virtual environment
venv\Scripts\activate

:: Install dependencies
pip install -r requirements.txt

:: Seed demo users
python seed.py
```

Or in **PowerShell**:

```powershell
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Seed demo users
python seed.py
```

> ⚠️ **PowerShell users:** If you get a permission error, run:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

### 3. Frontend Setup

#### Mac/Linux/Windows

```bash
cd frontend

# Install dependencies
npm install
```

### 4. Environment Configuration (Optional — for AI features)

#### Mac/Linux

```bash
cd backend
cp .env.example .env
# Edit .env and add your Grok AI API key (see AI Setup section below)
nano .env
```

#### Windows

```cmd
cd backend
copy .env.example .env
:: Edit .env and add your Grok AI API key (see AI Setup section below)
notepad .env
```

---

## 🚀 Running the App

You need to run **two terminals** — one for the backend and one for the frontend.

### Start the Backend

#### Mac/Linux

**Terminal 1:**
```bash
cd loanverify/backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

#### Windows (CMD)

**Terminal 1:**
```cmd
cd loanverify\backend
venv\Scripts\activate
uvicorn app.main:app --reload --port 8000
```

#### Windows (PowerShell)

**Terminal 1:**
```powershell
cd loanverify\backend
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --port 8000
```

### Start the Frontend

#### Mac/Linux/Windows

**Terminal 2:**
```bash
cd loanverify/frontend
npm run dev
```

### Access the App

| Resource | URL |
|----------|-----|
| **App** | [http://localhost:3000](http://localhost:3000) |
| **API Docs** | [http://localhost:8000/docs](http://localhost:8000/docs) |

### One-Click Launch (Mac/Linux only)

If you prefer a single command to start everything:

#### Mac/Linux

```bash
cd loanverify
chmod +x QUICK_START.sh
./QUICK_START.sh
```

> This script sets up both backend and frontend, starts both servers, and opens the app in your browser.

---

## 🤖 AI (Grok) Setup

The AI explanations use **Grok AI from xAI** (OpenAI-compatible, free tier available).

### Get a FREE API Key

1. Go to **[https://console.x.ai](https://console.x.ai)**
2. Sign up / Log in with your X (Twitter) account
3. Go to **API Keys** page
4. Click **Create API Key**
5. Copy the key (starts with `xai-`)

### Add the Key to Your Project

#### Mac/Linux

```bash
cd backend
nano .env
# Replace xai-your-key-here with your actual key
# Save and exit (Ctrl+O, Enter, Ctrl+X)
```

#### Windows

```cmd
cd backend
notepad .env
:: Replace xai-your-key-here with your actual key
:: Save and close
```

Or set it as an **environment variable** (no .env edit needed):

#### Mac/Linux

```bash
export XAI_API_KEY=xai-your-key-here
```

#### Windows (CMD)

```cmd
set XAI_API_KEY=xai-your-key-here
```

#### Windows (PowerShell)

```powershell
$env:XAI_API_KEY="xai-your-key-here"
```

### Available Grok Models

| Model | Speed | Cost | Best For |
|-------|-------|------|----------|
| `grok-3` | Fast | $0.30/$0.50 per 1M tokens | Default, recommended |
| `grok-3-mini` | Faster | $0.10/$0.10 per 1M tokens | High volume |
| `grok-4.6` | Fast | $2.00/$6.00 per 1M tokens | Latest, most capable |

To change the model, edit `backend/.env`:
```
GROK_MODEL=grok-3
```

> 💡 **Without an API key**, the app uses **mock AI responses** — everything still works for demo purposes.

---

## 👤 Demo Accounts

| Username | Password | Role | Permissions |
|----------|----------|------|-------------|
| `analyst` | `demo123` | Analyst | Upload & view data |
| `reviewer` | `demo123` | Reviewer | Resolve exceptions |
| `admin` | `demo123` | Admin | Full access |

---

## 📁 Sample Data

Upload any of these sample CSV files from `backend/sample_data/`:

| File | Records | Description |
|------|---------|-------------|
| `clean_data.csv` | 20 | Clean data, minimal issues |
| `messy_bank_export.csv` | 35 | Messy column names, multiple exceptions |
| `loan_tape_sample.csv` | 30 | Intentionally introduced errors |
| `critical_errors.csv` | 20 | Severely corrupted data |
| `large_dataset.csv` | 100 | Larger dataset for testing |
| `mixed_formats.csv` | — | Mixed date/currency formats |
| `minimal_fields.csv` | — | Sparse data with many missing fields |

---

## 📖 Using the App

### Step-by-Step Workflow

1. **Login** — Go to [http://localhost:3000](http://localhost:3000) and sign in with a demo account
2. **Upload Data** — Navigate to **Upload Data** and drag-and-drop a CSV/Excel file
3. **Review Preview** — Check the auto-detected column mappings before processing
4. **Process & Validate** — Click **Process & Validate** to run the validation engine
5. **Review Exceptions** — View data quality issues found in your data
6. **AI Explanations** — Click **Explain** on any exception to get an AI-powered explanation
7. **Resolve Issues** — As a Reviewer/Admin, resolve or dismiss exceptions
8. **Export** — Download verified CSV, audit reports, or hash manifests
9. **Verify Hash Chain** — Check the tamper-evident audit trail under **Audit & Hash Chain**

### Features

- **CSV Preview** — See column mappings and data types before processing
- **50+ Column Mappings** — Auto-detects messy column names
- **30+ Validation Rules** — Catches outliers, missing fields, invalid formats
- **AI Copilot Chat** — Ask follow-up questions about any exception
- **Bulk Operations** — Select multiple exceptions to explain/resolve at once
- **4 Export Formats** — Verified CSV, All CSV, Audit Report (JSON), Hash Manifest
- **Hash Chain** — SHA-256 linked records for tamper detection
- **Role-Based Access** — Analyst, Reviewer, and Admin roles

---

## 🔌 API Reference

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/auth/register` | Register new user | No |
| POST | `/api/auth/login` | Login and get JWT | No |
| GET | `/api/auth/me` | Get current user | Yes |
| POST | `/api/uploads` | Upload loan tape (CSV/Excel) | Analyst+ |
| GET | `/api/uploads` | List all uploads | Yes |
| GET | `/api/uploads/:id` | Get upload summary | Yes |
| GET | `/api/uploads/:id/records` | Get loan records | Yes |
| GET | `/api/uploads/:id/exceptions` | Get validation exceptions | Yes |
| POST | `/api/exceptions/:id/explain` | Get AI explanation | Yes |
| POST | `/api/exceptions/:id/resolve` | Resolve/dismiss exception | Reviewer+ |
| GET | `/api/audit/logs` | Get audit trail | Reviewer+ |
| GET | `/api/audit/dashboard` | Get dashboard stats | Yes |
| GET | `/api/audit/chain-verify/:id` | Verify hash chain integrity | Reviewer+ |

---

## 🐛 Troubleshooting

### Common Issues

#### "python3: command not found" (Mac/Linux)

```bash
# Try python instead of python3
python --version

# Or install Python
brew install python3        # Mac
sudo apt install python3    # Linux
```

#### "python: command not found" (Windows)

- Reinstall Python from [python.org](https://www.python.org/downloads/)
- During install, **check "Add Python to PATH"**
- Restart your terminal after installing

#### "node: command not found"

- Install Node.js from [nodejs.org](https://nodejs.org/)
- Or use a version manager like [nvm](https://github.com/nvm-sh/nvm):

#### Mac/Linux:
```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 20
nvm use 20
```

#### Windows:
```cmd
winget install OpenJS.NodeJS.LTS
:: Restart your terminal
```

#### PowerShell: "running scripts is disabled on this system"

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### Port 8000 already in use

#### Mac/Linux:
```bash
# Find and kill the process using port 8000
lsof -ti:8000 | xargs kill -9
```

#### Windows:
```cmd
:: Find process using port 8000
netstat -ano | findstr :8000
:: Kill it (replace PID with the actual number)
taskkill /PID <PID> /F
```

#### "ModuleNotFoundError" when starting backend

```bash
# Make sure your virtual environment is activated!
# Mac/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Then reinstall
pip install -r requirements.txt
```

#### Frontend shows blank page or errors

```bash
cd frontend
rm -rf node_modules
npm install
npm run dev
```

#### AI explanations not working

- Without a Grok API key, the app uses **mock responses** — this is normal
- If you have a key, make sure it's set in `backend/.env` or as an environment variable
- Check that the key starts with `xai-`

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
│ SQLite│   │  Ingestion │   │ Grok AI │
│  DB   │   │  Service   │   │ (xAI)   │
└───────┘   └───────────┘   └─────────┘
```

---

## 🧠 How It Works

1. **Column Detection** — Maps 50+ column name variants to 13 standard fields
2. **Type Coercion** — Converts strings to appropriate types (int/float/string)
3. **Rule Evaluation** — Each record passes through 30+ validation rules
4. **Exception Generation** — Violations create records with severity levels (Critical/Major/Minor)
5. **AI Explanation** — Grok AI generates human-readable explanations for each exception
6. **Quality Scoring** — Score = 100 − (weighted deductions per record)

### Hash Chain

Each record computes a SHA-256 hash from its data + the previous record's hash:

```
record[n].hash = SHA256(record[n-1].hash || sorted(field=value pairs))
```

The chain starts from `"GENESIS"` — tampering with any record breaks all subsequent hashes.

---

## 🎯 Tech Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | React 18, Tailwind CSS, React Router, Vite |
| **Backend** | FastAPI, SQLAlchemy (async), Pydantic |
| **AI** | Grok AI via xAI API (OpenAI-compatible) |
| **Database** | SQLite (async via aiosqlite) |
| **Auth** | JWT (python-jose), bcrypt |
| **Hashing** | SHA-256 (Python hashlib) |

---

**Built for Intain FinTech Challenge 2026 🏆**
