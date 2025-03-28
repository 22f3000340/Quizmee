#!/usr/bin/env python3
"""
Script to update an existing database with professional-looking IDs.
This script will create a backup of the original database, then update
all IDs to follow a professional convention.

WARNING: This script modifies the database in place. Back up your data first!
"""

import os
import sys
import sqlite3
import shutil
import random
from datetime import datetime

# Default to quizmaster.db, but allow overriding
DB_FILE = sys.argv[1] if len(sys.argv) > 1 else 'quizmaster.db'
BACKUP_FILE = f"{DB_FILE}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

# ID ranges for different entity types (same as in utils.py)
ID_RANGES = {
    'user': (1000, 9999),     # 1000-9999
    'subject': (10000, 19999), # 10000-19999
    'chapter': (20000, 29999), # 20000-29999
    'quiz': (30000, 39999),    # 30000-39999
    'question': (40000, 49999), # 40000-49999
    'score': (50000, 59999)    # 50000-59999
}

def generate_id(entity_type, index=0):
    """Generate a professional-looking ID for an entity"""
    min_id, max_id = ID_RANGES[entity_type]
    # Create a gap between IDs for more realistic look
    return min_id + index * random.randint(5, 20)

def update_database():
    """Update the database with professional-looking IDs"""
    if not os.path.exists(DB_FILE):
        print(f"Database file {DB_FILE} not found!")
        return
    
    # Create a backup
    print(f"Creating backup to {BACKUP_FILE}...")
    shutil.copy2(DB_FILE, BACKUP_FILE)
    print(f"Backup created.")
    
    # Connect to the database
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Start a transaction
    conn.execute("BEGIN TRANSACTION")
    
    try:
        # Get all current IDs and create mapping to new IDs
        tables = ['user', 'subject', 'chapter', 'quiz', 'question', 'score']
        id_mappings = {}
        
        for table in tables:
            id_mappings[table] = {}
            
            # Get existing IDs
            cursor.execute(f"SELECT id FROM {table} ORDER BY id")
            old_ids = [row[0] for row in cursor.fetchall()]
            
            # Create mapping to new IDs
            for i, old_id in enumerate(old_ids):
                new_id = generate_id(table, i)
                id_mappings[table][old_id] = new_id
        
        # Temporarily disable foreign key constraints
        cursor.execute("PRAGMA foreign_keys = OFF")
        
        print("Updating IDs in tables...")
        
        # For each table, create a temporary table, copy data with new IDs, then replace the original
        for table in tables:
            print(f"  Processing {table} table...")
            
            # Get table schema
            cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table}'")
            schema = cursor.fetchone()[0]
            
            # Create temp table
            cursor.execute(f"CREATE TABLE {table}_temp AS SELECT * FROM {table} WHERE 0")
            
            # Get column names
            cursor.execute(f"PRAGMA table_info({table})")
            columns = [row[1] for row in cursor.fetchall()]
            column_names = ', '.join(columns)
            placeholders = ', '.join(['?'] * len(columns))
            
            # Get all rows
            cursor.execute(f"SELECT * FROM {table}")
            rows = cursor.fetchall()
            
            # Insert into temp table with new IDs
            new_rows = []
            for row in rows:
                row_list = list(row)
                old_id = row_list[0]
                row_list[0] = id_mappings[table][old_id]
                
                # Update foreign keys
                if table == 'chapter':
                    subject_fk_index = columns.index('subject_id')
                    old_subject_id = row_list[subject_fk_index]
                    row_list[subject_fk_index] = id_mappings['subject'][old_subject_id]
                    
                elif table == 'quiz':
                    chapter_fk_index = columns.index('chapter_id')
                    old_chapter_id = row_list[chapter_fk_index]
                    row_list[chapter_fk_index] = id_mappings['chapter'][old_chapter_id]
                    
                elif table == 'question':
                    quiz_fk_index = columns.index('quiz_id')
                    old_quiz_id = row_list[quiz_fk_index]
                    row_list[quiz_fk_index] = id_mappings['quiz'][old_quiz_id]
                    
                elif table == 'score':
                    user_fk_index = columns.index('user_id')
                    quiz_fk_index = columns.index('quiz_id')
                    old_user_id = row_list[user_fk_index]
                    old_quiz_id = row_list[quiz_fk_index]
                    row_list[user_fk_index] = id_mappings['user'][old_user_id]
                    row_list[quiz_fk_index] = id_mappings['quiz'][old_quiz_id]
                
                new_rows.append(tuple(row_list))
            
            # Insert new rows
            cursor.executemany(f"INSERT INTO {table}_temp VALUES ({placeholders})", new_rows)
            
            # Drop original table and rename temp table
            cursor.execute(f"DROP TABLE {table}")
            cursor.execute(f"ALTER TABLE {table}_temp RENAME TO {table}")
            
            # Update sequence
            max_id = max(id_mappings[table].values())
            cursor.execute(f"INSERT OR REPLACE INTO sqlite_sequence (name, seq) VALUES ('{table}', {max_id})")
        
        # Re-enable foreign key constraints
        cursor.execute("PRAGMA foreign_keys = ON")
        
        # Commit the transaction
        conn.commit()
        print("Database updated successfully with professional-looking IDs.")
        
    except Exception as e:
        # Roll back any changes if something went wrong
        conn.rollback()
        print(f"Error updating database: {e}")
        print(f"Database restored to original state. Original backup is still at {BACKUP_FILE}")
    
    conn.close()

if __name__ == "__main__":
    print(f"This script will update IDs in {DB_FILE} to use professional-looking conventions.")
    print(f"A backup will be created at {BACKUP_FILE}.")
    choice = input("Do you want to continue? (y/n): ")
    if choice.lower() == 'y':
        update_database()
    else:
        print("Operation cancelled.") 