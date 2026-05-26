# 🔧 FIX: "No meaningful text extracted from file"

## Problem
When uploading files, you get the error: **"No meaningful text extracted from file"**

## Root Cause
**PaddleOCR is not installed** - the OCR library needed to extract text from images and PDFs.

---

## ✅ Solution (Quick Fix)

### Option 1: Use PowerShell Script (Recommended)
```powershell
# 1. Stop the backend server (Ctrl+C in backend terminal)

# 2. Run installation script
.\install-ocr.ps1

# 3. Restart backend
cd backend
py -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Option 2: Manual Installation
```powershell
# 1. Stop the backend server first!

# 2. Install PaddleOCR
py -m pip install paddleocr

# 3. Install PaddlePaddle
py -m pip install paddlepaddle

# 4. Verify installation
py -c "from paddleocr import PaddleOCR; print('Success!')"

# 5. Restart backend
cd backend
py -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

---

## 🧪 Test After Installation

1. **Open** http://localhost:3000
2. **Login** with your account
3. **Upload** a test PDF or image
4. **Wait** for processing
5. **Check** if extraction worked!

---

## ⚠️ Troubleshooting

### "Access is denied" or "[WinError 5]"
**Solution**: The backend is still running. Stop it first!
```powershell
# Find and kill Python processes
Get-Process python | Stop-Process -Force

# OR just press Ctrl+C in backend terminal
```

### "No module named 'paddleocr'" persists
**Solution**: Restart everything
```powershell
# 1. Close backend terminal completely
# 2. Open new PowerShell
# 3. cd c:\xampp\htdocs\medical\backend
# 4. py -m pip install paddleocr paddlepaddle
# 5. py -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Installation takes forever
**Patience!** PaddlePaddle is a large package (~200MB). It can take 2-5 minutes.

### Still not working?
Check backend logs for detailed error:
```powershell
# Look at the terminal where backend is running
# You should see OCR initialization messages
```

---

## 📝 Why This Happened

PaddleOCR was listed in `requirements.txt` but wasn't installed during the initial setup. This happens when:
- Requirements were installed before PaddleOCR was added
- Installation was interrupted
- Package conflicts occurred

---

## ✅ Verification

After installation, you should see this in backend logs when it starts:
```
INFO - PaddleOCR initialized successfully
```

If you see this, OCR will work! 🎉

---

## 🚀 Alternative: Use Demo Report

If you just want to test the system without OCR:
```bash
# Use the demo endpoint (no file upload needed)
POST http://localhost:8000/api/reports/demo

# This creates a sample report with pre-extracted data
```

---

**Need more help?**
Check the backend terminal for detailed error messages!
