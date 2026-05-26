"""
Test OCR functionality with diagnostic information
"""
import os
import sys

print("=== OCR Diagnostic Test ===\n")

# Test 1: Check if PaddleOCR can be imported
print("1. Testing PaddleOCR import...")
try:
    from paddleocr import PaddleOCR
    print("   ✅ PaddleOCR imported successfully")
except Exception as e:
    print(f"   ❌ PaddleOCR import failed: {e}")
    sys.exit(1)

# Test 2: Check if OpenCV works
print("\n2. Testing OpenCV...")
try:
    import cv2
    print(f"   ✅ OpenCV version: {cv2.__version__}")
except Exception as e:
    print(f"   ❌ OpenCV failed: {e}")

# Test 3: Check if PIL/Pillow works
print("\n3. Testing PIL/Pillow...")
try:
    from PIL import Image
    print(f"   ✅ PIL version: {Image.__version__}")
except Exception as e:
    print(f"   ❌ PIL failed: {e}")

# Test 4: Check if pdfplumber works
print("\n4. Testing pdfplumber...")
try:
    import pdfplumber
    print(f"   ✅ pdfplumber imported successfully")
except Exception as e:
    print(f"   ❌ pdfplumber failed: {e}")

# Test 5: Check if pdf2image works
print("\n5. Testing pdf2image...")
try:
    from pdf2image import convert_from_path
    print("   ✅ pdf2image imported successfully")
    print("   ⚠️  Note: Requires poppler-utils to be installed")
except Exception as e:
    print(f"   ❌ pdf2image failed: {e}")

# Test 6: Initialize PaddleOCR
print("\n6. Initializing PaddleOCR...")
try:
    ocr = PaddleOCR(use_angle_cls=True, lang='en', show_log=False)
    print("   ✅ PaddleOCR initialized successfully")
    
    # Test 7: Try OCR on a simple test
    print("\n7. Testing OCR on sample text...")
    import numpy as np
    
    # Create a simple test image with text
    test_img = np.ones((100, 400, 3), dtype=np.uint8) * 255
    cv2.putText(test_img, "TEST", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
    
    result = ocr.ocr(test_img, cls=True)
    if result and result[0]:
        extracted_text = " ".join([line[1][0] for line in result[0]])
        print(f"   ✅ OCR test successful! Extracted: '{extracted_text}'")
    else:
        print("   ⚠️  OCR returned empty result")
        
except Exception as e:
    print(f"   ❌ PaddleOCR test failed: {e}")
    import traceback
    traceback.print_exc()

# Test 8: Check uploads directory
print("\n8. Checking uploads directory...")
uploads_dir = "./uploads"
if os.path.exists(uploads_dir):
    files = os.listdir(uploads_dir)
    print(f"   ✅ Uploads directory exists with {len(files)} files")
    if files:
        print(f"   Files: {files[:5]}")  # Show first 5
else:
    print(f"   ❌ Uploads directory not found")

print("\n=== Diagnostic Complete ===")
