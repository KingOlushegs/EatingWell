import streamlit as st
import os
import pandas as pd
from engine import autonomous_logger
from database import init_db, save_meal_to_db, load_meals_from_db, get_active_profile, update_active_profile, get_all_profiles
from tracker import DailyNutritionTracker

# --- ZERO-DEPENDENCY KEY LOADER ---
if os.path.exists(".env"):
    with open(".env", "r") as f:
        for line in f:
            if line.strip() and not line.startswith("#"):
                key, value = line.strip().split("=", 1)
                os.environ[key.strip()] = value.strip().strip("'").strip('"')

# Re-initialize upgraded schemas
init_db()

st.set_page_config(page_title="Eating Well Engine", page_icon="🍏", layout="wide")
st.title("🍏 Eating Well: Elite Full-Stack Performance System")
st.markdown("---")

# --- PROFILE ARCHITECTURE SIDEBAR ---
st.sidebar.header("🎯 Active Athlete Profile")
all_profiles = get_all_profiles()
current_profile = get_active_profile()

selected_profile = st.sidebar.selectbox(
    "Switch Current Phase Targets:",
    all_profiles,
    index=all_profiles.index(current_profile["name"])
)

# If the profile drops down to a new phase, update state immediately
if selected_profile != current_profile["name"]:
    update_active_profile(selected_profile)
    st.rerun()

# Set current tracking goals based on profile table selection
calorie_goal = current_profile["calories"]
protein_goal = current_profile["protein"]

st.sidebar.metric("🔥 Phase Calories", f"{calorie_goal} kcal")
st.sidebar.metric("🍗 Phase Protein Target", f"{protein_goal}g")

# --- ENGINE DATA STREAM EXTRACTIONS ---
history = load_meals_from_db()

total_calories = sum(m['total_calories'] for m in history)
total_protein = sum(sum(ing['protein_g'] for ing in m['ingredients']) for m in history)
total_carbs = sum(sum(ing['carbs_g'] for ing in m['ingredients']) for m in history)
total_fats = sum(sum(ing['fats_g'] for ing in m['ingredients']) for m in history)

# Standing Telemetry Dashboard Row
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("🔥 Energy Balance En Route", f"{total_calories} / {calorie_goal} kcal")
    st.progress(min(total_calories / calorie_goal, 1.0))
with col2:
    st.metric("🍗 Protein Concentration", f"{total_protein:.1f}g / {protein_goal}g")
    st.progress(min(total_protein / protein_goal, 1.0))
with col3:
    st.metric("🍚 Carbohydrates", f"{total_carbs:.1f}g")
with col4:
    st.metric("🥑 Essential Fats", f"{total_fats:.1f}g")

st.markdown("---")

# --- HISTORICAL ADVANCED ANALYTICS CHART LAYER ---
if history:
    st.subheader("📊 Performance Trend Timelines")
    
    chart_data = []
    for m in history:
        date_str = m["timestamp"].split(" ")[0]
        p_val = sum(ing['protein_g'] for ing in m['ingredients'])
        chart_data.append({"Date": date_str, "Calories": m["total_calories"], "Protein (g)": p_val})
        
    df = pd.DataFrame(chart_data)
    grouped_df = df.groupby("Date").sum().sort_index()

    tab1, tab2 = st.tabs(["🔥 Calorie Volume Chronology", "🍗 Protein Intake Vectors"])
    with tab1:
        st.bar_chart(grouped_df["Calories"])
    with tab2:
        st.line_chart(grouped_df["Protein (g)"])
    st.markdown("---")

# Main Interface Split Row
left_input, right_coach = st.columns([1, 1])

with left_input:
    st.subheader("📝 Log New Intake")
    ingestion_mode = st.radio("Choose Ingestion Method:", ["Text Input Only", "Upload Photo File"])
    
    raw_text = st.text_input("Describe your food intake:")
    uploaded_image = None
    temp_image_path = None

    if ingestion_mode == "Upload Photo File":
        uploaded_image = st.file_uploader("Drag and drop meal photo here...", type=["jpg", "jpeg", "png"])
        if uploaded_image:
            temp_image_path = os.path.join(".", uploaded_image.name)
            with open(temp_image_path, "wb") as f:
                f.write(uploaded_image.getbuffer())
            st.image(uploaded_image, caption="Staged Image Pipeline Asset", width=300)

    if st.button("Execute Core Ingestion Pipeline", use_container_width=True):
        if raw_text or temp_image_path:
            with st.spinner("Processing unstructured context autonomously..."):
                try:
                    # Request pipeline analysis from backend engine
                    meal_analysis = autonomous_logger(raw_text, image_path=temp_image_path)
                    save_meal_to_db(meal_analysis)
                    st.success(f"Successfully logged: '{meal_analysis.meal_name}'")
                    
                    # --- INTERFACE DISPLAY FOR STRATEGIC & BEHAVIORAL LAYER ---
                    st.markdown("---")
                    st.subheader("⚡ Immediate Pipeline Feedback Array")
                    
                    # Itemized Ingredient Badges (Immediate view)
                    if hasattr(meal_analysis, 'ingredients') and meal_analysis.ingredients:
                        st.markdown("##### 🔍 Identified Meal Elements:")
                        i_cols = st.columns(min(len(meal_analysis.ingredients), 4))
                        for i, ing in enumerate(meal_analysis.ingredients):
                            with i_cols[i % 4]:
                                st.markdown(
                                    f"""<div style='background: #1e1e1e; padding: 8px; border-radius: 5px; border-left: 3px solid #39FF14;'>
                                    <strong>{ing.name}</strong> ({ing.estimated_weight_g}g)<br>
                                    <span style='color: #39FF14;'>{ing.calories} kcal</span>
                                    </div>""", unsafe_allow_html=True
                                )
                    
                    # Split view for Strategic Analysis and Behavioral Compliance
                    col_strat, col_behave = st.columns(2)
                    
                    with col_strat:
                        if hasattr(meal_analysis, 'strategic_layer') and meal_analysis.strategic_layer:
                            metabolic_now = getattr(meal_analysis.strategic_layer, 'metabolic_impact_the_now', None)
                            downstream_next = getattr(meal_analysis.strategic_layer, 'downstream_compensation_the_next', None)
                            if metabolic_now:
                                st.info(f"**Immediate Metabolic Impact (The NOW):**\n\n{metabolic_now}")
                            if downstream_next:
                                st.warning(f"**Downstream Compensation (The NEXT):**\n\n{downstream_next}")
                                
                    with col_behave:
                        if hasattr(meal_analysis, 'behavioral_matrix') and meal_analysis.behavioral_matrix:
                            hydration = getattr(meal_analysis.behavioral_matrix, 'hydration_status', None)
                            etiquette = getattr(meal_analysis.behavioral_matrix, 'environmental_etiquette', None)
                            if hydration:
                                st.success(f"**💧 Hydration Vector:**\n\n{hydration}")
                            if etiquette:
                                st.markdown(
                                    f"""<div style='background: #2b1818; padding: 12px; border-radius: 5px; border: 1px solid #ff4b4b; color: #E0E0E0;'>
                                    <strong style='color: #ff4b4b;'>🍽️ Behavioral Etiquette Note:</strong><br>{etiquette}
                                    </div>""", unsafe_allow_html=True
                                )
                    
                    if temp_image_path and os.path.exists(temp_image_path):
                        os.remove(temp_image_path)
                    
                    import time
                    time.sleep(5.0)  # Extended time block to review immediate structural callouts
                    st.rerun()
                    
                except Exception as e:
                    from engine import local_heuristic_fallback
                    offline_analysis = local_heuristic_fallback(raw_text if raw_text else "Photo Log (Offline)")
                    save_meal_to_db(offline_analysis)
                    st.success(f"💾 Offline preservation activated: '{offline_analysis.meal_name}'")
                    
                    import time
                    time.sleep(2.0)
                    st.rerun()
        else:
            st.warning("Please provide either a text description or a food photo.")

with right_coach:
    st.subheader("🧠 Performance Coaching Engine")
    if st.button("Compile Daily Insights", use_container_width=True):
        if not history:
            st.info("Log fuel items to trigger performance analysis benchmarks.")
        else:
            with st.spinner("Generating performance coach feedback arrays..."):
                temp_tracker = DailyNutritionTracker(protein_goal_g=protein_goal, calorie_goal=calorie_goal)
                insights = temp_tracker.generate_coaching_insights()
                st.info(insights)

# --- HISTORICAL TIMELINE LEDGER ---
st.markdown("---")
st.subheader("📂 Historical Timeline Ledger")
if history:
    for idx, meal in enumerate(history, 1):
        with st.expander(f"{idx}. {meal['meal_name']} — {meal['total_calories']} kcal ({meal['timestamp']})"):
            
            # Itemized breakdown block
            st.markdown("**🔍 Identified Meal Elements & Individual Macro Load:**")
            h_ingredients = meal.get('ingredients', [])
            if h_ingredients:
                h_cols = st.columns(min(len(h_ingredients), 4))
                for i, ing in enumerate(h_ingredients):
                    with h_cols[i % 4]:
                        st.markdown(
                            f"""<div style='background: #141414; padding: 10px; border-radius: 5px; border: 1px solid #262626;'>
                            <strong>{ing.get('name')}</strong> ({ing.get('estimated_weight_g')}g)<br>
                            <span style='color: #39FF14;'>⚡ {ing.get('calories')} kcal</span><br>
                            <small style='color: #888;'>P: {ing.get('protein_g')}g | C: {ing.get('carbs_g')}g | F: {ing.get('fats_g')}g</small>
                            </div>""", unsafe_allow_html=True
                        )
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Nested Strategic & Behavioral Historical Blocks
            col_hist_left, col_hist_right = st.columns(2)
            
            with col_hist_left:
                if "strategic_layer" in meal and meal["strategic_layer"]:
                    st.markdown("**⚡ Logged Strategic Metrics:**")
                    strat = meal["strategic_layer"]
                    if isinstance(strat, dict):
                        st.info(f"💡 **Impact:** {strat.get('metabolic_impact_the_now', 'N/A')}\n\n🎯 **Compensation:** {strat.get('downstream_compensation_the_next', 'N/A')}")
            
            with col_hist_right:
                if "behavioral_matrix" in meal and meal["behavioral_matrix"]:
                    st.markdown("**🍽️ Contextual & Behavioral Audits:**")
                    behave = meal["behavioral_matrix"]
                    if isinstance(behave, dict):
                        st.success(f"💧 **Hydration Status:** {behave.get('hydration_status', 'N/A')}")
                        st.markdown(
                            f"""<div style='background: #231919; padding: 10px; border-radius: 5px; border: 1px solid #ff4b4b; font-size: 14px;'>
                            <span style='color: #ff4b4b; font-weight: bold;'>Etiquette/Environment Analysis:</span><br>{behave.get('environmental_etiquette', 'N/A')}
                            </div>""", unsafe_allow_html=True
                        )
else:
    st.text("No data streams detected in sqlite3 cluster storage.")