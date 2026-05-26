# 🏥 MediScan AI

> **AI-Powered Medical Lab Report Interpreter**
>
> Upload your lab report · OCR extracts the text · AI explains the results · Download a professional PDF

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Frontend-Next.js_14-black?logo=nextdotjs)](https://nextjs.org/)
[![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL_16-4169E1?logo=postgresql)](https://www.postgresql.org/)
[![Gemini AI](https://img.shields.io/badge/AI-Gemini_2.5_Flash-blue?logo=google)](https://deepmind.google/technologies/gemini/)

---

## ⚠️ Medical Disclaimer

**MediScan AI is for educational and informational purposes only.**
It does not provide medical diagnosis, treatment, or professional medical advice.
Always consult a licensed healthcare professional before making any health-related decisions.

---

## 📋 Problem Statement

Understanding medical lab reports is challenging for most patients. Values like "WBC 7.2 x10³/µL" or "HbA1c 5.7%" mean little without context. MediScan AI bridges this gap by:

- Extracting lab values from uploaded images and PDFs using OCR
- Classifying results as normal / high / low / unknown
- Generating plain-language AI explanations via Google Gemini
- Tracking health trends over time across multiple reports
- Enabling secure report sharing with family or healthcare providers

---

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| 📤 **Smart Upload** | Drag-and-drop JPG, PNG, or PDF lab reports |
| 🔍 **OCR Extraction** | EasyOCR + pdfplumber extract text from any format |
| 🧪 **Lab Parsing** | Structured extraction of test name, value, unit, reference range |
| 🎨 **Color-Coded Results** | Green = normal · Red = high · Blue = low · Gray = unknown |
| 🤖 **AI Explanations** | Google Gemini generates simple, educational explanations |
| 📊 **Trend Analytics** | Track lab values across multiple reports over time |
| 🔗 **Secure Sharing** | Generate expiring, optionally password-protected share links |
| 📄 **PDF Export** | Download a professional PDF report with disclaimer |
| 🔐 **Authentication** | JWT-based login and registration |
| 📱 **Responsive UI** | Works on desktop, tablet, and mobile |

---

## 🏗️ System Architecture

```
┌─────────────────┐     ┌────────────────────────────────────────┐
│   Next.js 14    │────▶│            FastAPI Backend              │
│   (Port 3000)   │◀────│            (Port 8000)                  │
│                 │     │                                         │
│  • Upload/Dash  │     │  ┌────────┐  ┌────────┐  ┌──────────┐  │
│  • Report view  │     │  │  OCR   │  │ Parser │  │  Gemini  │  │
│  • History      │     │  │EasyOCR │  │Service │  │   API    │  │
│  • Analytics    │     │  └────────┘  └────────┘  └──────────┘  │
│  • Share view   │     │                                         │
└─────────────────┘     │  ┌──────────────────────────────────┐  │
                         │  │         PostgreSQL DB            │  │
                         │  │  users · reports · lab_results   │  │
                         │  │  explanations · shared_reports   │  │
                         │  └──────────────────────────────────┘  │
                         └────────────────────────────────────────┘
```

### OCR-to-AI Workflow

```
Upload PDF/Image
      │
      ▼
  [EasyOCR / pdfplumber]
  Extract raw text
      │
      ▼
  [Parser Service]
  Structured lab results
  (test_name, value, unit, ref_range, status)
      │
      ▼
  [Gemini 2.5 Flash]  ─── or ─── [Rule-Based Fallback]
  Patient-friendly explanation
      │
      ▼
  Store in PostgreSQL
  Return to frontend
```

---

## 🖥️ Pages Overview

| Page | URL | Description |
|------|-----|-------------|
| Dashboard / Upload | `/` | Stats overview + file upload |
| Report Detail | `/reports/[id]` | Full results, AI explanation, actions |
| History | `/reports` | Searchable, filterable list of all reports |
| Analytics | `/analytics` | Health trends over time (requires login) |
| Shared Report | `/shared/[token]` | Read-only public view via share link |
| Login | `/auth/login` | JWT authentication |
| Register | `/auth/register` | New account creation |

---

## ⚙️ Tech Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| Frontend | Next.js + TailwindCSS | 14 / 3.3 |
| Backend | FastAPI | 0.104+ |
| Database | PostgreSQL | 16 |
| ORM | SQLAlchemy | 2.x |
| OCR | EasyOCR + pdfplumber | Latest |
| AI | Google Gemini 2.5 Flash | API |
| PDF | ReportLab | 4.x |
| Auth | JWT (python-jose) + bcrypt | Latest |
| Container | Docker + docker-compose | Latest |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- PostgreSQL 15+ **OR** Docker Desktop

---

### Option A — Local Development (No Docker)

#### 1. Clone and enter the project

```bash
git clone <your-repo-url>
cd medical
```

#### 2. Set up the backend

```powershell
cd backend

# Create virtual environment
python -m venv venv
.\venv\Scripts\activate        # Windows PowerShell
# source venv/bin/activate      # Linux / macOS

# Install dependencies
pip install -r requirements.txt

# Configure environment
copy .env.example .env         # Windows
# cp .env.example .env         # Linux/macOS
# Edit .env – set DATABASE_URL and optionally GEMINI_API_KEY
```

#### 3. Create the PostgreSQL database

```sql
-- Connect to PostgreSQL and run:
CREATE DATABASE medical;
```

Tables are created automatically on first startup.

#### 4. Start the backend

```bash
# From the backend/ directory
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Backend → http://localhost:8000  
API docs → http://localhost:8000/docs

#### 5. Set up the frontend

```powershell
cd ../frontend

npm install

copy .env.local.example .env.local    # Windows
# cp .env.local.example .env.local    # Linux/macOS
```

#### 6. Start the frontend

```bash
npm run dev
```

Frontend → http://localhost:3000

---

### Option B — Docker Compose (Recommended for demo)

```bash
# Create a .env file from the example
copy .env.example .env     # Windows (or cp on Linux)

# Set GEMINI_API_KEY and SECRET_KEY in .env (at minimum)

# Build and start all services
docker compose up --build -d

# Check health
curl http://localhost:8000/health
```

Stop everything: `docker compose down`

---

## 🔑 Environment Variables

### Backend (`backend/.env`)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | ✅ | — | PostgreSQL connection string |
| `SECRET_KEY` | ✅ | — | JWT signing secret |
| `FRONTEND_URL` | ✅ | `http://localhost:3000` | Used for share link generation |
| `GEMINI_API_KEY` | For AI | — | Google AI Studio key |
| `ENABLE_AI_EXPLANATIONS` | — | `false` | Set `true` to use Gemini |
| `GEMINI_MODEL` | — | `gemini-2.5-flash-preview-05-20` | Gemini model ID |
| `MAX_FILE_SIZE` | — | `10485760` | Max upload bytes (10 MB) |
| `DEBUG` | — | `false` | Enable reload and debug output |
| `CORS_ORIGINS` | — | `http://localhost:3000` | Comma-separated allowed origins |

**Generate a secure `SECRET_KEY`:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Frontend (`frontend/.env.local`)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `NEXT_PUBLIC_API_URL` | ✅ | `http://localhost:8000` | Backend API URL |

---

## 🗄️ Database Setup

Tables are created automatically on startup via `Base.metadata.create_all()`.

Key tables:

| Table | Purpose |
|-------|---------|
| `users` | Registered accounts |
| `reports` | Uploaded lab reports |
| `report_files` | File references |
| `extracted_text` | OCR output |
| `lab_results` | Structured parsed results |
| `explanations` | AI summaries |
| `shared_reports` | Share link records |
| `audit_logs` | Processing audit trail |

---

## 🧪 Testing

### Backend

```bash
cd backend
pip install pytest httpx

# All tests
pytest tests/ -v

# Specific file
pytest tests/test_api.py -v
pytest tests/test_parser.py -v

# With coverage
pip install pytest-cov
pytest tests/ --cov=. --cov-report=term-missing
```

### Frontend

```bash
cd frontend
npm run build    # Check for build errors
npm run lint     # ESLint check
```

---

## 📄 PDF Export

- Available on any `done` report via the **PDF** button or `GET /api/reports/{id}/pdf`
- PDF includes: title, date, lab results table, AI explanation, wellness tips, full medical disclaimer
- File is named `mediscan_<type>_<id-prefix>.pdf`
- Shared reports also expose a PDF download button

---

## 🔗 Report Sharing

1. Open any completed report → click **Share**
2. Choose expiry (1–90 days), optional password protection
3. Copy and share the URL
4. Recipient sees a read-only view with disclaimer
5. Revoke any link at any time

API:
- `POST /api/reports/{id}/share` — create link
- `GET /api/reports/{id}/shares` — list active links
- `DELETE /api/reports/{id}/share/{token}` — revoke link
- `GET /api/shared/{token}` — public access (no auth required)

---

## 📈 Health Trends / Analytics

The `/analytics` page shows how lab values change across reports over time:

- Requires at least **2 reports** with the same test
- Displays SVG line chart with color-coded data points
- Shows increasing / decreasing / stable trend badge
- Full measurement history table below the chart
- Available for: Hemoglobin, Glucose, Cholesterol, HbA1c, and any other parsed test

---

## 🔒 Privacy & Security

- Uploaded files are deleted after processing by default
- Users can only access their own reports
- JWT tokens expire after 24 hours
- Share link tokens are cryptographically random (32-byte URL-safe)
- Passwords on share links are bcrypt-hashed
- Stack traces are **never** exposed in API responses
- Medical data is **never** logged

---

## 🐳 Docker Reference

```bash
# Start all services
docker compose up -d

# View logs
docker compose logs -f backend
docker compose logs -f frontend

# Stop and clean
docker compose down

# Rebuild after code changes
docker compose up --build
```

Services and ports:
- `mediscan_frontend` → http://localhost:3000
- `mediscan_backend` → http://localhost:8000
- `mediscan_postgres` → localhost:5432

---

## 🔮 Future Improvements

- [ ] Multi-language support (Arabic, French, etc.)
- [ ] PaddleOCR option for higher accuracy
- [ ] Custom reference ranges per user
- [ ] Doctor/patient role system
- [ ] Email alerts for critical values
- [ ] Mobile app (React Native)
- [ ] DICOM / HL7 FHIR integration
- [ ] Batch report upload
- [ ] Two-factor authentication

---

*Built with ❤️ using FastAPI, Next.js, and Google Gemini AI*
