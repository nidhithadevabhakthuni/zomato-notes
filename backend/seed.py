import os
import sys
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, engine, SessionLocal
from models import User, Note
from ranking_dataset import RANKING_DATASET
from ai_sample_notes import AI_SAMPLE_NOTES
import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Seed data from part 1
SEED_USERS = [
    {"id": 1, "name": "Alice", "email": "alice@example.com", "password": "alicepass123"},
    {"id": 2, "name": "Bob", "email": "bob@example.com", "password": "bobpass123"},
]

SEED_NOTES = [
    {"id": 1, "owner_id": 1, "title": "Standup Summary", "tag": "work",
     "content": "Discussed sprint progress, blockers on the payments API integration, and the plan for the demo on Friday."},
    {"id": 2, "owner_id": 1, "title": "Sprint Retro Notes", "tag": "work",
     "content": "Retro highlighted communication gaps between frontend and backend teams and agreed on daily syncs going forward."},
    {"id": 3, "owner_id": 2, "title": "One on One", "tag": "work",
     "content": "Quick check-in, no blockers, discussed career growth goals for next quarter."},
    {"id": 4, "owner_id": 1, "title": "Morning Run", "tag": "health",
     "content": "Ran 5km along the river trail before breakfast, felt great."},
    {"id": 5, "owner_id": 2, "title": "Doctor Visit", "tag": "health",
     "content": "Annual checkup went well, blood pressure normal, scheduled next visit in six months."},
    {"id": 6, "owner_id": 1, "title": "Pasta Recipe", "tag": "recipes",
     "content": "Boil pasta, saute garlic in olive oil, add tomatoes, basil, and a pinch of chili flakes."},
    {"id": 7, "owner_id": 2, "title": "Smoothie Recipe", "tag": "recipes",
     "content": "Blend banana, spinach, almond milk, and a spoon of peanut butter for breakfast."},
    {"id": 8, "owner_id": 1, "title": "Flight Booking", "tag": "travel",
     "content": "Booked a round trip flight for the December vacation, window seat confirmed."},
    {"id": 9, "owner_id": 2, "title": "Random Thought", "tag": "random",
     "content": "Maybe the library needs a better recommendation system based on reading history."},
    {"id": 10, "owner_id": 1, "title": "Quote To Remember", "tag": "random",
     "content": "Done is better than perfect, keep shipping."},
]

def seed_database():
    """Seed the database with initial data."""
    logger.info("Creating tables...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Clear existing data
        logger.info("Clearing existing data...")
        db.query(Note).delete()
        db.query(User).delete()
        db.commit()
        
        # Seed users
        logger.info("Seeding users...")
        for user_data in SEED_USERS:
            user = User(**user_data)
            db.add(user)
        db.commit()
        
        # Seed notes
        logger.info("Seeding notes...")
        for note_data in SEED_NOTES:
            note = Note(**note_data)
            db.add(note)
        db.commit()
        
        # Seed ranking dataset
        logger.info("Seeding ranking dataset...")
        for note_data in RANKING_DATASET:
            # Remove id and let DB auto-generate
            note_data_copy = note_data.copy()
            note_data_copy.pop('id', None)
            note = Note(**note_data_copy)
            db.add(note)
        db.commit()
        
        # Seed AI sample notes
        logger.info("Seeding AI sample notes...")
        for note_data in AI_SAMPLE_NOTES:
            note_data_copy = note_data.copy()
            note_data_copy.pop('id', None)
            note = Note(**note_data_copy)
            db.add(note)
        db.commit()
        
        logger.info("Database seeded successfully!")
        
        # Print summary
        users = db.query(User).all()
        notes = db.query(Note).all()
        logger.info(f"Created {len(users)} users and {len(notes)} notes")
        
    except Exception as e:
        logger.error(f"Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()