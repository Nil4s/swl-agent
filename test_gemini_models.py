#!/usr/bin/env python3
import os
import google.generativeai as genai

api_key = os.getenv('GEMINI_API_KEY', 'AIzaSyC7EILy4A6tGxjmDFSRLCJj5LKHYzKvQkI')
genai.configure(api_key=api_key)

print("Available Gemini models that support generateContent:")
print("=" * 60)

for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        print(f"  - {model.name}")
        
print("=" * 60)
print("\nTrying to use first available model...")

models = [m for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
if models:
    model_name = models[0].name
    print(f"Using: {model_name}")
    
    model = genai.GenerativeModel(model_name)
    response = model.generate_content("Say 'test' in one word")
    print(f"Response: {response.text}")
    print("\n✅ Gemini API works!")
else:
    print("❌ No models available!")
