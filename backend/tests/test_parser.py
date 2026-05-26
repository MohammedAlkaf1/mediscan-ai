"""
Unit tests for the parser service
"""
import pytest
from parser_service import (
    parse_lab_line,
    parse_lab_results,
    detect_report_type,
    get_canonical_name,
    parse_value_and_unit,
    parse_reference_range,
    classify_status
)


class TestParserService:
    
    def test_parse_value_and_unit(self):
        """Test parsing values and units"""
        # Test normal value with unit
        value, unit = parse_value_and_unit("110 mg/dL")
        assert value == 110.0
        assert unit == "mg/dL"
        
        # Test value with space
        value, unit = parse_value_and_unit("7.2 x10^3/uL")
        assert value == 7.2
        assert unit == "x10^3/uL"
        
        # Test value without unit
        value, unit = parse_value_and_unit("42.5")
        assert value == 42.5
        assert unit is None
    
    def test_parse_reference_range(self):
        """Test parsing reference ranges"""
        # Test normal range
        low, high = parse_reference_range("70-99")
        assert low == 70.0
        assert high == 99.0
        
        # Test decimal range
        low, high = parse_reference_range("4.0-11.0")
        assert low == 4.0
        assert high == 11.0
        
        # Test less than
        low, high = parse_reference_range("<5.7")
        assert low is None
        assert high == 5.7
        
        # Test greater than
        low, high = parse_reference_range(">40")
        assert low == 40.0
        assert high is None
    
    def test_classify_status(self):
        """Test status classification"""
        # Test normal
        assert classify_status(85, 70, 99) == "normal"
        
        # Test high
        assert classify_status(120, 70, 99) == "high"
        
        # Test low
        assert classify_status(50, 70, 99) == "low"
        
        # Test unknown (no ranges)
        assert classify_status(100, None, None) == "unknown"
    
    def test_get_canonical_name(self):
        """Test canonical name mapping"""
        assert get_canonical_name("WBC") == "White Blood Cells"
        assert get_canonical_name("hgb") == "Hemoglobin"
        assert get_canonical_name("Glucose") == "Glucose"
        assert get_canonical_name("Unknown Test") == "Unknown Test"
    
    def test_parse_lab_line_simple(self):
        """Test parsing simple lab result line"""
        line = "Glucose 110 mg/dL 70-99"
        result = parse_lab_line(line)
        
        assert result is not None
        assert result.test_name == "Glucose"
        assert result.canonical_name == "Glucose"
        assert result.value_numeric == 110.0
        assert result.unit == "mg/dL"
        assert result.ref_low == 70.0
        assert result.ref_high == 99.0
        assert result.status == "high"
    
    def test_parse_lab_line_with_parentheses(self):
        """Test parsing lab result with parentheses"""
        line = "WBC 6.2 x10^3/uL (4.0 - 11.0)"
        result = parse_lab_line(line)
        
        assert result is not None
        assert result.test_name == "WBC"
        assert result.canonical_name == "White Blood Cells"
        assert result.value_numeric == 6.2
        assert result.status == "normal"
    
    def test_parse_lab_line_with_colon(self):
        """Test parsing lab result with colon"""
        line = "Hemoglobin: 13.5 g/dL [12.0-16.0]"
        result = parse_lab_line(line)
        
        assert result is not None
        assert result.canonical_name == "Hemoglobin"
        assert result.value_numeric == 13.5
        assert result.status == "normal"
    
    def test_parse_lab_results_full_text(self):
        """Test parsing full report text"""
        text = """
        LABORATORY REPORT
        
        Complete Blood Count
        
        White Blood Cells: 7.2 x10^3/uL (4.0-11.0)
        Red Blood Cells: 4.8 x10^6/uL (4.2-5.9)
        Hemoglobin: 14.2 g/dL (12.0-16.0)
        Platelets: 245 x10^3/uL (150-400)
        
        Glucose: 110 mg/dL (70-99)
        """
        
        results = parse_lab_results(text)
        
        assert len(results) >= 4  # Should parse at least 4 valid results
        test_names = [r.canonical_name for r in results]
        assert "White Blood Cells" in test_names
        assert "Hemoglobin" in test_names
        assert "Glucose" in test_names
    
    def test_detect_report_type_cbc(self):
        """Test report type detection for CBC"""
        text = """
        WBC: 7.2 x10^3/uL (4.0-11.0)
        RBC: 4.8 x10^6/uL (4.2-5.9)
        Hemoglobin: 14.2 g/dL (12.0-16.0)
        Hematocrit: 42% (36-48)
        Platelets: 245 x10^3/uL (150-400)
        """
        
        results = parse_lab_results(text)
        report_type = detect_report_type(results)
        
        assert "CBC" in report_type or "Blood Count" in report_type
    
    def test_detect_report_type_lipid(self):
        """Test report type detection for Lipid Panel"""
        text = """
        Total Cholesterol: 195 mg/dL (<200)
        LDL Cholesterol: 115 mg/dL (<100)
        HDL Cholesterol: 52 mg/dL (>40)
        Triglycerides: 140 mg/dL (<150)
        """
        
        results = parse_lab_results(text)
        report_type = detect_report_type(results)
        
        assert "Lipid" in report_type


def test_readme_sample_1():
    """Test sample from fixture 1 - CBC Report"""
    with open("tests/fixtures/sample_cbc.txt", "r") as f:
        text = f.read()
    
    results = parse_lab_results(text)
    assert len(results) > 0
    
    # Check for expected tests
    canonical_names = [r.canonical_name for r in results]
    assert any("White Blood" in name or "WBC" in name for name in canonical_names)


def test_readme_sample_2():
    """Test sample from fixture 2 - Lipid Panel"""
    with open("tests/fixtures/sample_lipid.txt", "r") as f:
        text = f.read()
    
    results = parse_lab_results(text)
    assert len(results) > 0
    
    # Check for lipid markers
    canonical_names = [r.canonical_name for r in results]
    assert any("Cholesterol" in name for name in canonical_names)


def test_readme_sample_3():
    """Test sample from fixture 3 - Metabolic Panel"""
    with open("tests/fixtures/sample_metabolic.txt", "r") as f:
        text = f.read()
    
    results = parse_lab_results(text)
    assert len(results) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
