import google.generativeai as genai
import os

# Use the same key as in your secrets.json
genai.configure(api_key="AIzaSyALPr7boitFVKIEn7Xzl3No8tQ5w1e1YJo")

print("Listing available models:")
for m in genai.list_models():
    if "generateContent" in m.supported_generation_methods:
        print(m.name)