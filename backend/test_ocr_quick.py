"""
Quick diagnostic test to verify OCR is working
"""
import sys
sys.path.insert(0, r'c:\xampp\htdocs\medical\backend')

from ocr_service import get_ocr_engine
import logging

logging.basicConfig(level=logging.INFO)

print("=" * 50)
print("OCR DIAGNOSTIC TEST")
print("=" * 50)
print()

try:
    print("1. Testing PaddleOCR import...")
    from paddleocr import PaddleOCR
    print("   ✓ PaddleOCR imported successfully")
    print()
    
    print("2. Initializing OCR engine...")
    ocr = get_ocr_engine()
    print("   ✓ OCR engine initialized")
    print(f"   Engine type: {type(ocr)}")
    print()
    
    print("3. OCR is ready to extract text from files!")
    print()
    print("=" * 50)
    print("RESULT: OCR SERVICE IS WORKING ✓")
    print("=" * 50)
    
except ImportError as e:
    print(f"   ✗ Import Error: {e}")
    print()
    print("=" * 50)
    print("RESULT: PADDLEOCR NOT INSTALLED ✗")
    print("=" * 50)
    print()
    print("Fix: Run this command:")
    print("  py -m pip install paddleocr paddlepaddle")
    
except Exception as e:
    print(f"   ✗ Error: {e}")
    print()
    print("=" * 50)
    print("RESULT: OCR INITIALIZATION FAILED ✗")
    print("=" * 50)

input("\nPress Enter to exit...")
