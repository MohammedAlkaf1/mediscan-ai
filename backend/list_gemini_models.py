"""List available Gemini models"""
import google.generativeai as genai
import warnings
warnings.filterwarnings('ignore')

genai.configure(api_key='AIzaSyCA54bPynTZMivnNns0qj26OTRGqE7tvZM')

print("Available Gemini Models:")
print("=" * 60)

try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"✓ {m.name}")
            print(f"  Display Name: {m.display_name}")
            print(f"  Description: {m.description[:80]}...")
            print()
except Exception as e:
    print(f"Error: {e}")
