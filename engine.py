import os
from dotenv import load_dotenv  # Add this line
load_dotenv()                   # Add this line too
import streamlit as st
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from typing import List, Optional
from PIL import Image
import tempfile

# -------------------------------------------------------------------
# 1. DATA STRUCURES & PYDANTIC STRUCTURAL SCHEMAS
# -------------------------------------------------------------------
class Ingredient(BaseModel):
    name: str = Field(description="The name of the food item.")
    estimated_weight_g: float = Field(description="Estimated weight in grams.")
    protein_g: float = Field(description="Grams of protein.")
    carbs_g: float = Field(description="Grams of carbohydrates.")
    fats_g: float = Field(description="Grams of fats.")
    calories: int = Field(description="Total calories.")

class MealAnalysis(BaseModel):
    meal_name: str = Field(description="Clean title for the meal.")
    confidence_score: float = Field(description="Confidence rating 0.0 to 1.0.")
    ingredients: List[Ingredient]
    total_calories: int = Field(description="Sum of all calories.")

# -------------------------------------------------------------------
# 2. CORE BACKEND INGESTION ENGINES (GEMINI & FALLBACK)
# -------------------------------------------------------------------
# Securely extract the key from the system environment variables
api_key_env = os.environ.get("GEMINI_API_KEY")

# Initialize the client securely if key exists, otherwise let UI handle error gracefully
client = genai.Client(api_key=api_key_env) if api_key_env else None

def autonomous_logger(raw_input: str, image_file=None) -> MealAnalysis:
    """Parses text and stream imagery into structured nutritional data."""
    if not client:
        # If API Key environment variable is missing, fall back immediately to local database
        return local_heuristic_fallback(raw_input or "Uploaded Image Track")

    base_prompt = (
        "You are the vision and text ingestion engine for an autonomous nutrition app. "
        "Analyze the provided input (text description, image, or both), extract all food items, "
        "estimate their weights in grams, and calculate their precise macronutrient breakdown."
    )
    
    contents = [base_prompt]
    
    if raw_input:
        contents.append(f"User Text Description: {raw_input}")
        
    if image_file:
        try:
            img = Image.open(image_file)
            contents.append(img)
        except Exception as e:
            st.sidebar.error(f"⚠️ Image parsing failure: {e}")

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=contents,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=MealAnalysis,
                temperature=0.1,
            ),
        )
        return MealAnalysis.model_validate_json(response.text)
    except Exception as network_error:
        # If network error or token limit hit, safety bridge to local offline DB
        return local_heuristic_fallback(raw_input or "Image Scan Fallback")

def local_heuristic_fallback(raw_input: str) -> MealAnalysis:
    """An internet-free backup parser that estimates macros if the Gemini API is unreachable."""
    text = raw_input.lower()
    detected_ingredients = []
    
    local_db = {
        "chicken": {"name": "Grilled Chicken Breast", "weight": 150, "p": 46, "c": 0, "f": 4, "cal": 220},
        "salmon": {"name": "Atlantic Salmon", "weight": 150, "p": 34, "c": 0, "f": 18, "cal": 300},
        "steak": {"name": "Sirloin Steak", "weight": 200, "p": 52, "c": 0, "f": 14, "cal": 340},
        "egg": {"name": "Whole Eggs", "weight": 150, "p": 18, "c": 1, "f": 15, "cal": 210},
        "rice": {"name": "Brown Rice", "weight": 150, "p": 4, "c": 35, "f": 1, "cal": 170},
        "toast": {"name": "Whole Wheat Toast", "weight": 50, "p": 4, "c": 24, "f": 1, "cal": 120},
        "avocado": {"name": "Fresh Avocado", "weight": 100, "p": 2, "c": 9, "f": 15, "cal": 160},
        "shake": {"name": "Whey Protein Shake", "weight": 40, "p": 30, "c": 3, "f": 2, "cal": 150},
        "yogurt": {"name": "Greek Yogurt", "weight": 200, "p": 20, "c": 7, "f": 0, "cal": 110},
    }
    
    for keyword, macros in local_db.items():
        if keyword in text:
            multiplier = 1.0
            if "2 " in text or "two " in text or "double" in text:
                multiplier = 2.0
                
            detected_ingredients.append(Ingredient(
                name=f"{macros['name']} (Est.)",
                estimated_weight_g=macros['weight'] * multiplier,
                protein_g=macros['p'] * multiplier,
                carbs_g=macros['c'] * multiplier,
                fats_g=macros['f'] * multiplier,
                calories=int(macros['cal'] * multiplier)
            ))
            
    if not detected_ingredients:
        detected_ingredients.append(Ingredient(
            name="Unspecified Meal Volume",
            estimated_weight_g=200,
            protein_g=15.0,
            carbs_g=30.0,
            fats_g=10.0,
            calories=270
        ))
        
    total_cal = sum(ing.calories for ing in detected_ingredients)
    
    return MealAnalysis(
        meal_name=f"[Offline Log] {raw_input[:30]}...",
        confidence_score=0.3,
        ingredients=detected_ingredients,
        total_calories=total_cal
    )

# -------------------------------------------------------------------
# 3. STREAMLIT APPLICATION STATE CONFIGURATIONS
# -------------------------------------------------------------------
st.set_page_config(page_title="Eating Well // Bio-Intelligence Engine", layout="wide")

# Persistent state mapping for state pools across application reruns
if "protein_pool" not in st.session_state:
    st.session_state.protein_pool = 42  
if "stamina_pool" not in st.session_state:
    st.session_state.stamina_pool = 64
if "clarity_pool" not in st.session_state:
    st.session_state.clarity_pool = 75

# Immersive dark aesthetic stylesheets
st.markdown("""
    <style>
    .reportview-container { background: #050505; color: #E0E0E0; }
    .stProgress > div > div > div > div { background-color: #39FF14; }
    .hud-card {
        background: #141414;
        border: 1px solid #262626;
        padding: 22px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .guardian-text {
        color: #00D4FF;
        font-family: monospace;
        font-weight: bold;
        letter-spacing: 1px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("EATING WELL // BIOLOGICAL INTERFACE")
st.caption("A16Z SPEEDRUN SYSTEM ARCHITECTURE V2.0 // THE PROACTIVE HEALTH HUD")

if not api_key_env:
    st.warning("⚠️ Running in Local Fallback Node. GEMINI_API_KEY environment variable not configured.")

# -------------------------------------------------------------------
# 4. SIDEBAR: AVATAR HUD COMPONENT
# -------------------------------------------------------------------
with st.sidebar:
    st.header("👤 AVATAR PROFILE")
    st.markdown("---")
    
    st.subheader("💪 STRENGTH (PROTEIN PROFILE)")
    st.progress(st.session_state.protein_pool / 100)
    st.caption(f"Current Value: **{st.session_state.protein_pool}/100**")
    
    st.subheader("⚡ STAMINA (GLYCOGEN LOADING)")
    st.progress(st.session_state.stamina_pool / 100)
    st.caption(f"Current Value: **{st.session_state.stamina_pool}/100**")
    
    st.subheader("🧠 SYSTEMIC CLARITY (MICROS)")
    st.progress(st.session_state.clarity_pool / 100)
    st.caption(f"Current Value: **{st.session_state.clarity_pool}/100**")
    
    st.markdown("---")
    st.subheader("🧪 Core Reset Framework")
    if st.button("Reset Avatar Buff Pools"):
        st.session_state.protein_pool = 42
        st.session_state.stamina_pool = 64
        st.session_state.clarity_pool = 75
        st.rerun()

# -------------------------------------------------------------------
# 5. CORE INTERACTION SECTION: AUDIO, PHOTO, & STRING PROCESSING
# -------------------------------------------------------------------
st.header("📸 INGESTION HUD: VISION & VOICE MULTIMODAL LOOP")

tab1, tab2 = st.tabs(["🖼️ Visual/Text Multi-Modal Scanner", "🎙️ Ambient Voice Link"])

with tab1:
    col_input, col_view = st.columns([1, 1])
    
    with col_input:
        text_desc = st.text_input("Manually declare food elements (e.g., 'Double steak with brown rice')", key="text_desc")
        uploaded_image = st.file_uploader("Drop biological image target array", type=["png", "jpg", "jpeg"])
        execute_analysis = st.button("Scan Biological Load")
    
    with col_view:
        if uploaded_image:
            st.image(uploaded_image, caption="Target Asset Ingested", width=320)

    if execute_analysis:
        with st.spinner("Analyzing macro vectors via Gemini 2.5 Engine..."):
            analysis_result = autonomous_logger(text_desc, uploaded_image)
            
            # Print complete structured schema results
            st.markdown("### 📊 Pixel Scanning Readout")
            st.json(analysis_result.model_dump())
            
            # Extract total nutrient metrics to reward the local session stats
            total_protein_g = sum(ing.protein_g for ing in analysis_result.ingredients)
            total_carbs_g = sum(ing.carbs_g for ing in analysis_result.ingredients)
            
            # Apply math modifiers cleanly to update our cached UI sidebar bars
            st.session_state.protein_pool = min(100, int(st.session_state.protein_pool + total_protein_g))
            st.session_state.stamina_pool = min(100, int(st.session_state.stamina_pool + (total_carbs_g * 0.5)))
            st.success(f"🧬 Stats updated! Added **{int(total_protein_g)}g** Protein to Strength Pool.")
            st.button("Synchronize HUD Updates")

with tab2:
    st.write("Communicate directly with your AI Guardian hands-free while driving, train-loading, or shopping.")
    voice_capture = st.audio_input("Record your environmental intent vector", key="voice_capture")
    
    if voice_capture:
        st.success("Audio transmission clean. Connected to internal processing nodes.")
        
        # In standard alpha expansion, audio bytes get passed down to your STT processing loop
        # Simulating processing loop for localized alpha feedback validation:
        st.markdown("""
            <div class="hud-card" style="border-color: #00D4FF;">
                <p class="guardian-text">// AUDIO STREAM PARSED TRANSCRIPT:</p>
                <p style="font-style: italic; color: #FFFFFF;">
                    "Hey Eating Well, I just got back from a heavy lift. I'm hitting the kitchen next to build a high protein stack. What is my next quest?"
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        # Dynamically trigger local helper response inside voice loop if user targets protein queries
        if st.button("Query AI Guardian Voice Array"):
            st.session_state.protein_pool = min(100, st.session_state.protein_pool + 30)
            st.rerun()

# -------------------------------------------------------------------
# 6. ADVANCED PROACTIVE MECHANICS: THE NEXT QUEST & ACTIVITY SYNC
# -------------------------------------------------------------------
st.markdown("---")
st.header("🎯 CONTEXTUAL OPTIMIZATION LAYER")

col_quest, col_sync = st.columns(2)

with col_quest:
    st.subheader("🔮 The Next Quest Engine")
    st.caption("Predictive meal profiling to capture consumer target intents early.")
    
    user_craving = st.selectbox(
        "Select your upcoming food flavor profile target:",
        ["Warm & Savory", "Crisp & Fresh", "High-Protein Quick Fuel", "Slow Glycogen Energy"]
    )
    
    if st.button("Generate Proactive Quest Vector"):
        st.markdown('<div class="hud-card">', unsafe_allow_html=True)
        if st.session_state.protein_pool < 50:
            st.markdown("<span style='color: #FF3333; font-weight:bold;'>⚠️ CRITICAL DEFICIT REGISTERED</span>", unsafe_allow_html=True)
            st.write(f"**AI Guardian:** 'Your current Strength profile is critically down at **{st.session_state.protein_pool}%**. Your optimal pathway for a **{user_craving}** profile demands exactly **35g+ of targeted clean protein**.'")
            st.info("💡 **Quest Path recommendations:** Pan-seared wild salmon over greens, or a double-sliced turkey burger stack.")
        else:
            st.markdown("<span style='color: #39FF14; font-weight:bold;'>✅ LOGISTICAL PROFILE OPTIMAL</span>", unsafe_allow_html=True)
            st.write(f"**AI Guardian:** 'Metabolic levels are locked and stable. To satisfy your **{user_craving}** profile loop, maintain standard maintenance targets with clean greens and light grains.'")
        st.markdown('</div>', unsafe_allow_html=True)

with col_sync:
    st.subheader("🌦️ Biometric Activity Sync")
    st.caption("Harmonizing metabolic consumption indexes with outdoor environments.")
    
    env_weather = st.selectbox("Current Environmental Telemetry Node", ["Clear & Sunny", "Overcast & Raining", "Freezing Temperatures"])
    user_ingest_type = st.radio("Target Current Load Archetype:", ["Heavy Macro-Load Meal", "Light Focus Spark Energy"])
    
    if st.button("Process Environmental Habit Modifier"):
        st.markdown('<div class="hud-card" style="border-color: #39FF14;">', unsafe_allow_html=True)
        st.write(f"**NODE CONFIG:** {env_weather.upper()} // **LOAD ANALYSIS:** {user_ingest_type.upper()}")
        st.write("---")
        
        if user_ingest_type == "Heavy Macro-Load Meal" and env_weather == "Clear & Sunny":
            st.markdown("""
                <span style='color:#39FF14; font-weight:bold;'>🔓 UNLOCKED HABIT: OUTDOOR STEADY GLUCOSE SHIELD</span><br>
                Sky telemetry is beautiful. Embark on a brisk 15-minute steady walk immediately post-meal. This actively redirects digestion circulation, limits glucose volatility spikes, and keeps focus clean.
            """, unsafe_allow_html=True)
        elif user_ingest_type == "Heavy Macro-Load Meal" and env_weather == "Overcast & Raining":
            st.markdown("""
                <span style='color:#00D4FF; font-weight:bold;'>🔓 UNLOCKED HABIT: INDOOR DIGESTION STRETCH</span><br>
                Rain tracking detected. Execute an indoor 10-minute mobility sequencing routine to assist core vascular processing and prevent post-load lethargy crashes.
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
                <span style='color:#FFFFFF; font-weight:bold;'>🔓 UNLOCKED HABIT: STEADY RECOVERY BLOCK</span><br>
                Systemic energy ratios balanced. You are green-lit for an immediate high-focus coding sprint, studio scoring flow, or intense weight training layout.
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)