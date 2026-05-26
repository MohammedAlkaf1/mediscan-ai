import os
import sys
from dotenv import load_dotenv
load_dotenv()

import google.generativeai as genai

# Configure API
api_key = os.getenv("GEMINI_API_KEY")
model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

print(f"Testing Gemini API: {model_name}")
print(f"API Key: {api_key[:20]}...")

genai.configure(api_key=api_key)
model = genai.GenerativeModel(model_name)

# Simple test prompt
prompt = """Please write a detailed explanation (at least 500 words) about the importance of regular health checkups. Include multiple paragraphs covering different aspects."""

from google.generativeai.types import HarmCategory, HarmBlockThreshold

safety_settings = {
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
}

gen_config = {
    "temperature": 0.7,
    "max_output_tokens": 8000,
    "top_p": 0.95,
    "top_k": 40,
}

print(f"\nGeneration config: {gen_config}")
print("\nGenerating response...")

response = model.generate_content(
    prompt,
    generation_config=gen_config,
    safety_settings=safety_settings
)

print(f"\nFinish reason: {response.candidates[0].finish_reason}")
print(f"Safety ratings: {response.candidates[0].safety_ratings}")
print(f"\nResponse length: {len(response.text)} characters")
print(f"\nFirst 200 chars: {response.text[:200]}")
print(f"\nLast 200 chars: {response.text[-200:]}")
print(f"\n=== FULL RESPONSE ===")
print(response.text)
