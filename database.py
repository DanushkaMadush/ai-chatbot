import sqlite3

DB_NAME = "chat_history.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            role TEXT,
            content TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            field TEXT,
            duration TEXT,
            fees TEXT,
            institute TEXT,
            requirements TEXT,
            validity TEXT
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS unknown_questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT
        )
    """)

    conn.commit()
    conn.close()


def save_message(session_id, role, content):
    conn = sqlite3.connect(DB_NAME)
    conn.execute(
        "INSERT INTO messages (session_id, role, content) VALUES (?, ?, ?)",
        (session_id, role, content)
    )
    conn.commit()
    conn.close()

def get_messages(session_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT role, content FROM messages WHERE session_id=? ORDER BY timestamp",
        (session_id,)
    )

    messages = cursor.fetchall()
    conn.close()
    return messages

def get_all_courses():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT name, field, duration, fees, institute FROM courses")
    data = cursor.fetchall()
    conn.close()
    return data


def get_course_details(course_name):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT name, fees, requirements, validity 
        FROM courses 
        WHERE name LIKE ?
    """, (f"%{course_name}%",))
    data = cursor.fetchall()
    conn.close()
    return data


def save_unknown_question(question):
    conn = sqlite3.connect(DB_NAME)
    conn.execute(
        "INSERT INTO unknown_questions (question) VALUES (?)",
        (question,)
    )
    conn.commit()
    conn.close()

def seed_courses():
    conn = sqlite3.connect(DB_NAME)

    conn.execute("""
    INSERT INTO courses (name, field, duration, fees, institute, requirements, validity)
    VALUES 
    ('Software Engineering', 'IT', '4 years', '$4000', 'ESOFT Metro Campus', 'Advanced Lavel', 'International'),
    ('Cyber Security', 'IT', '4 years', '$4500', 'ESOFT Metro Campus', 'Advanced Lavel', 'International'),
    ('Network Engineering', 'IT', '3 years', '$3500', 'ESOFT Metro Campus', Advanced Lavel', 'Local'),
    ('Business Management', 'Business', '3 years', '$3000', 'ESOFT Metro Campus', 'Advanced Lavel', 'International'),
    ('Fashion Designing', 'Design', '3 years', '$3200', 'ESOFT Metro Campus', 'Advanced Lavel', 'Local')
    """)

    conn.commit()
    conn.close()