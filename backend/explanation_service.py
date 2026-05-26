"""
Explanation Service for generating simplified explanations of lab results
"""
import logging
from typing import List, Dict, Tuple
from parser_service import ParsedLabResult

logger = logging.getLogger(__name__)

# Standard disclaimer (removed - no longer displayed)
DISCLAIMER = ""


# Test explanations
TEST_EXPLANATIONS = {
    "Glucose": {
        "what": "Glucose measures the amount of sugar in your blood. It's important for energy.",
        "normal": "Your glucose level is within the normal range. Keep maintaining a balanced diet.",
        "high": "Your glucose level is higher than normal. Persistently high glucose may indicate diabetes risk. Consult your doctor.",
        "low": "Your glucose level is lower than normal. Low blood sugar can cause dizziness or weakness. Discuss with your doctor.",
        "urgent": {"threshold": 300, "message": "⚠️ Very high glucose level. Seek medical attention soon."}
    },
    "Hemoglobin": {
        "what": "Hemoglobin carries oxygen in your blood. It's essential for energy and organ function.",
        "normal": "Your hemoglobin level is normal. This suggests healthy red blood cell production.",
        "high": "Your hemoglobin is higher than normal. This could be due to dehydration or other factors. Consult your doctor.",
        "low": "Your hemoglobin is lower than normal, which may indicate anemia. Your doctor can help determine the cause.",
        "urgent": {"threshold_low": 7, "message": "⚠️ Very low hemoglobin. Seek medical attention."}
    },
    "White Blood Cells": {
        "what": "White blood cells fight infections and are part of your immune system.",
        "normal": "Your white blood cell count is normal, suggesting healthy immune function.",
        "high": "Your white blood cell count is elevated. This might indicate infection or inflammation. Consult your doctor.",
        "low": "Your white blood cell count is lower than normal. This may affect immune function. Discuss with your doctor.",
        "urgent": {"threshold_low": 2, "threshold_high": 30, "message": "⚠️ Abnormal white blood cell count. Seek medical attention."}
    },
    "Platelets": {
        "what": "Platelets help your blood clot and prevent bleeding.",
        "normal": "Your platelet count is normal, supporting healthy blood clotting.",
        "high": "Your platelet count is elevated. Your doctor can determine if this needs attention.",
        "low": "Your platelet count is lower than normal. Low platelets can affect blood clotting. Consult your doctor.",
        "urgent": {"threshold_low": 50, "message": "⚠️ Very low platelet count. Seek medical attention."}
    },
    "Total Cholesterol": {
        "what": "Cholesterol is a fatty substance that can affect heart health.",
        "normal": "Your total cholesterol is within the normal range. Continue heart-healthy habits.",
        "high": "Your cholesterol is higher than recommended. Diet and lifestyle changes may help. Consult your doctor.",
        "low": "Your cholesterol is lower than normal. Usually not a concern, but discuss with your doctor.",
    },
    "LDL Cholesterol": {
        "what": "LDL is often called 'bad cholesterol' because high levels can increase heart disease risk.",
        "normal": "Your LDL cholesterol is at a healthy level.",
        "high": "Your LDL cholesterol is elevated. Reducing it may help heart health. Talk to your doctor about diet and exercise.",
        "low": "Your LDL cholesterol is low, which is generally good for heart health.",
    },
    "HDL Cholesterol": {
        "what": "HDL is 'good cholesterol' that helps remove other forms of cholesterol from your bloodstream.",
        "normal": "Your HDL cholesterol is at a healthy level.",
        "high": "High HDL is generally good and may protect against heart disease.",
        "low": "Your HDL cholesterol is lower than ideal. Exercise and healthy fats may help increase it.",
    },
    "Triglycerides": {
        "what": "Triglycerides are a type of fat in your blood. High levels can increase heart disease risk.",
        "normal": "Your triglyceride level is normal.",
        "high": "Your triglycerides are elevated. Reducing sugar and alcohol intake may help. Consult your doctor.",
        "low": "Your triglyceride level is low, which is generally not a concern.",
    },
    "Hemoglobin A1c": {
        "what": "HbA1c shows your average blood sugar over the past 2-3 months.",
        "normal": "Your HbA1c is in the normal range, suggesting good blood sugar control.",
        "high": "Your HbA1c is elevated, which may indicate diabetes or prediabetes. Consult your doctor for evaluation.",
        "low": "Your HbA1c is lower than normal, which is uncommon. Discuss with your doctor.",
        "urgent": {"threshold": 9.0, "message": "⚠️ Very high HbA1c. Seek medical attention for diabetes management."}
    },
    "Creatinine": {
        "what": "Creatinine is a waste product filtered by your kidneys. It helps assess kidney function.",
        "normal": "Your creatinine level is normal, suggesting healthy kidney function.",
        "high": "Your creatinine is elevated, which may indicate reduced kidney function. Consult your doctor.",
        "low": "Your creatinine is lower than normal, which is usually not a concern.",
    },
    "Potassium": {
        "what": "Potassium is essential for heart and muscle function.",
        "normal": "Your potassium level is normal.",
        "high": "Your potassium is higher than normal. This needs medical attention as it can affect heart rhythm.",
        "low": "Your potassium is lower than normal. Low potassium can affect muscle and heart function.",
        "urgent": {"threshold_low": 2.5, "threshold_high": 6.0, "message": "⚠️ Abnormal potassium level. Seek urgent medical care."}
    },
}


def get_test_explanation(canonical_name: str, status: str, value: float = None) -> str:
    """Get explanation for a specific test"""
    test_data = TEST_EXPLANATIONS.get(canonical_name)
    
    if not test_data:
        # Generic explanation
        return f"{canonical_name}: {status.capitalize()} result."
    
    explanation = test_data.get("what", "")
    status_text = test_data.get(status, "")
    
    # Check for urgent conditions
    urgent_warning = ""
    if value is not None and "urgent" in test_data:
        urgent = test_data["urgent"]
        if "threshold_low" in urgent and value < urgent["threshold_low"]:
            urgent_warning = " " + urgent["message"]
        elif "threshold_high" in urgent and value > urgent["threshold_high"]:
            urgent_warning = " " + urgent["message"]
        elif "threshold" in urgent and value > urgent["threshold"]:
            urgent_warning = " " + urgent["message"]
    
    return f"{explanation} {status_text}{urgent_warning}"


def generate_summary(results: List[ParsedLabResult]) -> str:
    """Generate a summary of all results"""
    if not results:
        return "No lab results could be parsed from the document."
    
    # Count statuses
    counts = {"normal": 0, "high": 0, "low": 0, "unknown": 0}
    for result in results:
        counts[result.status] += 1
    
    summary = f"Your lab report contains {len(results)} test results.\n\n"
    summary += f"• {counts['normal']} result(s) are within normal range\n"
    
    if counts['high'] > 0:
        summary += f"• {counts['high']} result(s) are higher than normal\n"
    
    if counts['low'] > 0:
        summary += f"• {counts['low']} result(s) are lower than normal\n"
    
    if counts['unknown'] > 0:
        summary += f"• {counts['unknown']} result(s) could not be classified\n"
    
    # Add specific highlights
    abnormal_results = [r for r in results if r.status in ['high', 'low']]
    
    if abnormal_results:
        summary += "\n### Results Needing Attention:\n\n"
        for result in abnormal_results[:5]:  # Show top 5
            explanation = get_test_explanation(result.canonical_name, result.status, result.value_numeric)
            summary += f"**{result.canonical_name}**: {explanation}\n\n"
    
    return summary


def generate_general_tips() -> str:
    """Generate general health tips (non-medical)"""
    tips = """
### General Wellness Tips

These are general lifestyle suggestions, NOT medical recommendations for your specific results:

**Nutrition:**
- Eat a balanced diet with plenty of vegetables, fruits, whole grains, and lean proteins
- Limit processed foods, added sugars, and excessive salt
- Stay hydrated by drinking adequate water throughout the day

**Physical Activity:**
- Aim for regular physical activity (check with your doctor before starting a new exercise program)
- Include both aerobic exercise and strength training
- Even short walks can be beneficial

**Sleep:**
- Aim for 7-9 hours of quality sleep per night
- Maintain a consistent sleep schedule
- Create a relaxing bedtime routine

**Stress Management:**
- Practice stress-reduction techniques like deep breathing or meditation
- Make time for activities you enjoy
- Stay connected with friends and family

**Medical Follow-up:**
- Schedule regular check-ups with your healthcare provider
- Keep track of your lab results over time
- Ask questions and discuss any concerns with your doctor

⚠️ **Remember:** These are general tips only. Always follow your doctor's specific recommendations for your health situation.
"""
    return tips


def generate_explanation(results: List[ParsedLabResult], report_type: str) -> Dict[str, str]:
    """
    Generate complete explanation package
    
    Returns dict with keys: summary, tips, disclaimer
    """
    summary = generate_summary(results)
    tips = generate_general_tips()
    
    explanation = {
        "summary": summary,
        "tips": tips,
        "disclaimer": DISCLAIMER
    }
    
    return explanation


def check_critical_values(results: List[ParsedLabResult]) -> List[str]:
    """Check for any critical/urgent values that need immediate attention"""
    warnings = []
    
    for result in results:
        if result.value_numeric is None:
            continue
        
        canonical = result.canonical_name
        value = result.value_numeric
        
        # Define critical ranges
        critical_ranges = {
            "Glucose": (None, 300),
            "Hemoglobin": (7, None),
            "White Blood Cells": (2, 30),
            "Platelets": (50, None),
            "Potassium": (2.5, 6.0),
            "Sodium": (120, 160),
            "Creatinine": (None, 5.0),
        }
        
        if canonical in critical_ranges:
            low, high = critical_ranges[canonical]
            
            if low and value < low:
                warnings.append(f"⚠️ {canonical} is critically low ({value}). Seek medical attention.")
            elif high and value > high:
                warnings.append(f"⚠️ {canonical} is critically high ({value}). Seek medical attention.")
    
    return warnings
