from fastapi import FastAPI, Depends, HTTPException, status, BackgroundTasks, UploadFile, File, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import time
import logging
import json
from datetime import datetime
import os
from dotenv import load_dotenv

from database import get_db, engine, Base
from models import User, Note
from schemas import (
    UserCreate, UserResponse, NoteCreate, NoteUpdate, 
    NoteResponse, NoteWithAIResponse, TagSummaryResponse,
    UserNoteCountResponse
)
from crud import (
    create_user, get_user_by_email, get_user_by_id,
    create_note as crud_create_note,
    get_notes, get_note, update_note, delete_note,
    get_tag_summary, get_long_notes, get_user_notes_count
)
from algorithms import (
    insertion_sort_by_key, binary_search_iterative,
    binary_search_recursive, linear_search
)
from ai_service import generate_ai_suggestion
from semantic_search import semantic_search

load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Zomato Notes API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500", "http://localhost:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom process time middleware
@app.middleware("http")
async def add_process_time_header(request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Health check
@app.get("/")
def read_root():
    return {"message": "Zomato Notes API", "status": "running"}

# ============ USER ENDPOINTS ============

@app.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user_endpoint(user: UserCreate, db: Session = Depends(get_db)):
    """Create a new user."""
    # Check if email already exists
    existing_user = get_user_by_email(db, user.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    return create_user(db, user)

# ============ NOTE ENDPOINTS ============

@app.post("/notes", response_model=NoteWithAIResponse, status_code=status.HTTP_201_CREATED)
async def create_note_endpoint(
    note: NoteCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Create a new note."""
    # Verify owner exists
    user = get_user_by_id(db, note.owner_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {note.owner_id} not found"
        )
    
    # Create the note
    db_note = crud_create_note(db, note)
    
    # Generate AI suggestion in background (but we need it for response)
    # We'll do it synchronously since the response needs it
    ai_suggestion = generate_ai_suggestion(note.content)
    
    # Add background task for indexing simulation
    background_tasks.add_task(simulate_indexing, db_note.id)
    
    # Create response with AI suggestion
    response = NoteWithAIResponse.model_validate(db_note)
    response.ai_suggestion = ai_suggestion
    
    return response

def simulate_indexing(note_id: int):
    """Simulate background indexing task."""
    time.sleep(2)  # Simulate 2-3 second delay
    logger.info(f"Background indexing completed for note {note_id}")

@app.get("/notes", response_model=List[NoteResponse])
def get_notes_endpoint(tag: Optional[str] = None, db: Session = Depends(get_db)):
    """Get all notes, optionally filtered by tag."""
    notes = get_notes(db, tag)
    return notes

@app.get("/notes/{note_id}", response_model=NoteResponse)
def get_note_endpoint(note_id: int, db: Session = Depends(get_db)):
    """Get a specific note by ID."""
    note = get_note(db, note_id)
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Note with id {note_id} not found"
        )
    return note

@app.put("/notes/{note_id}", response_model=NoteResponse)
def update_note_endpoint(
    note_id: int,
    note_update: NoteUpdate,
    db: Session = Depends(get_db)
):
    """Update a note."""
    updated_note = update_note(db, note_id, note_update)
    if not updated_note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Note with id {note_id} not found"
        )
    return updated_note

# Auth dependency for DELETE
def verify_token(x_token: str = Depends(lambda: None)):
    """Verify the x-token header."""
    # This is a lightweight auth-gate
    # In production, you'd use proper authentication
    # For this project, we check for a specific token
    return True

@app.delete("/notes/{note_id}")
def delete_note_endpoint(
    note_id: int,
    x_token: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Delete a note. Requires x-token header."""
    # Check for token
    if not x_token or x_token != "secret-token-123":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing authentication token"
        )
    
    success = delete_note(db, note_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Note with id {note_id} not found"
        )
    return {"message": "Note deleted successfully"}

# ============ BULK IMPORT ============

@app.post("/notes/import")
async def import_notes(
    file: UploadFile = File(...),
    owner_id: int = Query(..., description="Owner ID for all imported notes"),
    db: Session = Depends(get_db)
):
    """Import notes from a text file."""
    # Verify owner exists
    user = get_user_by_id(db, owner_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {owner_id} not found"
        )
    
    # Read and parse file
    content = await file.read()
    lines = content.decode('utf-8').splitlines()
    
    # Filter non-empty lines
    non_empty_lines = [line.strip() for line in lines if line.strip()]
    
    created_notes = []
    for line in non_empty_lines:
        # Each line becomes a note
        # Using line as content, and first few words as title
        words = line.split()
        title = ' '.join(words[:5]) if len(words) > 5 else line
        if len(title) > 120:
            title = title[:117] + '...'
        
        note_data = NoteCreate(
            title=title,
            content=line,
            tag="imported",
            owner_id=owner_id
        )
        db_note = crud_create_note(db, note_data)
        created_notes.append(db_note)
    
    return {
        "message": f"Successfully imported {len(created_notes)} notes",
        "count": len(created_notes)
    }
    
# ============ RANKING ENGINE ENDPOINTS  ============

@app.get("/notes/search")
def search_notes(
    keyword: Optional[str] = None,
    sort_by: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Search notes with ranking."""
    notes = get_notes(db)
    
    # Convert to list of dicts for algorithm processing
    notes_list = [
        {
            "id": note.id,
            "title": note.title,
            "content": note.content,
            "tag": note.tag,
            "owner_id": note.owner_id,
            "created_at": note.created_at
        }
        for note in notes
    ]
    
    if sort_by == "date":
        # Sort by creation time descending
        for note in notes_list:
            note["created_at_epoch"] = note["created_at"].timestamp()
        sorted_notes = insertion_sort_by_key(notes_list, "created_at_epoch")
        return sorted_notes[:5]  # Return top 5
    
    elif keyword:
        # Compute relevance score (keyword occurrence count)
        keyword_lower = keyword.lower()
        for note in notes_list:
            content_lower = note["content"].lower()
            note["score"] = content_lower.count(keyword_lower)
        
        sorted_notes = insertion_sort_by_key(notes_list, "score")
        return sorted_notes[:5]  # Return top 5
    
    return notes_list[:5]  # Return first 5 if no search params
    
@app.get("/notes/lookup")
def lookup_note_by_title(
    title: str,
    algo: str = "iterative",
    db: Session = Depends(get_db)
):
    """Look up a note by exact title using binary search."""
    # Get all notes sorted by title
    notes = db.query(Note).order_by(Note.title).all()
    titles = [note.title for note in notes]
    
    # Perform binary search
    if algo == "iterative":
        index = binary_search_iterative(titles, title)
    elif algo == "recursive":
        index = binary_search_recursive(titles, title, 0, len(titles) - 1)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="algo must be 'iterative' or 'recursive'"
        )
    
    if index == -1:
        return {"message": f"Note with title '{title}' not found", "found": False}
    
    note = notes[index]
    return {
        "found": True,
        "note": {
            "id": note.id,
            "title": note.title,
            "content": note.content,
            "tag": note.tag,
            "owner_id": note.owner_id,
            "created_at": note.created_at
        }
    }

@app.get("/notes/quick-find")
def quick_find_by_tag(
    tag: str,
    db: Session = Depends(get_db)
):
    """Find first note with a specific tag using linear search."""
    notes = get_notes(db)
    
    # Convert to list of dicts
    notes_list = [
        {
            "id": note.id,
            "title": note.title,
            "content": note.content,
            "tag": note.tag,
            "owner_id": note.owner_id,
            "created_at": note.created_at
        }
        for note in notes
    ]
    
    # Linear search
    result = linear_search(notes_list, "tag", tag)
    
    if result is None:
        return {"message": f"No note found with tag '{tag}'", "found": False}
    
    return {"found": True, "note": result}

# ============ SMART SEARCH (SEMANTIC) ============

@app.get("/notes/smart-search")
def smart_search(
    q: str = Query(..., description="Search query"),
    db: Session = Depends(get_db)
):
    """Semantic search using embeddings."""
    # Get AI sample notes (tag: ai-demo)
    notes = db.query(Note).filter(Note.tag == "ai-demo").all()
    
    if not notes:
        return {"message": "No notes found for semantic search", "results": []}
    
    # Convert to list of dicts
    notes_list = [
        {
            "id": note.id,
            "title": note.title,
            "content": note.content,
            "tag": note.tag,
            "owner_id": note.owner_id,
            "created_at": note.created_at
        }
        for note in notes
    ]
    
    # Perform semantic search
    results = semantic_search(q, notes_list, top_k=3)
    
    return {"query": q, "results": results}

# ============ REPORTING ENDPOINTS ============

@app.get("/reports/tag-summary", response_model=List[TagSummaryResponse])
def get_tag_summary_endpoint(db: Session = Depends(get_db)):
    """Get summary of tags with more than 1 note."""
    results = get_tag_summary(db)
    return [{"tag": row[0], "count": row[1]} for row in results]

@app.get("/reports/long-notes")
def get_long_notes_endpoint(db: Session = Depends(get_db)):
    """Get notes with content length above average."""
    results = get_long_notes(db)
    return [
        {
            "id": row.id,
            "title": row.title,
            "content": row.content,
            "tag": row.tag,
            "owner_id": row.owner_id,
            "created_at": row.created_at
        }
        for row in results
    ]

@app.get("/reports/user-notes", response_model=List[UserNoteCountResponse])
def get_user_notes_count_endpoint(db: Session = Depends(get_db)):
    """Get note count per user."""
    results = get_user_notes_count(db)
    return [
        {"user_id": row[0], "user_name": row[1], "note_count": row[2]}
        for row in results
    ]

# ============ SAMPLE .txt file content ============
# This would be in sample_import.txt in the root directory