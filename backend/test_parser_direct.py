"""Test the table parser directly"""
import sys
sys.path.insert(0, '.')

# Sample extracted text
text = """GNU Solidario Hospital
Autovla Gel Norte 12485
Lus Fulmnas ue Gran Cunrij
LABORATORY REPORT
Name
Betz
Pallent ID FACOO1
Djle
2011-08-25 08.32
Age
25y 10m 260
Sex
Fema le
Dcctor
Cameron Comjrj
Test Iu B165AAF4
COMPLETE BLOOD
COUNT
Test Name
Result
Normal Range
Hemoglobin
11.0
16.0
9/uL
RBC
3.5-5.5 0
10^6/uL
HCT
37.0-50.
MCV
82-95
MCH
27-31
MCHC
32.0-36.0
glaL
RDW-CV
11.5-14.5
RDW-SD
35-56
WBC
4.5-11
10^Jul
NEUS
40-70
LYMY
20-45
MONYS
2-10
EOS
BAS%S
LYM#
1.5-4_
10^Jul
GRA#
2.0-7.5
10^Jul
PLT
256
150-450
10^Vul
ESR
Up to 15
mm/hr"""

from parser_service import parse_lab_results, parse_table_format

print("=== TESTING TABLE PARSER ===\n")
lines = text.split('\n')
print(f"Total lines: {len(lines)}\n")

# Test table parser directly
print("Testing parse_table_format()...")
table_results = parse_table_format(lines)
print(f"Table results: {len(table_results)}\n")

for r in table_results[:10]:
    print(f"{r.test_name}: {r.value_text} {r.unit} (ref: {r.ref_low}-{r.ref_high}) [{r.status}]")

print(f"\n=== TESTING FULL PARSER ===")
all_results = parse_lab_results(text)
print(f"Total results: {len(all_results)}\n")

for r in all_results[:10]:
    print(f"{r.test_name}: {r.value_text} {r.unit} [{r.status}]")
