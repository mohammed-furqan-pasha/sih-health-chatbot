import logging
from typing import Any, Dict, Optional, List

from supabase import create_client, AsyncClient

from core.config import settings
from models.schemas import User, ChatMessage

# Configure logging for better debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseService:
    """
    Manages all asynchronous interactions with the Supabase database.
    """
    def __init__(self):
        try:
            # FIX: Create an AsyncClient directly for all async operations
            self.supabase: AsyncClient = AsyncClient(
                settings.SUPABASE_URL, settings.SUPABASE_KEY
            )
            logger.info("Successfully initialized Supabase AsyncClient.")
        except Exception as e:
            logger.error(f"Failed to initialize Supabase AsyncClient: {e}")
            self.supabase = None

    async def get_user(self, phone_number: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves a user's profile from the 'users' table by their phone number.
        """
        if not self.supabase:
            logger.error("Supabase client not available.")
            return None
            
        try:
            response = await self.supabase.table('users').select('*').eq('phone_number', phone_number).execute()
            if response.data:
                logger.info(f"User found for phone number: {phone_number}")
                return response.data[0]
            else:
                logger.info(f"No user found for phone number: {phone_number}")
                return None
        except Exception as e:
            logger.error(f"Database error while getting user {phone_number}: {e}")
            return None

    async def create_or_update_user(self, user_data: User) -> None:
        """
        Creates a new user or updates an existing one based on the phone number.
        This is also known as an 'upsert' operation.yoo
        """
        if not self.supabase:
            logger.error("Supabase client not available.")
            return
            
        try:
            # model_dump() converts the Pydantic model to a dictionary
            # upsert() will insert if the record doesn't exist, or update it if it does.
            await self.supabase.table('users').upsert(user_data.model_dump()).execute()
            logger.info(f"Upserted user profile for: {user_data.phone_number}")
        except Exception as e:
            logger.error(f"Database error during user upsert for {user_data.phone_number}: {e}")

    async def save_chat_message(self, message: ChatMessage) -> None:
        """
        Saves a single chat message to the 'chat_history' table.hi
        """
        if not self.supabase:
            logger.error("Supabase client not available.")
            return

        try:
            await self.supabase.table('chat_history').insert(message.model_dump()).execute()
            logger.info(f"Saved message from '{message.sender}' to chat history.")
        except Exception as e:
            logger.error(f"Database error while saving chat message: {e}")
            
    async def get_chat_history(self, phone_number: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieves the most recent chat history for a given user.
        """
        if not self.supabase:
            logger.error("Supabase client not available.")
            return []

        try:
            response = (
                await self.supabase.table('chat_history')
                .select('*')
                .eq('phone_number', phone_number)
                .order('created_at', desc=True)
                .limit(limit)
                .execute()
            )
            # The records are fetched in descending order, so we reverse them to get chronological order
            return list(reversed(response.data))
        except Exception as e:
            logger.error(f"Database error while getting chat history for {phone_number}: {e}")
            return []
