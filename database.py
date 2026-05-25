import sqlite3
import json
from datetime import datetime

DB_NAME = "eating_well.db"

def init_db():
    """Initializes SQLite tables for meals and user goal profiles."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Core Meals Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS meals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            meal_name TEXT,
            total_calories INTEGER,
            ingredients_json TEXT
        )
    ''')
    
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
    
    # Insert some default athletic baseline profiles if the table is empty
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
    """Saves a parsed MealAnalysis object into SQLite with an explicit date stamp."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    ingredients_list = [ing.model_dump() for ing in meal_data.ingredients]
    ingredients_json = json.dumps(ingredients_list)
    
    cursor.execute('''
        INSERT INTO meals (timestamp, meal_name, total_calories, ingredients_json)
        VALUES (?, ?, ?, ?)
    ''', (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), meal_data.meal_name, meal_data.total_calories, ingredients_json))
    conn.commit()
    conn.close()

def load_meals_from_db():
    """Retrieves all historical meals with timestamps included."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT meal_name, total_calories, ingredients_json, timestamp FROM meals ORDER BY id DESC')
    rows = cursor.fetchall()
    conn.close()
    
    meals = []
    for row in rows:
        meals.append({
            "meal_name": row[0],
            "total_calories": row[1],
            "ingredients": json.loads(row[2]),
            "timestamp": row[3]
        })
    return meals

# --- New Profile Management Functions ---
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