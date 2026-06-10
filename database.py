import sqlite3
import json
from datetime import datetime

DB_NAME = "eating_well.db"

def init_db():
    """Initializes SQLite tables for meals and user goal profiles with schema evolution safety."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Core Meals Table - Upgraded to safely capture full JSON payloads and strategic parameters
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS meals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            meal_name TEXT,
            total_calories INTEGER,
            ingredients_json TEXT,
            strategic_json TEXT,
            behavioral_json TEXT,
            guardian_voice_script TEXT
        )
    ''')
    
    # Check for legacy schema and dynamically patch missing columns to preserve existing local logs
    cursor.execute("PRAGMA table_info(meals)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if "strategic_json" not in columns:
        cursor.execute("ALTER TABLE meals ADD COLUMN strategic_json TEXT")
    if "behavioral_json" not in columns:
        cursor.execute("ALTER TABLE meals ADD COLUMN behavioral_json TEXT")
    if "guardian_voice_script" not in columns:
        cursor.execute("ALTER TABLE meals ADD COLUMN guardian_voice_script TEXT")
    
    # User Profiles Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            profile_name TEXT UNIQUE,
            calorie_goal INTEGER,
            protein_goal INTEGER,
            is_active INTEGER DEFAULT 0
        )
    ''')
    
    # Insert default athletic baseline profiles if table cluster is uninitialized
    cursor.execute('SELECT COUNT(*) FROM profiles')
    if cursor.fetchone()[0] == 0:
        cursor.executemany('''
            INSERT INTO profiles (profile_name, calorie_goal, protein_goal, is_active)
            VALUES (?, ?, ?, ?)
        ''', [
            ("Mass Building (Bulk)", 3500, 220, 1),
            ("Leaning Out (Cut)", 2400, 200, 0),
            ("High Performance Maintain", 3000, 180, 0)
        ])
        
    conn.commit()
    conn.close()

def save_meal_to_db(meal_data):
    """Saves a fully-validated MealAnalysis object into SQLite, serializing nested tracking structures."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Handle both object attributes (from active Gemini model responses) and raw fallback dict parsing safely
    ingredients = getattr(meal_data, 'ingredients', [])
    ingredients_list = [ing.model_dump() if hasattr(ing, 'model_dump') else ing for ing in ingredients]
    ingredients_json = json.dumps(ingredients_list)
    
    # Serialize the Advanced Strategic Layer
    strategic_layer = getattr(meal_data, 'strategic_layer', None)
    strategic_json = json.dumps(strategic_layer.model_dump() if hasattr(strategic_layer, 'model_dump') else strategic_layer)
    
    # Serialize the Newly Integrated Behavioral Matrix Layout
    behavioral_matrix = getattr(meal_data, 'behavioral_matrix', None)
    behavioral_json = json.dumps(behavioral_matrix.model_dump() if hasattr(behavioral_matrix, 'model_dump') else behavioral_matrix)
    
    # Extract structural voice link text script
    voice_script = getattr(meal_data, 'guardian_voice_script', None)
    
    cursor.execute('''
        INSERT INTO meals (timestamp, meal_name, total_calories, ingredients_json, strategic_json, behavioral_json, guardian_voice_script)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
        getattr(meal_data, 'meal_name', 'Unknown Intake'), 
        getattr(meal_data, 'total_calories', 0), 
        ingredients_json,
        strategic_json,
        behavioral_json,
        voice_script
    ))
    
    conn.commit()
    conn.close()

def load_meals_from_db():
    """Retrieves all historical records, deserializing complex optimization metrics back into dictionary matrices."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT meal_name, total_calories, ingredients_json, timestamp, strategic_json, behavioral_json, guardian_voice_script 
        FROM meals 
        ORDER BY id DESC
    ''')
    rows = cursor.fetchall()
    conn.close()
    
    meals = []
    for row in rows:
        meals.append({
            "meal_name": row[0],
            "total_calories": row[1],
            "ingredients": json.loads(row[2]) if row[2] else [],
            "timestamp": row[3],
            "strategic_layer": json.loads(row[4]) if row[4] else {},
            "behavioral_matrix": json.loads(row[5]) if row[5] else {},
            "guardian_voice_script": row[6]
        })
    return meals

# --- Profile Management Functions ---
def get_active_profile():
    """Fetches the current active goal profile configuration."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT profile_name, calorie_goal, protein_goal FROM profiles WHERE is_active = 1 LIMIT 1')
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"name": row[0], "calories": row[1], "protein": row[2]}
    return {"name": "Default", "calories": 3000, "protein": 200}

def update_active_profile(profile_name):
    """Switches the active flag to a newly selected profile cluster."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('UPDATE profiles SET is_active = 0')
    cursor.execute('UPDATE profiles SET is_active = 1 WHERE profile_name = ?', (profile_name,))
    conn.commit()
    conn.close()

def get_all_profiles():
    """Returns a dictionary mapping of all stored target configurations."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT profile_name FROM profiles')
    rows = cursor.fetchall()
    conn.close()
    return [r[0] for r in rows]