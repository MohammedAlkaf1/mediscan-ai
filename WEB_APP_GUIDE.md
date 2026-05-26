# Web Application - Access Guide

## 🌐 This is a Web Application

The Smart Medical Report Interpreter is built as a **web application** that runs in your browser. No desktop installation needed!

## 🚀 How to Run the Web App

### Option 1: Quick Start (Easiest)

**Double-click** one of these files:
- `start-webapp.bat` (Windows Batch)
- `start-webapp.ps1` (PowerShell - right-click → Run with PowerShell)

The browser will automatically open to http://localhost:3000

### Option 2: Manual Start

```powershell
cd c:\xampp\htdocs\medical
docker-compose up -d
```

Then open your browser to: **http://localhost:3000**

## 🌐 Web URLs

Once running, access these URLs in your web browser:

| Service | URL | Description |
|---------|-----|-------------|
| **Main Web App** | http://localhost:3000 | User interface - Upload & View Reports |
| **API Server** | http://localhost:8000 | Backend REST API |
| **API Docs** | http://localhost:8000/docs | Interactive API documentation |

## 📱 Access from Other Devices (Same Network)

To access the web app from your phone or another computer on the same network:

1. Find your computer's IP address:
   ```powershell
   ipconfig
   # Look for "IPv4 Address" (e.g., 192.168.1.100)
   ```

2. On other device, open browser to:
   - `http://YOUR-IP:3000` (e.g., http://192.168.1.100:3000)

3. Update CORS settings in `backend/.env`:
   ```
   CORS_ORIGINS=http://localhost:3000,http://YOUR-IP:3000
   ```

## 🌍 Deploy to Public Web (Future)

For production deployment to make it accessible from anywhere:

1. **Deploy Backend**: 
   - Heroku, AWS, Google Cloud, DigitalOcean
   - Use managed PostgreSQL (AWS RDS, etc.)

2. **Deploy Frontend**:
   - Vercel (recommended for Next.js)
   - Netlify
   - AWS Amplify

3. **Update Environment Variables**:
   ```
   NEXT_PUBLIC_API_URL=https://your-backend.com
   ```

## 🖥️ Convert to Desktop App (Future)

When you're ready to create a desktop application:

### Option 1: Electron (Easiest)
- Wrap the Next.js web app in Electron
- Creates Windows/Mac/Linux desktop app
- Still uses web technologies underneath

### Option 2: Tauri (Modern)
- Lighter than Electron
- Better performance
- Rust-based

### Option 3: Python Desktop (PyQt/Tkinter)
- Rewrite frontend in Python
- Keep FastAPI backend as-is
- Native desktop feel

## 📊 Current Architecture (Web-Based)

```
┌─────────────────┐
│   Web Browser   │  ← User accesses via http://localhost:3000
└────────┬────────┘
         │ HTTP
         ↓
┌─────────────────┐
│  Next.js        │  ← Frontend (Port 3000)
│  (React/TS)     │
└────────┬────────┘
         │ API Calls
         ↓
┌─────────────────┐
│  FastAPI        │  ← Backend (Port 8000)
│  (Python)       │
└────────┬────────┘
         │ SQL
         ↓
┌─────────────────┐
│  PostgreSQL     │  ← Database (Port 5432)
└─────────────────┘
```

## ✅ Advantages of Web App

- ✅ No installation needed
- ✅ Access from any device with a browser
- ✅ Easy to update (just restart server)
- ✅ Works on Windows, Mac, Linux, mobile
- ✅ Easy to share (just send URL)
- ✅ Can be deployed to cloud easily

## 🎯 Quick Test

1. Run the web app (double-click `start-webapp.bat`)
2. Browser opens to http://localhost:3000
3. Click **"Try Demo Report"**
4. See results instantly!

---

**This IS the web application!** Everything is already set up for web access. Desktop conversion can come later when needed.
