"""Test upload with correct endpoint"""
import requests
import time
import os
import warnings
warnings.filterwarnings("ignore")

BASE = "http://localhost:8000"

print("=== UPLOAD TEST ===\n")

# Upload file
test_file = "uploads/5f25b803-d3a1-4296-a51c-9dbb5d738736.png"
print(f"Uploading: {test_file} ({os.path.getsize(test_file)} bytes)")

with open(test_file, "rb") as f:
    files = {"file": ("GNU_Health_lab_report_sample.png", f, "image/png")}
    data = {"save_report": "true"}
    r = requests.post(f"{BASE}/api/reports/upload", files=files, data=data, timeout=120)

print(f"Upload status: {r.status_code}")
resp = r.json()
print(f"Response: {resp}")

if r.status_code != 200:
    print("UPLOAD FAILED!")
    exit(1)

report_id = resp["id"]
print(f"\nReport ID: {report_id}")
print("Waiting for processing...\n")

for i in range(20):
    time.sleep(3)
    r2 = requests.get(f"{BASE}/api/reports/{report_id}/status", timeout=10)
    status_data = r2.json()
    status = status_data.get("status", "unknown")
    error = status_data.get("error_message", "")
    print(f"  [{i+1}] Status: {status}" + (f" | Error: {error}" if error else ""))
    
    if status == "done":
        print("\n=== SUCCESS! Report processed! ===")
        r3 = requests.get(f"{BASE}/api/reports/{report_id}", timeout=10)
        if r3.status_code == 200:
            report = r3.json()
            print(f"Report type: {report.get('report_type', 'N/A')}")
            results = report.get('lab_results', [])
            print(f"Lab results found: {len(results)}")
            for lr in results[:5]:
                print(f"  - {lr['test_name']}: {lr.get('value_text', lr.get('value_numeric', 'N/A'))} {lr.get('unit', '')} [{lr.get('status', '')}]")
        break
    elif status == "error":
        print(f"\n=== FAILED: {error} ===")
        break
else:
    print("\nTimeout waiting for processing")
