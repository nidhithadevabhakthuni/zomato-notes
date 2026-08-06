import os
import json
import logging
from typing import Dict, Any, Optional
from dotenv import load_dotenv
import re

load_dotenv()

logger = logging.getLogger(__name__)

# Check if we're in mock mode
MOCK_AI = os.getenv("MOCK_AI", "1") == "1"

# The prompt template with 5-part structure
PROMPT_TEMPLATE = """
Instructions: Analyze the provided note content and extract key information.

Context: This is for a note-taking application where users want quick categorization and summary of their notes.

Input: Note content: "{content}"

Constraints: 
- Return ONLY valid JSON
- Do not include any text before or after the JSON
- The JSON must have exactly two keys: "tags" and "summary"
- "tags" must be a list of 1-3 short lowercase keyword strings
- "summary" must be one sentence at most 20 words

Output Format: 
{{
    "tags": ["keyword1", "keyword2"],
    "summary": "One sentence summary of the note content."
}}
"""

def get_ai_response(user_message: str, system_prompt: str) -> str:
    """
    Get AI response from LLM API or mock mode.
    """
    if MOCK_AI:
        return mock_ai_response(user_message)
    
    # Real API path (optional extension)
    try:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.warning("OPENAI_API_KEY not set, falling back to mock")
            return mock_ai_response(user_message)
        
        # Import here to avoid dependency if not used
        import openai
        client = openai.OpenAI(api_key=api_key)
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.3,
            max_tokens=150
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Error calling OpenAI API: {e}")
        return mock_ai_response(user_message)

def mock_ai_response(content: str) -> str:
    """
    Mock response that extracts tags and summary from content.
    No API key required.
    """
    # Extract significant words (nouns and adjectives) as tags
    words = content.lower().split()
    # Filter out common stopwords
    stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                 'of', 'with', 'without', 'by', 'from', 'up', 'down', 'off', 'over',
                 'under', 'above', 'below', 'between', 'among', 'through', 'during'}
    
    significant_words = [w.strip('.,!?;:') for w in words if w.strip('.,!?;:') not in stopwords and len(w) > 3]
    
    # Take first 3 significant words as tags
    tags = significant_words[:3] if significant_words else ["note"]
    
    # Generate summary from first sentence
    sentences = content.split('.')
    first_sentence = sentences[0] if sentences else content
    summary_words = first_sentence.split()
    summary = ' '.join(summary_words[:20])
    if len(summary_words) > 20:
        summary += '...'
    
    return json.dumps({
        "tags": tags,
        "summary": summary
    })

def generate_ai_suggestion(content: str) -> Optional[Dict[str, Any]]:
    """
    Generate AI suggestion for note content.
    Returns dict with tags and summary, or None if parsing fails.
    """
    try:
        # Format the prompt with content
        prompt = PROMPT_TEMPLATE.format(content=content)
        
        # Get response
        response = get_ai_response(content, prompt)
        
        # Try to parse JSON
        # Clean the response to extract just the JSON
        response = response.strip()
        # Find JSON-like structure
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            response = json_match.group()
        
        result = json.loads(response)
        
        # Validate structure
        if not isinstance(result, dict) or 'tags' not in result or 'summary' not in result:
            logger.warning(f"Invalid response structure: {result}")
            return None
        
        if not isinstance(result['tags'], list) or not isinstance(result['summary'], str):
            logger.warning(f"Invalid data types in response: {result}")
            return None
        
        return result
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON parse error: {e}, response: {response}")
        return None
    except Exception as e:
        logger.error(f"Error generating AI suggestion: {e}")
        return None