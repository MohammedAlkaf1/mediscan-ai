"""Test the upload API endpoint with an existing uploaded file"""
import requests
import os

BASE_URL = "http://localhost:8000"

# Check health
print("1. Checking backend health...")
try:
    r = requests.get(f"{BASE_URL}/health", timeout=5)
    print(f"   Status: {r.status_code}")
    print(f"   Response: {r.json()}")
except Exception as e:
    print(f"   ERROR: {e}")
    exit(1)

# Test OCR directly through endpoint
print("\n2. Testing file upload with OCR...")
test_file = "uploads/5f25b803-d3a1-4296-a51c-9dbb5d738736.png"
if not os.path.exists(test_file):
    print(f"   Test file not found: {test_file}")
    exit(1)

with open(test_file, "rb") as f:
    files = {"file": ("test_report.png", f, "image/png")}
    data = {"save_report": "true"}
    try:
        r = requests.post(f"{BASE_URL}/api/upload", files=files, data=data, timeout=120)
        print(f"   Status: {r.status_code}")
        resp = r.json()
        print(f"   Response: {resp}")
        
        if r.status_code == 200:
            report_id = resp.get("report_id") or resp.get("id")
            print(f"\n3. Checking report status (id: {report_id})...")
            import time
            for i in range(10):
                time.sleep(3)
                r2 = requests.get(f"{BASE_URL}/api/reports/{report_id}", timeout=10)
                if r2.status_code == 200:
                    status = r2.json().get("status")
                    print(f"   Attempt {i+1}: status={status}")
                    if status in ("done", "error"):
                        print(f"   Final response: {r2.json()}")
                        break
                else:
                    print(f"   Attempt {i+1}: HTTP {r2.status_code}")
    except Exception as e:
        print(f"   ERROR: {e}")
