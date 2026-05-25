import os
import json
from datetime import datetime
from typing import Optional  
from engine import autonomous_logger, MealAnalysis

class DailyNutritionTracker:
    def __init__(self, protein_goal_g=180, calorie_goal=2700, filename="diary.json"):
        self.protein_goal_g = protein_goal_g
        self.calorie_goal = calorie_goal
        self.filename = filename
        self.meal_history = []
        
        # Automatically load past data on startup
        self.load_from_disk()

    def log_meal(self, raw_input: str, image_path: Optional[str] = None):
        """Parses raw input (text and/or image), appends to state, and persists to disk."""
        print(f"\n[System Log - {datetime.now().strftime('%H:%M:%S')}] Processing raw meal input...")
        
        try:
            # Pass both the text and the image path into our updated engine
            meal_data = autonomous_logger(raw_input, image_path=image_path)
            self.meal_history.append(meal_data)
            print(f"✅ Successfully logged: '{meal_data.meal_name}'")
            
            self.save_to_disk()
            self.display_daily_summary()
            
        except Exception as e:
            print(f"\n❌ Operational Error: Could not parse input. Details: {e}")
            self.display_daily_summary()

    def save_to_disk(self):
        """Serializes our complex Pydantic data models into a clean JSON file."""
        # Convert our list of Pydantic objects into raw dictionaries Python can save
        serialized_meals = [meal.model_dump() for meal in self.meal_history]
        
        with open(self.filename, "w") as f:
            json.dump(serialized_meals, f, indent=4)
        print(f"💾 State persisted securely to '{self.filename}'")

    def load_from_disk(self):
        """Looks for an existing database file to restore the user's session history."""
        if os.path.exists(self.filename):
            print(f"📂 Found existing data file '{self.filename}'. Restoring session state...")
            try:
                with open(self.filename, "r") as f:
                    raw_data = json.load(f)
                
                # Reconstruct the text data back into strict Pydantic objects
                self.meal_history = [MealAnalysis.model_validate(meal) for meal in raw_data]
                print(f"🔄 Successfully restored {len(self.meal_history)} meals from disk.")
            except Exception as e:
                print(f"⚠️ Could not read data file, starting with a fresh session. Error: {e}")
        else:
            print("🆕 No existing data file found. Creating a fresh daily log session.")

    def display_daily_summary(self):
        """Calculates cumulative analytics across all logged meals."""
        total_calories = sum(meal.total_calories for meal in self.meal_history)
        total_protein = sum(sum(ing.protein_g for ing in meal.ingredients) for meal in self.meal_history)
        total_carbs = sum(sum(ing.carbs_g for ing in meal.ingredients) for meal in self.meal_history)
        total_fats = sum(sum(ing.fats_g for ing in meal.ingredients) for meal in self.meal_history)

        print("\n" + "="*40)
        print("        DAILY NUTRITION DASHBOARD        ")
        print("="*40)
        print(f"Meals Logged: {len(self.meal_history)}")
        for i, meal in enumerate(self.meal_history, 1):
            print(f"  {i}. {meal.meal_name} ({meal.total_calories} kcal)")
        print("-"*40)
        print("CUMULATIVE MACROS:")
        print(f"  🔥 Calories: {total_calories} / {self.calorie_goal} kcal")
        print(f"  🍗 Protein:  {total_protein:.1f}g / {self.protein_goal_g}g")
        print(f"  🍚 Carbs:    {total_carbs:.1f}g")
        print(f"  🥑 Fats:     {total_fats:.1f}g")
        print("="*40)

    def generate_coaching_insights(self) -> str:
        """Compiles the entire daily log and passes it to Gemini for athletic coaching feedback."""
        if not self.meal_history:
            return "No meals logged today. Get some fuel in your system before asking for coaching insights!"

        print(f"\n🧠 [AI Coach] Analyzing today's nutrition timeline and macro targets...")

        # 1. Convert our logged data into a clean text summary for the AI to read
        history_summary = ""
        for i, meal in enumerate(self.meal_history, 1):
            history_summary += f"\nMeal {i}: {meal.meal_name} ({meal.total_calories} kcal)\n"
            for ing in meal.ingredients:
                history_summary += f"  - {ing.name}: P:{ing.protein_g}g, C:{ing.carbs_g}g, F:{ing.fats_g}g\n"

        # 2. Craft a high-performance prompt
        coach_prompt = (
            f"You are an elite, high-performance athletic nutrition coach. "
            f"Analyze the user's daily meal log and evaluate their performance against these targets:\n"
            f"- Calorie Goal: {self.calorie_goal} kcal\n"
            f"- Protein Goal: {self.protein_goal_g}g\n\n"
            f"Here is their logged food data for today:\n{history_summary}\n"
            f"Provide a concise, direct, and motivating 3-paragraph breakdown:\n"
            f"1. Macro Assessment: How well did they hit their numbers (especially protein for muscle recovery)?\n"
            f"2. Micronutrient/Fuel Quality: Evaluate the quality of their food choices (e.g., salmon, whole grains vs processed items).\n"
            f"3. Actionable Next Steps: What exactly should they eat next, or adjust tomorrow, to optimize performance?"
        )

        try:
            # Call our existing Gemini client directly
            from engine import client
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=coach_prompt
            )
            return response.text
        except Exception as e:
            return f"❌ Coach was unable to review data due to a network issue: {e}"

# --- Test the Persistent Storage Engine ---
if __name__ == "__main__":
    tracker = DailyNutritionTracker(protein_goal_g=200, calorie_goal=3000)
    
    # Let's log a late night snack to test persistence
    tracker.log_meal("A bowl of Greek yogurt with a drizzle of honey and a handful of almonds")