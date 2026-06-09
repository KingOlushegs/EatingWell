import os
import json
import urllib.request
import urllib.error

# --- 1. ZERO-DEPENDENCY .ENV PARSER ---
if os.path.exists(".env"):
    with open(".env", "r") as f:
        for line in f:
            if line.strip() and not line.startswith("#"):
                key, value = line.strip().split("=", 1)
                os.environ[key.strip()] = value.strip().strip('"').strip("'")

# Ingest environment key
api_key_env = os.environ.get("GEMINI_API_KEY")
if not api_key_env:
    print("❌ ERROR: GEMINI_API_KEY not found in your .env file!")
    exit()

# Your target testing instance
test_prompt = "User: 42yo Executive, high cortisol, 5 hours sleep. Jet-lagged (EST to GMT). 4-hour back-to-back board meeting sequence starting in 30 minutes. Current fasting window: 14 hours."

print("🚀 Executing zero-dependency backend validation against Gemini Engine...")

# Using the native REST endpoint for gemini-2.5-flash
url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key_env}"

# Defining the exact schema configuration as a standard dictionary
payload = {
    "contents": [{
        "parts": [{
            "text": f"You are the vision, text ingestion, and strategic health optimization engine for an autonomous nutrition platform. Analyze the input context, map or extract food items, calculate precise macro arrays, and formulate high-performance strategic decisions.\n\nInput Context: {test_prompt}"
        }]
    }],
    "generationConfig": {
        "responseMimeType": "application/json",
        "responseSchema": {
            "type": "OBJECT",
            "properties": {
                "meal_name": {"type": "STRING"},
                "confidence_score": {"type": "NUMBER"},
                "total_calories": {"type": "INTEGER"},
                "ingredients": {
                    "type": "ARRAY",
                    "items": {
                        "type": "OBJECT",
                        "properties": {
                            "name": {"type": "STRING"},
                            "estimated_weight_g": {"type": "NUMBER"},
                            "protein_g": {"type": "NUMBER"},
                            "carbs_g": {"type": "NUMBER"},
                            "fats_g": {"type": "NUMBER"},
                            "calories": {"type": "INTEGER"}
                        },
                        "required": ["name", "estimated_weight_g", "protein_g", "carbs_g", "fats_g", "calories"]
                    }
                },
                "strategic_layer": {
                    "type": "OBJECT",
                    "properties": {
                        "metabolic_impact_the_now": {"type": "STRING"},
                        "downstream_compensation_the_next": {"type": "STRING"}
                    },
                    "required": ["metabolic_impact_the_now", "downstream_compensation_the_next"]
                }
            },
            "required": ["meal_name", "confidence_score", "total_calories", "ingredients", "strategic_layer"]
        },
        "temperature": 0.1
    }
}

# Sending the raw web request directly to Google's cloud
headers = {"Content-Type": "application/json"}
req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers)

try:
    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read().decode("utf-8"))
        
        # Extract the raw text string containing our structured JSON from the API wrapper
        structured_output = result['candidates'][0]['content']['parts'][0]['text']
        
        print("\n✅ CORE API PIPELINE & STRATEGIC LAYER FUNCTIONAL!")
        print("--- RESPONSE STRUCT ---")
        print(structured_output)

except urllib.error.HTTPError as e:
    print(f"\n❌ API Error (HTTP {e.code}): {e.read().decode('utf-8')}")
except Exception as e:
    print(f"\n❌ Script Error: {e}")