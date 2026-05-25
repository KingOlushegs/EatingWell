import sys
import os
from tracker import DailyNutritionTracker

def run_command_center():
    tracker = DailyNutritionTracker(protein_goal_g=200, calorie_goal=3000)
    
    print("\n" + "="*50)
    print("      🍏 WELCOME TO EATING WELL COMMAND CENTER 🍏      ")
    print("="*50)
    
    while True:
        print("\n[MAIN MENU] What would you like to do?")
        print("  1. Log a new meal (Text only)")
        print("  2. Log a new meal (With Photo File)")
        print("  3. View current Daily Dashboard")
        print("  4. 🧠 Get AI Performance Coach Insights")
        print("  5. Exit Application")
        
        choice = input("\nSelect an option (1-5): ").strip()
        
        if choice == "1":
            raw_meal = input("\n📝 Describe what you just ate: ")
            if raw_meal.strip():
                tracker.log_meal(raw_meal)
                
        elif choice == "2":
            img_path = input("\n🖼️ Enter the exact file path to your meal photo (e.g., meal.jpg): ").strip()
            if not os.path.exists(img_path):
                print(f"❌ File not found at path: '{img_path}'. Please check the path and try again.")
                continue
                
            raw_meal = input("📝 Optional text description (or leave blank): ")
            tracker.log_meal(raw_meal, image_path=img_path)
            
        elif choice == "3":
            tracker.display_daily_summary()
            
        elif choice == "4":
            insights = tracker.generate_coaching_insights()
            print("\n" + "~"*50)
            print("           📋 AI COACH PERFORMANCE REVIEW           ")
            print("~"*50)
            print(insights)
            print("~"*50)
            
        elif choice == "5":
            print("\n💾 All data safely stored in diary.json. Exiting Command Center. Stay disciplined!")
            print("="*50 + "\n")
            sys.exit()
            
        else:
            print("❌ Invalid choice. Please enter a number between 1 and 5.")

if __name__ == "__main__":
    run_command_center()