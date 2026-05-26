# Quick Start Guide

## Prerequisites Check

Before starting, ensure you have:

- ✅ Docker Desktop installed and running
- ✅ PostgreSQL 18 running (default credentials: `postgres/1234`)
- ✅ At least 8GB RAM available
- ✅ Ports 3000, 5432, and 8000 available

## 🚀 5-Minute Setup

### Step 1: Start Services

```powershell
# Navigate to project directory
cd c:\xampp\htdocs\medical

# Start all services with Docker Compose
docker-compose up -d

# Wait about 30 seconds for services to initialize
```

### Step 2: Verify Services

```powershell
# Check all services are running
docker-compose ps

# You should see:
# - medical_postgres   (running on port 5432)
# - medical_backend    (running on port 8000)
# - medical_frontend   (running on port 3000)
```

### Step 3: Access Application

Open your browser and navigate to:

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

### Step 4: Try Demo

1. Go to http://localhost:3000
2. Click **"Try Demo Report"** button
3. See instant results with sample lab data!

OR

1. Upload your own lab report (JPG, PNG, or PDF)
2. Wait for processing (~10-30 seconds)
3. View your results!

## 🎯 What to Test

### Test 1: Demo Report
- Click "Try Demo Report" on homepage
- Should instantly show results with:
  - Summary cards (Normal, High, Low counts)
  - Detailed results table
  - Explanations in simple language
  - Wellness tips
  - Disclaimer

### Test 2: Upload Image
- Use a screenshot or photo of a lab report
- Supported: JPG, PNG (max 10MB)
- Processing time: 10-30 seconds

### Test 3: Upload PDF
- Use a PDF lab report
- System will try text extraction first (fast)
- Falls back to OCR if needed (slower)

### Test 4: View History
- Click "History" in navigation
- See all previously processed reports
- Click any report to view details

## 🐛 Common Issues & Fixes

### Issue: "Connection refused" error

**Cause**: Services not fully started

**Fix**:
```powershell
# Check service status
docker-compose ps

# Restart services
docker-compose restart

# View logs for errors
docker-compose logs backend
```

### Issue: OCR taking too long

**Cause**: Large file or low RAM

**Fix**:
- Use smaller image files (<2MB)
- Try text-based PDFs instead of scanned images
- Ensure Docker has enough RAM allocated (8GB+)

### Issue: "Module not found" errors in backend

**Cause**: Dependencies not installed

**Fix**:
```powershell
# Rebuild backend container
docker-compose build backend
docker-compose up -d backend
```

### Issue: Frontend can't connect to backend

**Cause**: CORS or network issue

**Fix**:
1. Ensure backend is running: `docker-compose ps`
2. Test backend: http://localhost:8000
3. Check browser console for errors

## 📝 Development Workflow

### Make Code Changes

#### Backend Changes:
```powershell
# Edit files in backend/
# Changes auto-reload (FastAPI reload enabled)

# If you need to restart:
docker-compose restart backend
```

#### Frontend Changes:
```powershell
# Edit files in frontend/
# Changes auto-reload (Next.js hot reload)

# If you need to restart:
docker-compose restart frontend
```

### Run Tests

```powershell
# Backend unit tests
docker-compose exec backend pytest tests/ -v

# Should show all tests passing
```

### View Logs

```powershell
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres
```

### Database Access

```powershell
# Connect to PostgreSQL
docker-compose exec postgres psql -U postgres -d postgres

# Run queries
SELECT * FROM reports;
SELECT * FROM lab_results;
\q  # to exit
```

## 🧹 Cleanup

### Stop Services (Keep Data)

```powershell
docker-compose down
```

### Full Cleanup (Remove All Data)

```powershell
# Remove containers, volumes, and images
docker-compose down -v --rmi all

# This will delete:
# - All uploaded files
# - All database data
# - All processed reports
```

## 🎓 Learning Path

### For Beginners:

1. Start with **Demo Report** - no uploads needed
2. Review the **results page** layout
3. Read the **explanations** section
4. Check out the **API docs** at http://localhost:8000/docs

### For Developers:

1. Review `backend/main.py` - API endpoints
2. Study `parser_service.py` - How parsing works
3. Read `ocr_service.py` - OCR integration
4. Check `frontend/pages/` - UI pages

### For Testing:

1. Use sample fixtures in `backend/tests/fixtures/`
2. Run `pytest` to see parser in action
3. Try uploading different report formats
4. Test error handling (invalid files, etc.)

## 📚 Next Steps

- Read full [PROJECT_README.md](PROJECT_README.md) for detailed documentation
- Explore API endpoints at http://localhost:8000/docs
- Review database schema in `schema.sql`
- Check out code comments in Python and TypeScript files

## 🆘 Get Help

If you encounter issues:

1. Check this guide's troubleshooting section
2. Review logs: `docker-compose logs`
3. Verify all services are running: `docker-compose ps`
4. Ensure ports aren't in use by other applications
5. Check Docker has enough resources allocated

## ✅ Success Checklist

- [ ] All 3 services running (`docker-compose ps`)
- [ ] Frontend accessible at http://localhost:3000
- [ ] Backend API responding at http://localhost:8000
- [ ] Demo report works (instant results)
- [ ] Upload functionality works
- [ ] Results page displays correctly
- [ ] History page shows reports

---

**Ready to go!** Start by opening http://localhost:3000 in your browser. 🚀
