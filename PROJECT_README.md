# Smart Medical Report Interpreter

<div align="center">

![Medical Report Interpreter](https://img.shields.io/badge/Medical-Report%20Interpreter-blue)
![Python](https://img.shields.io/badge/Python-3.10-green)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-teal)
![Next.js](https://img.shields.io/badge/Next.js-14-black)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue)

**AI-Powered Medical Lab Report Analysis with OCR and Structured Result Parsing**

</div>

---

## 📋 Overview

Smart Medical Report Interpreter is a full-stack web application that helps users understand their medical lab reports. Upload an image or PDF of your lab report, and the system will:

- 🔍 **Extract text** using advanced OCR (PaddleOCR/EasyOCR)
- 📊 **Parse structured results** with test names, values, units, and reference ranges
- 🎨 **Color-code results** as Normal (green), High (red), Low (yellow), or Unknown (gray)
- 📝 **Generate explanations** in simple, non-medical language
- 💡 **Provide wellness tips** (general lifestyle suggestions only)
- ⚠️ **Display disclaimers** prominently (NOT medical advice)

## ⚡ Quick Start

### Prerequisites

- Docker & Docker Compose installed
- PostgreSQL running (credentials: `postgres/1234`)
- 8GB+ RAM recommended (for OCR models)

### Run with Docker (Recommended)

```bash
# 1. Clone or navigate to project directory
cd c:\xampp\htdocs\medical

# 2. Copy environment files
copy backend\.env.example backend\.env
copy frontend\.env.local.example frontend\.env.local

# 3. Start all services
docker-compose up -d

# 4. Wait for services to be ready (~30 seconds)

# 5. Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Alternative: Run Locally (Without Docker)

#### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Set up environment
copy .env.example .env
# Edit .env with your database credentials

# Run migrations
psql -U postgres -d postgres -f ..\schema.sql

# Start backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Set up environment
copy .env.local.example .env.local

# Start frontend
npm run dev
```

## 🏗️ Project Structure

```
medical/
├── backend/                    # FastAPI Backend
│   ├── main.py                # API endpoints
│   ├── config.py              # Configuration
│   ├── database.py            # Database connection
│   ├── models.py              # SQLAlchemy models
│   ├── ocr_service.py         # OCR processing (PaddleOCR/EasyOCR)
│   ├── parser_service.py      # Lab result parsing
│   ├── explanation_service.py # Generate explanations
│   ├── requirements.txt       # Python dependencies
│   ├── Dockerfile            # Backend Docker image
│   ├── .env.example          # Environment template
│   └── tests/                # Unit tests
│       ├── test_parser.py
│       └── fixtures/         # Sample OCR texts
│           ├── sample_cbc.txt
│           ├── sample_lipid.txt
│           └── sample_metabolic.txt
│
├── frontend/                  # Next.js Frontend
│   ├── pages/                # Next.js pages
│   │   ├── index.tsx         # Upload page
│   │   ├── reports/
│   │   │   ├── [id].tsx      # Report details
│   │   │   └── index.tsx     # Report history
│   │   └── _app.tsx
│   ├── components/           # React components
│   │   ├── Layout.tsx
│   │   ├── FileUploader.tsx
│   │   ├── StatusBadge.tsx
│   │   ├── ResultsTable.tsx
│   │   ├── SummaryCards.tsx
│   │   └── DisclaimerBox.tsx
│   ├── lib/
│   │   └── api.ts            # API client
│   ├── styles/
│   │   └── globals.css
│   ├── package.json
│   ├── Dockerfile
│   └── .env.local.example
│
├── schema.sql                # PostgreSQL schema
├── docker-compose.yml        # Docker orchestration
├── Makefile                  # Helper commands
└── README.md                 # This file
```

## 🗄️ Database Schema

The application uses PostgreSQL with the following tables:

- **users** - User accounts (optional for MVP)
- **reports** - Report metadata and status
- **report_files** - Uploaded file information
- **extracted_text** - OCR results (stored only if `save_report=true`)
- **lab_results** - Structured test results
- **explanations** - Generated summaries and tips
- **audit_logs** - Processing audit trail

See `schema.sql` for complete schema.

## 🔌 API Endpoints

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/reports/upload` | Upload medical report file |
| `GET` | `/api/reports/{id}` | Get full report with results |
| `GET` | `/api/reports/{id}/status` | Check processing status |
| `GET` | `/api/reports` | List all reports |
| `POST` | `/api/reports/demo` | Create demo report (no file) |
| `DELETE` | `/api/reports/{id}` | Delete report |

### Example: Upload Report

```bash
curl -X POST "http://localhost:8000/api/reports/upload" \
  -F "file=@lab_report.pdf" \
  -F "save_report=false"
```

Response:
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "queued",
  "error_message": null
}
```

## 🧪 Testing

### Run Backend Tests

```bash
# With Docker
docker-compose exec backend pytest tests/ -v

# Locally
cd backend
pytest tests/ -v
```

### Test Demo Report

Access http://localhost:3000 and click "Try Demo Report" to see the system work with sample data without uploading files.

## 📊 Sample Lab Reports

The `backend/tests/fixtures/` directory contains three sample lab reports:

1. **sample_cbc.txt** - Complete Blood Count
2. **sample_lipid.txt** - Lipid Panel
3. **sample_metabolic.txt** - Comprehensive Metabolic Panel

These are used for testing the parser without OCR.

## 🛡️ Privacy & Safety

### Privacy Features

- **Default: Files NOT saved** - Uploaded files are deleted after processing unless `save_report=true`
- **Only results stored** - Structured lab results saved, not raw images/PDFs (unless opted in)
- **No PHI in logs** - Sensitive data excluded from application logs

### Safety Guardrails

- ⚠️ **Prominent disclaimers** on every results page
- 🚫 **NO medical diagnosis** - System only explains test meanings
- 🚫 **NO medication recommendations** - No drug names or dosing
- 🚫 **NO treatment advice** - Always directs to healthcare provider
- ⚠️ **Critical value warnings** - Flags extremely abnormal results

### Disclaimer Example

```
⚠️ IMPORTANT MEDICAL DISCLAIMER:

This information is for educational purposes only and is NOT medical advice.
This tool does not diagnose, treat, cure, or prevent any disease.

- Always consult a licensed healthcare provider for medical advice
- Do not make medical decisions based solely on this information
- In emergencies, call your local emergency number immediately
```

## 🎨 User Flow

1. **Upload** - User visits homepage and uploads lab report (JPG/PNG/PDF)
2. **Processing** - System extracts text via OCR and parses lab results
3. **Results** - User sees:
   - Summary cards (# Normal, High, Low, Unknown)
   - Detailed table with color-coded results
   - Simplified explanations
   - General wellness tips
   - **Prominent disclaimer**
4. **History** - User can view previous reports

## 🚀 Deployment Notes

### Production Considerations

1. **Use Celery + Redis** for background processing (not BackgroundTasks)
2. **Switch to S3/Cloud Storage** instead of local filesystem
3. **Implement proper authentication** (JWT tokens)
4. **Rate limiting** to prevent abuse
5. **HTTPS only** for production
6. **Update SECRET_KEY** to a secure random value
7. **Set DEBUG=False**
8. **Configure proper CORS origins**
9. **Database backups** and replication
10. **Monitor OCR costs** if using cloud OCR services

### Environment Variables (Production)

```bash
# Backend
DATABASE_URL=postgresql://user:pass@prod-db:5432/medical
SECRET_KEY=<generate-with-openssl-rand-hex-32>
DEBUG=False
UPLOAD_DIR=/mnt/storage/uploads
CORS_ORIGINS=https://yourdomain.com

# Frontend
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
```

## 🛠️ Development Commands

```bash
# Start all services
make up

# View logs
make logs

# Run migrations
make migrate

# Run tests
make test

# Stop services
make down

# Rebuild images
make build

# Clean everything
make clean

# Access database
make db-shell

# Access backend shell
make backend-shell
```

## 🔧 Troubleshooting

### Issue: OCR not working

**Solution:** Ensure sufficient RAM (8GB+). PaddleOCR models are large.

```bash
# Check backend logs
docker-compose logs backend
```

### Issue: Database connection error

**Solution:** Verify PostgreSQL is running and credentials are correct.

```bash
# Test connection
psql -U postgres -h localhost -d postgres
```

### Issue: Frontend can't reach backend

**Solution:** Check CORS settings and ensure backend is running.

```bash
# Verify backend is accessible
curl http://localhost:8000/
```

### Issue: Processing takes too long

**Solution:** For large PDFs with many pages, OCR can be slow. Consider:
- Using text-based PDFs (faster extraction)
- Reducing image DPI
- Switching to cloud OCR services

## 📚 Tech Stack

### Backend
- **Python 3.10+**
- **FastAPI** - Modern async API framework
- **SQLAlchemy** - ORM
- **PostgreSQL** - Database
- **PaddleOCR** - Primary OCR engine
- **EasyOCR** - Fallback OCR engine
- **pdfplumber** - PDF text extraction
- **OpenCV** - Image preprocessing

### Frontend
- **Next.js 14** - React framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **Axios** - API client
- **React Dropzone** - File uploads

### Infrastructure
- **Docker & Docker Compose** - Containerization
- **Uvicorn** - ASGI server

## 🤝 Contributing

This is an educational project. Contributions welcome!

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## ⚖️ Legal & Ethics

**IMPORTANT**: This tool is for educational purposes ONLY.

- NOT approved for clinical use
- NOT a medical device
- NOT a substitute for professional medical advice
- Users must consult healthcare providers for medical decisions
- Developers NOT liable for any medical decisions made using this tool

## 📄 License

[Specify your license here - MIT, Apache 2.0, etc.]

## 📞 Support

For questions or issues:
- Open an issue on GitHub
- Check existing issues for solutions
- Review the troubleshooting section

---

<div align="center">

**⚠️ FOR EDUCATIONAL PURPOSES ONLY - NOT MEDICAL ADVICE ⚠️**

Made with ❤️ for better health literacy

</div>
