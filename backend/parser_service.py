"""
Parser Service for extracting structured lab results from OCR text
"""
import re
import logging
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ParsedLabResult:
    test_name: str
    canonical_name: str
    value_numeric: Optional[float]
    value_text: str
    unit: Optional[str]
    ref_low: Optional[float]
    ref_high: Optional[float]
    ref_text: Optional[str]
    status: str  # normal, high, low, unknown


# Canonical name mappings
CANONICAL_NAMES = {
    # CBC Tests
    "wbc": "White Blood Cells",
    "white blood cells": "White Blood Cells",
    "white blood cell": "White Blood Cells",
    "rbc": "Red Blood Cells",
    "red blood cells": "Red Blood Cells",
    "red blood cell": "Red Blood Cells",
    "hgb": "Hemoglobin",
    "hemoglobin": "Hemoglobin",
    "hb": "Hemoglobin",
    "hct": "Hematocrit",
    "hematocrit": "Hematocrit",
    "plt": "Platelets",
    "platelet": "Platelets",
    "platelets": "Platelets",
    "mcv": "Mean Corpuscular Volume",
    "mch": "Mean Corpuscular Hemoglobin",
    "mchc": "Mean Corpuscular Hemoglobin Concentration",
    "neutrophils": "Neutrophils",
    "lymphocytes": "Lymphocytes",
    "monocytes": "Monocytes",
    "eosinophils": "Eosinophils",
    "basophils": "Basophils",
    
    # Lipid Panel
    "cholesterol": "Total Cholesterol",
    "total cholesterol": "Total Cholesterol",
    "ldl": "LDL Cholesterol",
    "ldl cholesterol": "LDL Cholesterol",
    "hdl": "HDL Cholesterol",
    "hdl cholesterol": "HDL Cholesterol",
    "triglycerides": "Triglycerides",
    "vldl": "VLDL Cholesterol",
    
    # Metabolic
    "glucose": "Glucose",
    "blood sugar": "Glucose",
    "hba1c": "Hemoglobin A1c",
    "hemoglobin a1c": "Hemoglobin A1c",
    "a1c": "Hemoglobin A1c",
    
    # Kidney Function
    "creatinine": "Creatinine",
    "bun": "Blood Urea Nitrogen",
    "blood urea nitrogen": "Blood Urea Nitrogen",
    "egfr": "eGFR",
    
    # Liver Function
    "alt": "ALT",
    "alanine aminotransferase": "ALT",
    "sgpt": "ALT",
    "ast": "AST",
    "aspartate aminotransferase": "AST",
    "sgot": "AST",
    "alp": "Alkaline Phosphatase",
    "alkaline phosphatase": "Alkaline Phosphatase",
    "bilirubin": "Bilirubin",
    "total bilirubin": "Total Bilirubin",
    
    # Electrolytes
    "sodium": "Sodium",
    "potassium": "Potassium",
    "chloride": "Chloride",
    "calcium": "Calcium",
    "magnesium": "Magnesium",
}


def get_canonical_name(test_name: str) -> str:
    """Get canonical name for a test"""
    test_lower = test_name.lower().strip()
    return CANONICAL_NAMES.get(test_lower, test_name)


def parse_value_and_unit(value_str: str) -> Tuple[Optional[float], Optional[str]]:
    """
    Parse a value string like "110 mg/dL" into numeric value and unit
    """
    # Remove extra whitespace
    value_str = value_str.strip()
    
    # Try to extract number
    number_match = re.search(r'([\d.,]+)', value_str)
    if not number_match:
        return None, None
    
    value_text = number_match.group(1).replace(',', '')
    
    try:
        value_numeric = float(value_text)
    except ValueError:
        value_numeric = None
    
    # Extract unit (everything after the number)
    unit_match = re.search(r'[\d.,]+\s*([^\d\s]+)', value_str)
    unit = unit_match.group(1).strip() if unit_match else None
    
    return value_numeric, unit


def parse_reference_range(ref_str: str) -> Tuple[Optional[float], Optional[float]]:
    """
    Parse reference range like "70-99", "4.0-11.0", "<5.7", ">100"
    """
    ref_str = ref_str.strip()
    
    # Pattern: low-high
    range_match = re.search(r'([\d.]+)\s*-\s*([\d.]+)', ref_str)
    if range_match:
        try:
            ref_low = float(range_match.group(1))
            ref_high = float(range_match.group(2))
            return ref_low, ref_high
        except ValueError:
            pass
    
    # Pattern: < value
    less_match = re.search(r'<\s*([\d.]+)', ref_str)
    if less_match:
        try:
            return None, float(less_match.group(1))
        except ValueError:
            pass
    
    # Pattern: > value
    greater_match = re.search(r'>\s*([\d.]+)', ref_str)
    if greater_match:
        try:
            return float(greater_match.group(1)), None
        except ValueError:
            pass
    
    return None, None


def classify_status(value_numeric: Optional[float], ref_low: Optional[float], ref_high: Optional[float]) -> str:
    """Classify result as normal, high, low, or unknown"""
    if value_numeric is None:
        return "unknown"
    
    if ref_low is not None and value_numeric < ref_low:
        return "low"
    
    if ref_high is not None and value_numeric > ref_high:
        return "high"
    
    if ref_low is not None or ref_high is not None:
        return "normal"
    
    return "unknown"


def _normalize_line(line: str) -> str:
    """Strip common abbreviations like '(WBC)' from test names and unwrap (<200) refs."""
    # Remove short uppercase abbreviations in parens: "White Blood Cells (WBC)" → "White Blood Cells"
    line = re.sub(r'\s*\([A-Z]{2,6}\)\s*', ' ', line).strip()
    # Unwrap (<200) → <200 and (>40) → >40 so patterns can match them
    line = re.sub(r'\(\s*([<>][^)]+)\)', r'\1', line)
    return line


def parse_lab_line(line: str) -> Optional[ParsedLabResult]:
    """
    Parse a single line of lab results

    Example formats:
    - "Glucose 110 mg/dL 70-99"
    - "WBC 6.2 x10^3/uL (4.0 - 11.0)"
    - "HbA1c 5.7 % 4.0-5.6"
    - "Hemoglobin: 13.5 g/dL [12.0-16.0]"
    - "White Blood Cells (WBC): 7.2 x10^3/uL (4.0-11.0)"
    - "Total Cholesterol: 215 mg/dL (<200)"
    """
    line = line.strip()

    if not line or len(line) < 5:
        return None

    line = _normalize_line(line)

    # Common patterns
    patterns = [
        # Pattern 1: TestName Value Unit RefLow-RefHigh
        r'^([A-Za-z][A-Za-z0-9\s\-/]+?)\s+([\d.,]+)\s*([A-Za-z/%^0-9]+)?\s+[\(\[]?([\d.]+)\s*-\s*([\d.]+)[\)\]]?',

        # Pattern 2: TestName: Value Unit [RefLow-RefHigh]
        r'^([A-Za-z][A-Za-z0-9\s\-/]+?):\s*([\d.,]+)\s*([A-Za-z/%^0-9]+)?\s*[\[\(]?([\d.]+)\s*-\s*([\d.]+)[\]\)]?',

        # Pattern 3: TestName Value (RefLow - RefHigh) Unit
        r'^([A-Za-z][A-Za-z0-9\s\-/]+?)\s+([\d.,]+)\s*[\(\[]?([\d.]+)\s*-\s*([\d.]+)[\)\]]?\s*([A-Za-z/%^0-9]+)?',

        # Pattern 4: TestName Value Unit <RefHigh or >RefLow
        r'^([A-Za-z][A-Za-z0-9\s\-/]+?)\s+([\d.,]+)\s*([A-Za-z/%^0-9]+)?\s*([<>]\s*[\d.]+)',

        # Pattern 5: TestName: Value Unit <RefHigh or >RefLow (colon variant)
        r'^([A-Za-z][A-Za-z0-9\s\-/]+?):\s*([\d.,]+)\s*([A-Za-z/%^0-9]+)?\s*([<>]\s*[\d.]+)',
    ]
    
    for pattern in patterns:
        match = re.match(pattern, line, re.IGNORECASE)
        if match:
            try:
                groups = match.groups()
                test_name = groups[0].strip()
                
                # Skip if test name is too short or generic
                if len(test_name) < 2 or test_name.lower() in ['test', 'name', 'value', 'result']:
                    continue
                
                # Parse value
                value_text = groups[1] if len(groups) > 1 else ""
                try:
                    value_numeric = float(value_text.replace(',', ''))
                except (ValueError, AttributeError):
                    value_numeric = None
                
                # Parse unit
                unit = None
                ref_low = None
                ref_high = None
                ref_text = None
                
                if len(groups) > 2 and groups[2]:
                    unit = groups[2].strip()
                
                # Parse reference range
                if len(groups) > 4:
                    try:
                        if groups[3]:
                            ref_low = float(groups[3])
                        if groups[4]:
                            ref_high = float(groups[4])
                        ref_text = f"{groups[3]}-{groups[4]}"
                    except (ValueError, TypeError, IndexError):
                        pass
                
                # If ref range includes <> symbol
                if len(groups) > 3 and ('<' in str(groups[-1]) or '>' in str(groups[-1])):
                    ref_text = groups[-1]
                    ref_low, ref_high = parse_reference_range(groups[-1])
                
                # Classify status
                status = classify_status(value_numeric, ref_low, ref_high)
                
                # Get canonical name
                canonical_name = get_canonical_name(test_name)
                
                return ParsedLabResult(
                    test_name=test_name,
                    canonical_name=canonical_name,
                    value_numeric=value_numeric,
                    value_text=value_text,
                    unit=unit,
                    ref_low=ref_low,
                    ref_high=ref_high,
                    ref_text=ref_text,
                    status=status
                )
            except Exception as e:
                logger.debug(f"Failed to parse line '{line}': {e}")
                continue
    
    return None


def parse_table_format(lines: List[str]) -> List[ParsedLabResult]:
    """
    Parse table-format lab results where test names and values are on separate lines
    
    Format example:
    Test Name
    Result
    Normal Range
    Hemoglobin
    11.0
    12.0-16.0
    g/dL
    """
    results = []
    i = 0
    
    # Look for table header indicators
    header_found = False
    for j, line in enumerate(lines):
        if any(keyword in line.lower() for keyword in ['test name', 'result', 'normal range', 'reference']):
            header_found = True
            i = j + 1
            break
    
    if not header_found:
        return results
    
    # Process lines after header
    while i < len(lines):
        line = lines[i].strip()
        
        # Skip empty lines
        if not line or len(line) < 2:
            i += 1
            continue
        
        # Check if this looks like a test name (alphabetic, not just a number)
        if re.match(r'^[A-Za-z][A-Za-z0-9\-\s%#]*$', line):
            test_name = line
            
            # Try to get value from next line(s)
            value_numeric = None
            value_text = ""
            unit = None
            ref_low = None
            ref_high = None
            ref_text = None
            
            # Look ahead for numeric value
            for j in range(i + 1, min(i + 5, len(lines))):
                next_line = lines[j].strip()
                
                # Try to parse as numeric value
                value_match = re.search(r'([\d.]+)', next_line)
                if value_match and value_numeric is None:
                    try:
                        value_numeric = float(value_match.group(1))
                        value_text = value_match.group(1)
                        
                        # Check if unit is in same line
                        unit_match = re.search(r'[\d.]+\s*([A-Za-z/%^0-9]+)', next_line)
                        if unit_match:
                            unit = unit_match.group(1)
                    except ValueError:
                        pass
                
                # Try to parse as reference range
                ref_match = re.search(r'([\d.]+)\s*-\s*([\d.]+)', next_line)
                if ref_match and ref_low is None:
                    try:
                        ref_low = float(ref_match.group(1))
                        ref_high = float(ref_match.group(2))
                        ref_text = next_line
                    except ValueError:
                        pass
                
                # If we have both value and reference, we're done with this test
                if value_numeric is not None and ref_low is not None:
                    break
            
            # Create result if we found a value
            if value_numeric is not None:
                status = classify_status(value_numeric, ref_low, ref_high)
                canonical_name = get_canonical_name(test_name)
                
                result = ParsedLabResult(
                    test_name=test_name,
                    canonical_name=canonical_name,
                    value_numeric=value_numeric,
                    value_text=value_text,
                    unit=unit,
                    ref_low=ref_low,
                    ref_high=ref_high,
                    ref_text=ref_text,
                    status=status
                )
                results.append(result)
                logger.debug(f"Table parsed: {test_name} = {value_text} {unit} ({status})")
        
        i += 1
    
    return results


def parse_lab_results(text: str) -> List[ParsedLabResult]:
    """
    Parse full OCR text into structured lab results
    """
    results = []
    
    lines = text.split('\n')
    
    # First try table format parser
    table_results = parse_table_format(lines)
    if table_results:
        results.extend(table_results)
        logger.info(f"Parsed {len(table_results)} lab results from table format")
    
    # Then try single-line parser for any remaining data
    for line in lines:
        parsed = parse_lab_line(line)
        if parsed:
            # Check if not already in results
            if not any(r.test_name == parsed.test_name for r in results):
                results.append(parsed)
                logger.debug(f"Line parsed: {parsed.test_name} = {parsed.value_text} {parsed.unit} ({parsed.status})")
    
    logger.info(f"Total parsed: {len(results)} lab results from text")
    return results


def detect_report_type(results: List[ParsedLabResult]) -> str:
    """
    Detect the type of medical report based on tests present
    """
    canonical_names = {r.canonical_name.lower() for r in results}
    
    # CBC markers
    cbc_markers = {'white blood cells', 'red blood cells', 'hemoglobin', 'hematocrit', 'platelets'}
    if len(canonical_names.intersection(cbc_markers)) >= 3:
        return "Complete Blood Count (CBC)"
    
    # Lipid panel markers
    lipid_markers = {'total cholesterol', 'ldl cholesterol', 'hdl cholesterol', 'triglycerides'}
    if len(canonical_names.intersection(lipid_markers)) >= 2:
        return "Lipid Panel"
    
    # Diabetes markers
    diabetes_markers = {'glucose', 'hemoglobin a1c'}
    if canonical_names.intersection(diabetes_markers):
        return "Diabetes Screening"
    
    # Liver function markers
    liver_markers = {'alt', 'ast', 'alkaline phosphatase', 'bilirubin', 'total bilirubin'}
    if len(canonical_names.intersection(liver_markers)) >= 2:
        return "Liver Function Test"
    
    # Kidney function markers
    kidney_markers = {'creatinine', 'blood urea nitrogen', 'egfr'}
    if len(canonical_names.intersection(kidney_markers)) >= 2:
        return "Kidney Function Test"
    
    return "General Lab Report"
