import os
import logging
from importlib import import_module
from typing import List, Dict, Any
import numpy as np

logger = logging.getLogger(__name__)

# Global model instance (lazy loaded)
_model = None

def get_model():
    """Lazy load the sentence-transformers model."""
    global _model
    if _model is None:
        try:
            sentence_transformers = import_module("sentence_transformers")
            _model = sentence_transformers.SentenceTransformer(
                "sentence-transformers/all-MiniLM-L6-v2"
            )
            logger.info("Model loaded successfully")
        except ModuleNotFoundError as exc:
            if exc.name == "sentence_transformers":
                raise RuntimeError(
                    "Semantic search requires sentence-transformers. "
                    "Install the backend requirements in a supported Python environment."
                ) from exc
            raise
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise
    return _model

def compute_embeddings(texts: List[str]) -> np.ndarray:
    """
    Compute embeddings for a list of texts.
    """
    model = get_model()
    return model.encode(texts, convert_to_numpy=True)

def compute_similarity(query_embedding: np.ndarray, document_embeddings: np.ndarray) -> np.ndarray:
    """
    Compute cosine similarity between query and documents.
    """
    query_norm = np.linalg.norm(query_embedding)
    document_norms = np.linalg.norm(document_embeddings, axis=1)
    denominators = query_norm * document_norms

    # A zero vector has no meaningful cosine similarity; report it as zero.
    return np.divide(
        document_embeddings @ query_embedding,
        denominators,
        out=np.zeros_like(document_norms, dtype=float),
        where=denominators != 0,
    )

def semantic_search(query: str, notes: List[Dict[str, Any]], top_k: int = 3) -> List[Dict[str, Any]]:
    """
    Perform semantic search on notes.
    Returns top_k notes ranked by similarity.
    """
    if not notes:
        return []
    
    # Prepare texts for embedding
    texts = [note['content'] for note in notes]
    
    try:
        # Compute embeddings
        embeddings = compute_embeddings(texts)
        query_embedding = compute_embeddings([query])[0]
        
        # Compute similarities
        similarities = compute_similarity(query_embedding, embeddings)
        
        # Create results with similarity scores
        results = []
        for i, note in enumerate(notes):
            results.append({
                **note,
                'similarity_score': float(similarities[i])
            })
        
        # Sort by similarity descending
        results.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        return results[:top_k]
        
    except Exception as e:
        logger.error(f"Error in semantic search: {e}")
        return []

# Sample dataset for the AI sample notes
AI_SAMPLE_NOTES = [
    {"id": 1, "title": "Morning workout plan", "content": "Do 30 minutes of cardio followed by strength training focused on legs and core."},
    {"id": 2, "title": "Grocery list", "content": "Buy milk, eggs, spinach, chicken breast, and whole wheat bread for the week."},
    {"id": 3, "title": "Project deadline reminder", "content": "The backend API for the Zomato Notes capstone must be deployed and demoed by Friday."},
    {"id": 4, "title": "Book recommendation", "content": "A friend suggested reading a novel about a detective solving crimes in a coastal town."},
    {"id": 5, "title": "Recipe idea", "content": "Try making a vegetable stir fry with broccoli, bell peppers, and soy sauce tonight."},
    {"id": 6, "title": "Gym schedule change", "content": "Switch leg day to Thursday and move the rest day to Sunday this week."},
    {"id": 7, "title": "Meeting notes", "content": "Discussed the database schema for the notes app and agreed on using foreign keys for ownership."},
    {"id": 8, "title": "Weekend hiking trip", "content": "Plan a short hiking trip to a nearby trail, pack water bottles and snacks in advance."},
]
