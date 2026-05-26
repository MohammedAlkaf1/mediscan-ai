"""Check the latest report"""
from database import SessionLocal
import models
import uuid

db = SessionLocal()

# Get the most recent report
report = db.query(models.Report).order_by(models.Report.created_at.desc()).first()

if report:
    print(f"Report ID: {report.id}")
    print(f"Status: {report.status}")
    print(f"Type: {report.report_type}")
    print(f"Created: {report.created_at}")
    
    # Get explanation
    exp = db.query(models.Explanation).filter(models.Explanation.report_id == report.id).first()
    
    if exp:
        print("\n" + "="*80)
        print("FULL EXPLANATION SUMMARY:")
        print("="*80)
        print(exp.summary)
        print("\n" + "="*80)
        print("FULL TIPS:")
        print("="*80)
        print(exp.tips)
        print("\n" + "="*80)
    else:
        print("\n❌ No explanation found")
else:
    print("❌ Report not found")

db.close()
