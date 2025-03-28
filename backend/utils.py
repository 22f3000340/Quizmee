"""
Utility functions for the QuizMaster application.
"""
import random
import time

# ID ranges for different entity types
ID_RANGES = {
    'user': (1000, 9999),     # 1000-9999
    'subject': (10000, 19999), # 10000-19999
    'chapter': (20000, 29999), # 20000-29999
    'quiz': (30000, 39999),    # 30000-39999
    'question': (40000, 49999), # 40000-49999
    'score': (50000, 59999)    # 50000-59999
}

def generate_id(entity_type, previous_id=None):
    """
    Generate a professional-looking ID for the given entity type.
    
    Args:
        entity_type (str): The type of entity ('user', 'subject', etc.)
        previous_id (int, optional): The previous highest ID used
    
    Returns:
        int: A new ID in the appropriate range for the entity type
    """
    if entity_type not in ID_RANGES:
        raise ValueError(f"Unknown entity type: {entity_type}")
    
    min_id, max_id = ID_RANGES[entity_type]
    
    if previous_id is None:
        # Start with lowest ID in range + random offset
        return min_id + random.randint(0, 99)
    else:
        # Ensure the new ID is higher than the previous one
        new_id = previous_id + random.randint(1, 10)
        return min_id if new_id > max_id else new_id

def get_next_id(session, model, entity_type):
    """
    Get the next ID for a given model type.
    
    Args:
        session: SQLAlchemy session
        model: SQLAlchemy model class
        entity_type (str): Entity type for ID range
    
    Returns:
        int: Next available ID
    """
    min_id, max_id = ID_RANGES[entity_type]
    
    # Get the current highest ID
    highest = session.query(model).order_by(model.id.desc()).first()
    highest_id = highest.id if highest else None
    
    # Start with an ID higher than the highest existing ID
    next_id = highest_id + random.randint(10, 50) if highest_id else min_id + random.randint(0, 99)
    
    # Make sure the ID is within the valid range
    if next_id > max_id:
        # If we've reached max ID, restart from the beginning with a random offset
        next_id = min_id + random.randint(0, 99)
        
    # Check if the generated ID already exists
    attempts = 0
    max_attempts = 100  # Prevent infinite loops
    
    while session.query(model).filter(model.id == next_id).first() is not None:
        # ID exists, try another one with a larger increment
        next_id += random.randint(1, 100)
        
        # Make sure the ID is within the valid range
        if next_id > max_id:
            next_id = min_id + random.randint(0, 999)
            
        attempts += 1
        if attempts > max_attempts:
            raise ValueError(f"Could not find an available ID for {entity_type} after {max_attempts} attempts")
    
    # Return the guaranteed unique ID
    return next_id

def ensure_id_sequence(session, model, entity_type):
    """
    Ensure the SQLite sequence for the table is set correctly.
    Call this after manually setting an ID to make sure auto-increment works.
    
    Args:
        session: SQLAlchemy session
        model: SQLAlchemy model class
        entity_type (str): Entity type for ID range
    """
    try:
        # First check if sqlite_sequence table exists
        result = session.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sqlite_sequence'").fetchone()
        
        # If table doesn't exist, no need to update sequence
        if not result:
            print("sqlite_sequence table doesn't exist - skipping sequence update")
            return
            
        table_name = model.__tablename__
        
        # Get the current highest ID
        highest = session.query(model).order_by(model.id.desc()).first()
        if highest:
            # Set the SQLite sequence to be higher than the highest ID
            next_id = highest.id + 1
            session.execute(f"UPDATE sqlite_sequence SET seq = {next_id} WHERE name = '{table_name}'")
            session.commit()
    except Exception as e:
        print(f"Warning: Could not update sqlite_sequence: {str(e)}")
        print("This is not critical and the application will continue to function.") 