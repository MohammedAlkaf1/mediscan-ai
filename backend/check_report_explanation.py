"""Check report explanation"""
from database import SessionLocal
import models

db = SessionLocal()

# Get the most recent report
report = db.query(models.Report).filter(models.Report.status == 'done').order_by(models.Report.created_at.desc()).first()

if report:
    print(f"Report ID: {report.id}")
    print(f"Status: {report.status}")
    print(f"Type: {report.report_type}")
    print(f"Created: {report.created_at}")
    
    # Get explanation
    exp = db.query(models.Explanation).filter(models.Explanation.report_id == report.id).first()
    
    if exp:
        print("\n" + "="*60)
        print("EXPLANATION SUMMARY:")
        print("="*60)
        print(exp.summary[:500])
        print("\n" + "="*60)
        print("TIPS (first 300 chars):")
        print("="*60)
        print(exp.tips[:300] if exp.tips else "None")
    else:
        print("\n❌ No explanation found for this report")
else:
    print("❌ Report not found")

db.close()
