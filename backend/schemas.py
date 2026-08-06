from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime
from typing import Optional, List

# User schemas
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str = Field(min_length=8)
    
    @field_validator('name')
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Name cannot be empty or whitespace only')
        return v.strip()

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# Note schemas
class NoteCreate(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    content: str = Field(min_length=1)
    tag: str
    owner_id: int

class NoteUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=120)
    content: Optional[str] = Field(None, min_length=1)
    tag: Optional[str] = None

class NoteResponse(BaseModel):
    id: int
    title: str
    content: str
    tag: str
    owner_id: int
    created_at: datetime
    ai_suggestion: Optional[dict] = None
    
    class Config:
        from_attributes = True

class AISuggestion(BaseModel):
    tags: List[str]
    summary: str

class NoteWithAIResponse(NoteResponse):
    ai_suggestion: Optional[AISuggestion] = None

class TagSummaryResponse(BaseModel):
    tag: str
    count: int

class UserNoteCountResponse(BaseModel):
    user_id: int
    user_name: str
    note_count: int