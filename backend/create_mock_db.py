#!/usr/bin/env python3
"""
Script to create a mock database with sample data for the QuizMaster application.
Run this script from the backend directory to create a new mock_quizmaster.db file.
"""

import os
import sys
import random
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
import sqlite3
import faker

# Initialize faker for generating realistic data
fake = faker.Faker()

# Database file path
DB_FILE = 'mock_quizmaster.db'

# Disable auto-increment for all tables
DISABLE_AUTOINCREMENT = True

# ID ranges for different entity types (same as in utils.py)
ID_RANGES = {
    'user': (1000, 9999),     # 1000-9999
    'subject': (10000, 19999), # 10000-19999
    'chapter': (20000, 29999), # 20000-29999
    'quiz': (30000, 39999),    # 30000-39999
    'question': (40000, 49999), # 40000-49999
    'score': (50000, 59999)    # 50000-59999
}

# Track used IDs to avoid duplicates
used_ids = {
    'user': set(),
    'subject': set(),
    'chapter': set(),
    'quiz': set(),
    'question': set(),
    'score': set()
}

def generate_id(entity_type, index=0):
    """Generate a professional-looking ID for an entity"""
    min_id, max_id = ID_RANGES[entity_type]
    
    # Start with a base ID
    base_id = min_id + index * 50
    
    # Find the next available ID
    new_id = base_id
    while new_id in used_ids[entity_type]:
        new_id += 1
        if new_id > max_id:
            # If we've reached the max, wrap around to min + some offset
            new_id = min_id + random.randint(1, 100)
    
    # Mark this ID as used
    used_ids[entity_type].add(new_id)
    
    return new_id

# Check if database already exists
if os.path.exists(DB_FILE):
    print(f"Database file {DB_FILE} already exists.")
    choice = input("Do you want to delete it and create a new one? (y/n): ")
    if choice.lower() != 'y':
        print("Exiting without changes.")
        sys.exit(0)
    try:
        os.remove(DB_FILE)
        print(f"Deleted existing {DB_FILE}.")
    except Exception as e:
        print(f"Warning: Could not delete existing file: {e}")
        print("Will attempt to overwrite it.")

# Connect to the database (creates a new file)
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# Create tables

# User table
cursor.execute('''
CREATE TABLE user (
    id INTEGER PRIMARY KEY,
    username VARCHAR(80) NOT NULL UNIQUE,
    password_hash VARCHAR(128) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE,
    qualification VARCHAR(100),
    date_of_birth DATE,
    is_admin BOOLEAN DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
)
''')

# Subject table
cursor.execute('''
CREATE TABLE subject (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
)
''')

# Chapter table
cursor.execute('''
CREATE TABLE chapter (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    subject_id INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (subject_id) REFERENCES subject (id)
)
''')

# Quiz table
cursor.execute('''
CREATE TABLE quiz (
    id INTEGER PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    description TEXT,
    chapter_id INTEGER NOT NULL,
    duration INTEGER NOT NULL,
    date_of_quiz DATETIME NOT NULL,
    remarks TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (chapter_id) REFERENCES chapter (id)
)
''')

# Question table
cursor.execute('''
CREATE TABLE question (
    id INTEGER PRIMARY KEY,
    quiz_id INTEGER NOT NULL,
    question_text TEXT NOT NULL,
    option1 VARCHAR(200) NOT NULL,
    option2 VARCHAR(200) NOT NULL,
    option3 VARCHAR(200) NOT NULL,
    option4 VARCHAR(200) NOT NULL,
    correct_option INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (quiz_id) REFERENCES quiz (id)
)
''')

# Score table
cursor.execute('''
CREATE TABLE score (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    quiz_id INTEGER NOT NULL,
    score INTEGER NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    total_questions INTEGER NOT NULL,
    correct_answers INTEGER NOT NULL,
    time_taken INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES user (id),
    FOREIGN KEY (quiz_id) REFERENCES quiz (id)
)
''')

print("Tables created successfully.")

# Function to create a date in ISO format with random offset
def random_date(start_days=30, end_days=0):
    """Generate a random date within the range"""
    now = datetime.now()
    offset = random.randint(end_days, start_days)
    random_date = now - timedelta(days=offset)
    return random_date.strftime('%Y-%m-%d %H:%M:%S')

# Function to generate a password hash
def hash_password(password):
    return generate_password_hash(password)

# Create admin users with professional-looking IDs
admin_users = [
    (generate_id('user', 0), 'admin', hash_password('admin123'), 'Admin User', 'admin@quizmaster.com', 'System Administrator', '1980-01-01', 1, datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
    (generate_id('user', 1), 'john_admin', hash_password('john123'), 'John Smith', 'john.smith@quizmaster.com', 'Content Manager', '1985-05-15', 1, random_date())
]

# Insert admin users
cursor.executemany('''
INSERT INTO user (id, username, password_hash, full_name, email, qualification, date_of_birth, is_admin, created_at)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
''', admin_users)

# Create regular users with professional-looking IDs
regular_users = []
for i in range(1, 21):
    first_name = fake.first_name()
    last_name = fake.last_name()
    username = f"{first_name.lower()}_{last_name.lower()}{random.randint(1, 99)}"
    email = f"{first_name.lower()}.{last_name.lower()}@{fake.free_email_domain()}"
    full_name = f"{first_name} {last_name}"
    qualification = random.choice(['High School', 'Bachelor', 'Master', 'PhD', 'Student', None])
    birth_year = random.randint(1970, 2005)
    date_of_birth = f"{birth_year}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}"
    created_at = random_date()
    
    regular_users.append((
        generate_id('user', i + 1),  # Generate user ID
        username, hash_password('password123'), full_name, email, 
        qualification, date_of_birth, 0, created_at
    ))

# Insert regular users
cursor.executemany('''
INSERT INTO user (id, username, password_hash, full_name, email, qualification, date_of_birth, is_admin, created_at)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
''', regular_users)

print(f"Created {len(admin_users)} admin users and {len(regular_users)} regular users.")

# Create subjects with professional-looking IDs
subjects = [
    (generate_id('subject', 0), 'Mathematics', 'Study of numbers, quantities, shapes, and patterns.', random_date()),
    (generate_id('subject', 1), 'Science', 'Study of the natural world through observation and experimentation.', random_date()),
    (generate_id('subject', 2), 'History', 'Study of past events, societies, and civilizations.', random_date()),
    (generate_id('subject', 3), 'English Literature', 'Study of literary works in the English language.', random_date()),
    (generate_id('subject', 4), 'Computer Science', 'Study of computers and computational systems.', random_date())
]

# Insert subjects
cursor.executemany('''
INSERT INTO subject (id, name, description, created_at)
VALUES (?, ?, ?, ?)
''', subjects)

# Create chapters for each subject with professional-looking IDs
chapters = []

# Math chapters
math_chapters = [
    (generate_id('chapter', 0), 'Algebra', 'Study of symbols and the rules for manipulating those symbols.', subjects[0][0], random_date()),
    (generate_id('chapter', 1), 'Geometry', 'Study of shapes, sizes, and properties of space.', subjects[0][0], random_date()),
    (generate_id('chapter', 2), 'Calculus', 'Study of continuous change and its applications.', subjects[0][0], random_date()),
    (generate_id('chapter', 3), 'Statistics', 'Study of the collection, analysis, interpretation, and presentation of data.', subjects[0][0], random_date())
]
chapters.extend(math_chapters)

# Science chapters
science_chapters = [
    (generate_id('chapter', 4), 'Biology', 'Study of living organisms and their interactions.', subjects[1][0], random_date()),
    (generate_id('chapter', 5), 'Chemistry', 'Study of matter, its properties, and reactions.', subjects[1][0], random_date()),
    (generate_id('chapter', 6), 'Physics', 'Study of matter, energy, and their interactions.', subjects[1][0], random_date()),
    (generate_id('chapter', 7), 'Astronomy', 'Study of celestial objects and phenomena.', subjects[1][0], random_date())
]
chapters.extend(science_chapters)

# History chapters
history_chapters = [
    (generate_id('chapter', 8), 'Ancient History', 'History of early civilizations and empires.', subjects[2][0], random_date()),
    (generate_id('chapter', 9), 'Medieval History', 'History of the Middle Ages.', subjects[2][0], random_date()),
    (generate_id('chapter', 10), 'Modern History', 'History from the Renaissance to present day.', subjects[2][0], random_date()),
    (generate_id('chapter', 11), 'World Wars', 'History of the First and Second World Wars.', subjects[2][0], random_date())
]
chapters.extend(history_chapters)

# English chapters
english_chapters = [
    (generate_id('chapter', 12), 'Poetry', 'Study of poetic forms and notable poets.', subjects[3][0], random_date()),
    (generate_id('chapter', 13), 'Novels', 'Study of long prose narratives.', subjects[3][0], random_date()),
    (generate_id('chapter', 14), 'Drama', 'Study of plays and theatrical works.', subjects[3][0], random_date()),
    (generate_id('chapter', 15), 'Literary Criticism', 'Analysis and interpretation of literary works.', subjects[3][0], random_date())
]
chapters.extend(english_chapters)

# Computer Science chapters
cs_chapters = [
    (generate_id('chapter', 16), 'Programming Basics', 'Introduction to programming concepts and syntax.', subjects[4][0], random_date()),
    (generate_id('chapter', 17), 'Data Structures', 'Study of organizing and storing data.', subjects[4][0], random_date()),
    (generate_id('chapter', 18), 'Algorithms', 'Study of problem-solving methods and their efficiency.', subjects[4][0], random_date()),
    (generate_id('chapter', 19), 'Web Development', 'Creating applications for the World Wide Web.', subjects[4][0], random_date())
]
chapters.extend(cs_chapters)

# Insert chapters
cursor.executemany('''
INSERT INTO chapter (id, name, description, subject_id, created_at)
VALUES (?, ?, ?, ?, ?)
''', chapters)

print(f"Created {len(subjects)} subjects and {len(chapters)} chapters.")

# Create quizzes for each chapter with professional-looking IDs
quizzes = []
now = datetime.now()
quiz_index = 0

for chapter in chapters:
    chapter_id = chapter[0]
    chapter_name = chapter[1]
    
    # Create 1-3 quizzes per chapter
    for i in range(random.randint(1, 3)):
        # Random quiz properties
        quiz_date = now + timedelta(days=random.randint(1, 30))
        duration = random.choice([15, 30, 45, 60, 90])
        created_date = random_date(60, 10)
        
        title = f"{chapter_name} Quiz {i+1}"
        description = f"Test your knowledge of {chapter_name} with this comprehensive quiz."
        remarks = random.choice([
            "Focus on core concepts",
            "Advanced level questions included",
            "Review basic principles before attempting",
            "Time management is critical",
            None
        ])
        
        quizzes.append((
            generate_id('quiz', quiz_index),  # Generate quiz ID
            title, description, chapter_id, duration,
            quiz_date.strftime('%Y-%m-%d %H:%M:%S'),
            remarks, created_date
        ))
        quiz_index += 1

# Insert quizzes
cursor.executemany('''
INSERT INTO quiz (id, title, description, chapter_id, duration, date_of_quiz, remarks, created_at)
VALUES (?, ?, ?, ?, ?, ?, ?, ?)
''', quizzes)

print(f"Created {len(quizzes)} quizzes.")

# Create questions for each quiz with professional-looking IDs
questions = []
question_index = 0

# Sample question templates for different subjects
math_questions = [
    ("What is the value of x in the equation 2x + 5 = 15?", "5", "6", "7", "8", 1),
    ("If a triangle has angles of 30° and 60°, what is the measure of the third angle?", "90°", "60°", "45°", "30°", 1),
    ("What is the derivative of f(x) = x²?", "2x", "x²", "2", "x", 1),
    ("What is the mean of the numbers 5, 7, 9, 11, and 13?", "9", "8", "10", "11", 1),
    ("Solve for x: 3x - 7 = 8", "5", "15/3", "3", "7", 1),
    ("What is the area of a circle with radius 4?", "16π", "8π", "4π", "π/4", 1),
    ("What is the limit of (x² - 1)/(x - 1) as x approaches 1?", "2", "0", "1", "Undefined", 1),
    ("If P(A) = 0.3 and P(B) = 0.5, and A and B are independent events, what is P(A and B)?", "0.15", "0.8", "0.35", "0.2", 1)
]

science_questions = [
    ("What is the chemical symbol for gold?", "Au", "Ag", "Fe", "Cu", 1),
    ("Which organelle is responsible for photosynthesis in plant cells?", "Chloroplast", "Mitochondria", "Nucleus", "Ribosome", 1),
    ("What is Newton's Second Law of Motion?", "F = ma", "E = mc²", "F = G(m₁m₂)/r²", "v = u + at", 1),
    ("What planet is known as the 'Red Planet'?", "Mars", "Jupiter", "Venus", "Mercury", 1),
    ("What is the scientific name for the process of cells dividing?", "Mitosis", "Meiosis", "Diffusion", "Osmosis", 1),
    ("What is the chemical formula for water?", "H₂O", "CO₂", "NaCl", "O₂", 1),
    ("Which law of thermodynamics states that energy cannot be created or destroyed?", "First law", "Second law", "Third law", "Zeroth law", 1),
    ("What force keeps planets orbiting around the sun?", "Gravity", "Magnetism", "Friction", "Tension", 1)
]

history_questions = [
    ("In what year did World War II end?", "1945", "1939", "1941", "1950", 1),
    ("Who was the first Emperor of Rome?", "Augustus", "Julius Caesar", "Nero", "Constantine", 1),
    ("What event marked the beginning of World War I?", "Assassination of Archduke Franz Ferdinand", "Treaty of Versailles", "German invasion of Poland", "Russian Revolution", 1),
    ("Which civilization built the Machu Picchu?", "Incas", "Aztecs", "Mayans", "Olmecs", 1),
    ("Who wrote the 'I Have a Dream' speech?", "Martin Luther King Jr.", "Malcolm X", "Abraham Lincoln", "John F. Kennedy", 1),
    ("In what year did the Berlin Wall fall?", "1989", "1991", "1987", "1985", 1),
    ("Which ancient civilization built the pyramids at Giza?", "Egyptians", "Greeks", "Romans", "Persians", 1),
    ("Who was the first female Prime Minister of the United Kingdom?", "Margaret Thatcher", "Theresa May", "Queen Elizabeth II", "Queen Victoria", 1)
]

english_questions = [
    ("Who wrote 'Romeo and Juliet'?", "William Shakespeare", "Charles Dickens", "Jane Austen", "Mark Twain", 1),
    ("What figure of speech compares two things using 'like' or 'as'?", "Simile", "Metaphor", "Personification", "Hyperbole", 1),
    ("Which novel begins with the line 'It was the best of times, it was the worst of times'?", "A Tale of Two Cities", "Great Expectations", "Oliver Twist", "David Copperfield", 1),
    ("What is the main theme of George Orwell's '1984'?", "Totalitarianism", "Love", "War", "Friendship", 1),
    ("Who is the author of 'Pride and Prejudice'?", "Jane Austen", "Emily Brontë", "Charlotte Brontë", "Virginia Woolf", 1),
    ("What is the term for a word that imitates the sound it represents?", "Onomatopoeia", "Alliteration", "Assonance", "Consonance", 1),
    ("Who wrote 'The Great Gatsby'?", "F. Scott Fitzgerald", "Ernest Hemingway", "John Steinbeck", "William Faulkner", 1),
    ("What literary device is used when an author gives human characteristics to non-human objects?", "Personification", "Simile", "Metaphor", "Allegory", 1)
]

cs_questions = [
    ("What does HTML stand for?", "Hypertext Markup Language", "Hypertext Machine Language", "Hypertext Marking Logic", "High-Tech Markup Language", 1),
    ("Which data structure operates on a LIFO principle?", "Stack", "Queue", "Linked List", "Tree", 1),
    ("What is the time complexity of binary search?", "O(log n)", "O(n)", "O(n²)", "O(1)", 1),
    ("Which of these is not a programming paradigm?", "Sequential Programming", "Object-Oriented Programming", "Functional Programming", "Procedural Programming", 1),
    ("What does SQL stand for?", "Structured Query Language", "Simple Query Language", "Standardized Question Language", "System Query Language", 1),
    ("Which sorting algorithm has the worst-case time complexity of O(n²)?", "Bubble Sort", "Merge Sort", "Heap Sort", "Quick Sort", 1),
    ("What is the purpose of the 'git clone' command?", "Create a copy of a repository", "Create a new branch", "Merge branches", "Push changes to a repository", 1),
    ("Which of these is not a JavaScript framework?", "Django", "React", "Angular", "Vue", 1)
]

# Function to get appropriate questions based on chapter name
def get_questions_for_chapter(chapter_name):
    if any(keyword in chapter_name.lower() for keyword in ['algebra', 'geometry', 'calculus', 'statistics']):
        return math_questions
    elif any(keyword in chapter_name.lower() for keyword in ['biology', 'chemistry', 'physics', 'astronomy']):
        return science_questions
    elif any(keyword in chapter_name.lower() for keyword in ['history', 'ancient', 'medieval', 'modern', 'wars']):
        return history_questions
    elif any(keyword in chapter_name.lower() for keyword in ['poetry', 'novels', 'drama', 'literary']):
        return english_questions
    elif any(keyword in chapter_name.lower() for keyword in ['programming', 'data', 'algorithms', 'web']):
        return cs_questions
    else:
        # Default to a mixed set
        return math_questions + science_questions + history_questions + english_questions + cs_questions

# Create quiz questions
for quiz in quizzes:
    quiz_id = quiz[0]
    
    # Get the chapter name for this quiz
    for chapter in chapters:
        if chapter[0] == quiz[3]:  # quiz[3] is chapter_id
            chapter_name = chapter[1]
            break
    
    # Get appropriate question set
    question_set = get_questions_for_chapter(chapter_name)
    
    # Create 5-10 questions per quiz
    num_questions = random.randint(5, 10)
    selected_questions = random.sample(question_set, min(num_questions, len(question_set)))
    
    # If we need more questions than in our template set, add some generic ones
    if num_questions > len(selected_questions):
        for i in range(len(selected_questions), num_questions):
            question_text = f"Question {i+1} for this quiz on {chapter_name}"
            selected_questions.append((
                question_text,
                f"Option A for {question_text}",
                f"Option B for {question_text}",
                f"Option C for {question_text}",
                f"Option D for {question_text}",
                random.randint(1, 4)
            ))
    
    # Add quiz_id and created_at to each question
    for q in selected_questions:
        question_data = (
            generate_id('question', question_index),  # Generate question ID
            quiz_id, q[0], q[1], q[2], q[3], q[4], q[5], random_date()
        )
        questions.append(question_data)
        question_index += 1

# Insert questions
cursor.executemany('''
INSERT INTO question (id, quiz_id, question_text, option1, option2, option3, option4, correct_option, created_at)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
''', questions)

print(f"Created {len(questions)} questions across all quizzes.")

# Create scores (quiz attempts) for users with professional-looking IDs
scores = []
score_index = 0

# Get all regular user IDs
user_ids = [user[0] for user in regular_users]

# Generate random scores
for quiz in quizzes:
    quiz_id = quiz[0]
    
    # Get the number of questions for this quiz
    cursor.execute("SELECT COUNT(*) FROM question WHERE quiz_id = ?", (quiz_id,))
    num_questions = cursor.fetchone()[0]
    
    # Determine how many users have taken this quiz (30-80% of users)
    num_takers = int(len(user_ids) * random.uniform(0.3, 0.8))
    takers = random.sample(user_ids, num_takers)
    
    for user_id in takers:
        # Calculate random score
        correct_answers = random.randint(0, num_questions)
        score_value = int((correct_answers / num_questions) * 100)
        
        # Random time taken (30 seconds to 2 minutes per question)
        time_taken = correct_answers * random.randint(30, 120)
        
        # Random timestamp within the last 30 days
        timestamp = random_date(30, 0)
        
        scores.append((
            generate_id('score', score_index),  # Generate score ID
            user_id, quiz_id, score_value, timestamp,
            num_questions, correct_answers, time_taken
        ))
        score_index += 1

# Insert scores
cursor.executemany('''
INSERT INTO score (id, user_id, quiz_id, score, timestamp, total_questions, correct_answers, time_taken)
VALUES (?, ?, ?, ?, ?, ?, ?, ?)
''', scores)

print(f"Created {len(scores)} quiz scores for {len(user_ids)} users.")

# Create SQLite sequence entries for auto-increment
if DISABLE_AUTOINCREMENT:
    try:
        # Check if sqlite_sequence table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sqlite_sequence'")
        if not cursor.fetchone():
            # If the table doesn't exist, we don't need to do anything
            # SQLite will create it automatically when needed
            pass
        
        # Update sequences to be higher than our manual IDs
        for table, ids in used_ids.items():
            if ids:
                max_id = max(ids)
                try:
                    cursor.execute(f"UPDATE sqlite_sequence SET seq = {max_id} WHERE name = '{table}'")
                except sqlite3.Error as e:
                    print(f"Warning: Could not update sequence for {table}: {e}")
    except sqlite3.Error as e:
        print(f"Warning: Error handling sqlite_sequence: {e}")
        print("This is not critical and auto-increment should still work.")

# Commit changes and close the connection
conn.commit()
conn.close()

print(f"Database {DB_FILE} created successfully with mock data.")
print("All IDs use professional-looking conventions (e.g., 1032 instead of 1, 2, 3).")
print("You can now use this database for testing.") 