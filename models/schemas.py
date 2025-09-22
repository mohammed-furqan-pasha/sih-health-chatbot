from pydantic import BaseModel
from typing import Optional

class User(BaseModel):
    """
    Represents a user's profile in the database.
    Ensures data consistency for user-related operations.
    """
    phone_number: str
    language: str = 'English'  # Default language
    age: Optional[int] = None
    conditions: Optional[str] = None # e.g., "diabetes,hypertension"

class ChatMessage(BaseModel):
    """
    Represents a single message in a conversation.
    Used for logging chat history and providing context to the AI.
    """
    phone_number: str
    sender: str  # Can be 'user' or 'bot'
    message_text: str
