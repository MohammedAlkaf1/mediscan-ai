# System Control Guide
## How to Start and Stop the Medical Report Interpreter

---

## 🟢 **START THE SYSTEM**

### **Option 1: Quick Start (Recommended)**
```powershell
.\start-website.ps1
```

This will:
- Check PostgreSQL, Python, and Node.js
- Install any missing dependencies
- Start Backend server (port 8000)
- Start Frontend website (port 3000)
- Open browser automatically

### **Option 2: Manual Start**

**Step 1: Start Backend**
```powershell
cd c:\xampp\htdocs\medical\backend
py -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Step 2: Start Frontend** (in a new terminal)
```powershell
cd c:\xampp\htdocs\medical\frontend
npm run dev
```

**Step 3: Open Browser**
```
http://localhost:3000
```

---

## 🔴 **STOP THE SYSTEM**

### **Option 1: Quick Stop (Recommended)**
```powershell
.\stop-website.ps1
```

This automatically stops all backend and frontend processes.

### **Option 2: Manual Stop**

**Close Terminal Windows:**
- Close the PowerShell window running the backend
- Close the PowerShell window running the frontend

**OR use Task Manager:**
1. Press `Ctrl + Shift + Esc`
2. Find and end these processes:
   - `python.exe` (Backend)
   - `node.exe` (Frontend)

**OR use PowerShell commands:**
```powershell
# Stop Backend
Get-Process python,uvicorn -ErrorAction SilentlyContinue | Stop-Process -Force

# Stop Frontend
Get-Process node -ErrorAction SilentlyContinue | Stop-Process -Force
```

---

## 📊 **CHECK SYSTEM STATUS**

### Check if services are running:
```powershell
# Check Backend (port 8000)
Test-NetConnection -ComputerName localhost -Port 8000 -InformationLevel Quiet

# Check Frontend (port 3000)
Test-NetConnection -ComputerName localhost -Port 3000 -InformationLevel Quiet
```

### View running processes:
```powershell
# Backend processes
Get-Process python,uvicorn -ErrorAction SilentlyContinue

# Frontend processes
Get-Process node -ErrorAction SilentlyContinue
```

---

## 🔧 **TROUBLESHOOTING**

### "Port already in use" error:

**Check what's using the port:**
```powershell
# Check port 8000
netstat -ano | findstr :8000

# Check port 3000
netstat -ano | findstr :3000
```

**Kill the process:**
```powershell
# Stop all Python/Node processes
Get-Process python,node -ErrorAction SilentlyContinue | Stop-Process -Force
```

### Backend won't start:

1. **Check PostgreSQL is running:**
   ```powershell
   Get-Service -Name "*postgres*"
   ```

2. **Test database connection:**
   ```powershell
   cd c:\xampp\htdocs\medical\backend
   py test_db_connection.py
   ```

3. **Check dependencies:**
   ```powershell
   py -m pip list | Select-String "fastapi|uvicorn|paddleocr"
   ```

### Frontend won't start:

1. **Check Node.js is installed:**
   ```powershell
   node --version
   npm --version
   ```

2. **Reinstall dependencies:**
   ```powershell
   cd c:\xampp\htdocs\medical\frontend
   Remove-Item -Recurse -Force node_modules
   npm install
   ```

---

## 🚀 **QUICK REFERENCE**

| Action | Command |
|--------|---------|
| **Start Everything** | `.\start-website.ps1` |
| **Stop Everything** | `.\stop-website.ps1` |
| **View Backend** | http://localhost:8000/docs |
| **View Frontend** | http://localhost:3000 |
| **Check Backend Status** | `Test-NetConnection localhost -Port 8000` |
| **Check Frontend Status** | `Test-NetConnection localhost -Port 3000` |
| **Restart Backend Only** | Stop Python → `cd backend` → `py -m uvicorn main:app --reload --host 0.0.0.0 --port 8000` |
| **Restart Frontend Only** | Stop Node → `cd frontend` → `npm run dev` |

---

## 🐳 **DOCKER MODE (Alternative)**

If you prefer Docker:

**Start:**
```powershell
.\start-webapp.ps1
```

**Stop:**
```powershell
docker-compose down
```

**View logs:**
```powershell
docker-compose logs -f
```

---

## ⚙️ **SYSTEM REQUIREMENTS**

- **PostgreSQL 18** (must be running)
- **Python 3.10+** with dependencies installed
- **Node.js 18+** with npm
- **PaddleOCR** (automatically installed)
- **Free Ports:** 3000, 8000

---

## 📝 **NOTES**

- The backend must start before the frontend
- PostgreSQL must be running before starting the backend
- First startup takes longer (downloads OCR models ~110MB)
- Use `--reload` flag during development for auto-restart on code changes
- Production deployment uses different commands (see DEPLOYMENT.md)

---

**Need help?** Check the logs or run system diagnostics
