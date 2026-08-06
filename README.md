# Zomato Notes - AI-Augmented Internal Knowledge Base

A full-stack application for Zomato's on-call support engineering team to capture, organize, and search internal notes with AI assistance.

## Table of Contents
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Setup and Installation](#setup-and-installation)
- [Running the Application](#running-the-application)
- [API Endpoints](#api-endpoints)
- [Features Walkthrough](#features-walkthrough)
- [Testing and Verification](#testing-and-verification)
- [Database Schema](#database-schema)
- [Project Structure](#project-structure)

## Features

### Core App (Part 1)
- User and Note management with validation
- Full CRUD operations
- Bulk import from text files
- Raw SQL reporting (tag summary, long notes, user notes)
- CORS-enabled API with authentication
- Responsive web dashboard
- Recursive category tree navigation
- Debounced search

### Ranking Engine (Part 2)
- Custom insertion sort for relevance/date ranking
- Iterative and recursive binary search for exact title lookup
- Linear search for quick tag jumping
- Frontend controls for all search modes

### Intelligence Layer (Part 3)
- LLM-powered auto-tagging and summarization
- Mock AI mode (no API key required)
- Local semantic search using sentence-transformers
- Smart Search with cosine similarity ranking

## Technology Stack

### Backend
- **FastAPI** - Web framework
- **SQLAlchemy** - ORM
- **SQLite** - Database (file-based)
- **Pydantic** - Data validation
- **sentence-transformers** - Semantic search (all-MiniLM-L6-v2)

### Frontend
- **Vanilla HTML/CSS/JavaScript** - No frameworks
- **Fetch API** - HTTP requests
- **CSS Grid/Flexbox** - Responsive layout

## Setup and Installation

### Prerequisites
- Python 3.9 or higher
- Node.js (optional, for frontend development)
- Git

### Clone the Repository
```bash
git clone https://github.com/yourusername/zomato-notes.git
cd zomato-notes