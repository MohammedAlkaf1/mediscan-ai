"""Quick test to verify EasyOCR works on uploaded image"""
import easyocr
import sys

print('Initializing EasyOCR...')
reader = easyocr.Reader(['en'], gpu=False)
print('Running OCR on uploaded image...')
result = reader.readtext('uploads/5f25b803-d3a1-4296-a51c-9dbb5d738736.png')
print(f'Lines found: {len(result)}')
for i, (bbox, text, conf) in enumerate(result[:10]):
    print(f'  Line {i}: "{text}" (conf: {conf:.2f})')
total_text = '\n'.join([item[1] for item in result])
print(f'\nTotal chars extracted: {len(total_text)}')
print(f'First 500 chars:\n{total_text[:500]}')
