#!/usr/bin/env python3
"""
Script to check the IDs in the mock_quizmaster.db database.
This script will display sample IDs from each table to verify they follow
the professional-looking convention.
"""

import sqlite3
import os

DB_FILE = 'mock_quizmaster.db'

def check_database_ids():
    """Check the IDs in the database and print results"""
    if not os.path.exists(DB_FILE):
        print(f"Database file {DB_FILE} not found!")
        return
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    tables = ['user', 'subject', 'chapter', 'quiz', 'question', 'score']
    
    print("=" * 60)
    print(f"ID ranges in database: {DB_FILE}")
    print("=" * 60)
    
    for table in tables:
        # Get count of entries
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        
        # Get sample IDs
        cursor.execute(f"SELECT id FROM {table} ORDER BY id LIMIT 5")
        sample_ids = [row[0] for row in cursor.fetchall()]
        
        # Get min and max IDs
        cursor.execute(f"SELECT MIN(id), MAX(id) FROM {table}")
        min_id, max_id = cursor.fetchone()
        
        print(f"{table.capitalize()} table:")
        print(f"  - Total records: {count}")
        print(f"  - ID range: {min_id} to {max_id}")
        print(f"  - Sample IDs: {sample_ids}")
        print()
    
    # Check relationships
    print("Checking relationships:")
    
    # Chapter to Subject
    cursor.execute("""
        SELECT c.id, c.name, s.id, s.name 
        FROM chapter c 
        JOIN subject s ON c.subject_id = s.id 
        LIMIT 3
    """)
    relationships = cursor.fetchall()
    print("Sample Chapter-Subject relationships:")
    for row in relationships:
        print(f"  Chapter ID {row[0]} ({row[1]}) belongs to Subject ID {row[2]} ({row[3]})")
    
    # Quiz to Chapter
    cursor.execute("""
        SELECT q.id, q.title, c.id, c.name 
        FROM quiz q 
        JOIN chapter c ON q.chapter_id = c.id 
        LIMIT 3
    """)
    relationships = cursor.fetchall()
    print("\nSample Quiz-Chapter relationships:")
    for row in relationships:
        print(f"  Quiz ID {row[0]} ({row[1]}) belongs to Chapter ID {row[2]} ({row[3]})")
    
    # Question to Quiz
    cursor.execute("""
        SELECT qn.id, q.id, q.title 
        FROM question qn 
        JOIN quiz q ON qn.quiz_id = q.id 
        LIMIT 3
    """)
    relationships = cursor.fetchall()
    print("\nSample Question-Quiz relationships:")
    for row in relationships:
        print(f"  Question ID {row[0]} belongs to Quiz ID {row[1]} ({row[2]})")
    
    # Score to User and Quiz
    cursor.execute("""
        SELECT s.id, u.id, u.username, q.id, q.title 
        FROM score s 
        JOIN user u ON s.user_id = u.id 
        JOIN quiz q ON s.quiz_id = q.id 
        LIMIT 3
    """)
    relationships = cursor.fetchall()
    print("\nSample Score-User-Quiz relationships:")
    for row in relationships:
        print(f"  Score ID {row[0]} links User ID {row[1]} ({row[2]}) to Quiz ID {row[3]} ({row[4]})")
    
    print("\nSequence Values:")
    try:
        cursor.execute("SELECT name, seq FROM sqlite_sequence")
        sequences = cursor.fetchall()
        for row in sequences:
            print(f"  {row[0]}: {row[1]}")
    except sqlite3.Error as e:
        print(f"  No sequence values found: {e}")
        print("  This is normal for databases with manually assigned IDs.")
    
    conn.close()
    print("\nDatabase ID check complete.")

if __name__ == "__main__":
    check_database_ids() 