from pydantic import BaseModel
from typing import Optional

class User(BaseModel):
    """
    Represents a detailed user profile with specific health conditions.
    This structured data allows for more accurate, personalized AI responses.
    """
    phone_number: str
    language: str = 'English'
    age: Optional[int] = None
    has_diabetes: Optional[bool] = False
    has_hypertension: Optional[bool] = False
    other_conditions: Optional[str] = None

class ChatMessage(BaseModel):
    """
    Represents a single message in a conversation.
    Used for logging chat history and providing context to the AI.
    """
    phone_number: str
    sender: str  # Can be 'user' or 'bot'
    message_text: str
