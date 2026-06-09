import os
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from typing import List, Optional

# --- 1. ZERO-DEPENDENCY .ENV PARSER ---
# Manually reading the .env file as text to bypass python-dotenv entirely
if os.path.exists(".env"):
    with open(".env", "r") as f:
        for line in f:
            if line.strip() and not line.startswith("#"):
                key, value = line.strip().split("=", 1)
                os.environ[key.strip()] = value.strip().strip('"').strip("'")

# --- 2. MATCH YOUR EXACT PYDANTIC SCHEMA ---
class Ingredient(BaseModel):
    name: str
    estimated_weight_g: float
    protein_g: float
    carbs_g: float
    fats_g: float
    calories: int

class MealAnalysis(BaseModel):
    meal_name: str
    confidence_score: float
    ingredients: List[Ingredient]
    total_calories: int

# Ingest environment key
api_key_env = os.environ.get("GEMINI_API_KEY")
if not api_key_env:
    print("❌ ERROR: GEMINI_API_KEY not found in your .env file!")
    exit()

client = genai.Client(api_key=api_key_env)

# Your target testing instance
test_prompt = "User: 42yo Executive, high cortisol, 5 hours sleep. Jet-lagged (EST to GMT). 4-hour back-to-back board meeting sequence starting in 30 minutes. Current fasting window: 14 hours."

print("🚀 Executing local backend validation against Gemini Engine...")

try:
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=[
            "You are the vision and text ingestion engine for an autonomous nutrition app. Analyze the input, extract food items, and calculate macro metrics.",
            test_prompt
        ],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=MealAnalysis,
            temperature=0.1,
        ),
    )
    print("\n✅ CORE API PIPELINE FUNCTIONAL!")
    print("--- RESPONSE STRUCT ---")
    print(response.text)

except Exception as e:
    print(f"\n❌ API Error: {e}")