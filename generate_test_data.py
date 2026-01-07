import sqlite3
import random
from datetime import datetime, timedelta
import hashlib

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def generate_users(conn):
    users = [
        ("john_doe", hash_password("password123"), "John Doe", 45, "Male", "Type 2"),
        ("jane_smith", hash_password("securepass"), "Jane Smith", 32, "Female", "Type 1"),
        ("mike_johnson", hash_password("test1234"), "Mike Johnson", 58, "Male", "Prediabetes"),
        ("sarah_williams", hash_password("health123"), "Sarah Williams", 29, "Female", "Gestational"),
        ("david_brown", hash_password("demo123"), "David Brown", 50, "Male", "None")
    ]
    
    cursor = conn.cursor()
    cursor.executemany('''
        INSERT INTO users (username, password, full_name, age, gender, diabetes_type)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', users)
    conn.commit()

def generate_bp_readings(conn, user_id, num_readings=30):
    cursor = conn.cursor()
    base_date = datetime.now() - timedelta(days=num_readings)
    
    for i in range(num_readings):
        date = (base_date + timedelta(days=i)).strftime("%Y-%m-%d")
        time = datetime.strptime(f"{random.randint(6,22)}:{random.randint(0,59):02d}", "%H:%M").strftime("%H:%M")
        
        # Generate realistic BP values with some variation
        if random.random() < 0.8:  # 80% normal readings
            systolic = random.randint(100, 130)
            diastolic = random.randint(60, 85)
        else:  # 20% elevated/high readings
            systolic = random.randint(135, 160)
            diastolic = random.randint(85, 100)
            
        pulse = random.randint(60, 100)
        notes = random.choice(["", "After exercise", "Before bed", "Morning reading", ""])
        
        cursor.execute('''
            INSERT INTO bp_readings (user_id, date, time, systolic, diastolic, pulse, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, date, time, systolic, diastolic, pulse, notes))
    
    conn.commit()

def generate_bs_readings(conn, user_id, diabetes_type, num_readings=50):
    cursor = conn.cursor()
    base_date = datetime.now() - timedelta(days=num_readings//2)  # More readings per day
    
    measurement_types = ["Fasting", "Before Meal", "After Meal", "Before Bed", "Random"]
    meal_contexts = ["", "Breakfast", "Lunch", "Dinner", "Snack"]
    
    for i in range(num_readings):
        date = (base_date + timedelta(days=i//2)).strftime("%Y-%m-%d")
        time = datetime.strptime(f"{random.randint(6,22)}:{random.randint(0,59):02d}", "%H:%M").strftime("%H:%M")
        
        measurement_type = random.choice(measurement_types)
        meal_ctx = meal_contexts[measurement_types.index(measurement_type)] if measurement_type in ["Before Meal", "After Meal"] else ""
        
        # Generate glucose levels based on diabetes type
        if diabetes_type == "Type 1":
            if measurement_type == "Fasting":
                glucose = random.randint(80, 180)  # Wider range for Type 1
            elif measurement_type == "After Meal":
                glucose = random.randint(120, 250)
            else:
                glucose = random.randint(70, 200)
        elif diabetes_type == "Type 2":
            if measurement_type == "Fasting":
                glucose = random.randint(100, 160)
            elif measurement_type == "After Meal":
                glucose = random.randint(140, 220)
            else:
                glucose = random.randint(90, 180)
        elif diabetes_type == "Prediabetes":
            if measurement_type == "Fasting":
                glucose = random.randint(90, 130)
            elif measurement_type == "After Meal":
                glucose = random.randint(120, 180)
            else:
                glucose = random.randint(80, 150)
        else:  # Normal or gestational
            if measurement_type == "Fasting":
                glucose = random.randint(70, 100)
            elif measurement_type == "After Meal":
                glucose = random.randint(80, 140)
            else:
                glucose = random.randint(70, 120)
        
        notes = random.choice(["", "Felt dizzy", "After workout", "Stressful day", ""])
        
        cursor.execute('''
            INSERT INTO bs_readings (user_id, date, time, glucose_level, measurement_type, meal_context, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, date, time, glucose, measurement_type, meal_ctx, notes))
    
    conn.commit()

def main():
    conn = sqlite3.connect('health_monitor.db')
    
    # Create tables if they don't exist
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            full_name TEXT,
            age INTEGER,
            gender TEXT,
            diabetes_type TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bp_readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            systolic INTEGER NOT NULL,
            diastolic INTEGER NOT NULL,
            pulse INTEGER,
            notes TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bs_readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            glucose_level INTEGER NOT NULL,
            measurement_type TEXT NOT NULL,
            meal_context TEXT,
            notes TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    
    conn.commit()
    
    # Generate synthetic data
    print("Generating test users...")
    generate_users(conn)
    
    # Get user IDs and their diabetes types
    cursor.execute("SELECT id, diabetes_type FROM users")
    users = cursor.fetchall()
    
    for user_id, diabetes_type in users:
        print(f"Generating data for user {user_id} ({diabetes_type})...")
        generate_bp_readings(conn, user_id)
        generate_bs_readings(conn, user_id, diabetes_type)
    
    print("Synthetic data generation complete!")
    conn.close()

if __name__ == '__main__':
    main()