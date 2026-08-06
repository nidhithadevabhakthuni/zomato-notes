from sqlalchemy.orm import Session
from sqlalchemy import text
from models import User, Note
from schemas import UserCreate, NoteCreate, NoteUpdate
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

# User CRUD
def create_user(db: Session, user: UserCreate):
    db_user = User(name=user.name, email=user.email, password=user.password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

# Note CRUD
def create_note(db: Session, note: NoteCreate):
    db_note = Note(
        title=note.title,
        content=note.content,
        tag=note.tag,
        owner_id=note.owner_id
    )
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note

def get_notes(db: Session, tag: str = None):
    query = db.query(Note)
    if tag:
        query = query.filter(Note.tag == tag)
    return query.all()

def get_note(db: Session, note_id: int):
    return db.query(Note).filter(Note.id == note_id).first()

def update_note(db: Session, note_id: int, note_update: NoteUpdate):
    db_note = get_note(db, note_id)
    if db_note:
        update_data = note_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_note, key, value)
        db.commit()
        db.refresh(db_note)
    return db_note

def delete_note(db: Session, note_id: int):
    db_note = get_note(db, note_id)
    if db_note:
        db.delete(db_note)
        db.commit()
        return True
    return False

# Reports with raw SQL
def get_tag_summary(db: Session):
    sql = text("""
        SELECT tag, COUNT(*) as count 
        FROM notes 
        GROUP BY tag 
        HAVING COUNT(*) > 1
    """)
    return db.execute(sql).fetchall()

def get_long_notes(db: Session):
    sql = text("""
        SELECT * 
        FROM notes 
        WHERE LENGTH(content) > (SELECT AVG(LENGTH(content)) FROM notes)
    """)
    return db.execute(sql).fetchall()

def get_user_notes_count(db: Session):
    sql = text("""
        SELECT u.id as user_id, u.name as user_name, COUNT(n.id) as note_count
        FROM users u
        LEFT JOIN notes n ON u.id = n.owner_id
        GROUP BY u.id, u.name
    """)
    return db.execute(sql).fetchall()