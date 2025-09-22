import logging
import google.generativeai as genai
from typing import List, Dict, Any

from core.config import settings
from models.schemas import User

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define the system instruction as a constant for clarity
SYSTEM_INSTRUCTION = """You are Arogya Mitra, a friendly, empathetic, and helpful AI public health assistant for the people of Odisha. Your goal is to provide safe, general health information and guidance based on the user's profile and query. You are NOT a doctor and must NEVER provide a medical diagnosis. Always respond in the user's preferred language. Always conclude your health-related advice with a clear disclaimer to consult a registered medical practitioner."""

class GeminiService:
    """
    Manages all interactions with the Google Gemini API.
    """
    def __init__(self):
        """
        Configures the Generative AI client and initializes the model.
        """
        try:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.model = genai.GenerativeModel('gemini-pro')
            logger.info("Gemini Pro model initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to configure Gemini client: {e}")
            self.model = None

    async def get_ai_response(self, user_message: str, user_profile: User, chat_history: List[Dict[str, Any]]) -> str:
        """
        Constructs a detailed prompt and gets a response from the Gemini API.
        """
        if not self.model:
            logger.error("Gemini model not available.")
            return "I'm sorry, my AI service is currently unavailable. Please try again later."

        try:
            # 1. Format the user's health profile for the AI
            profile_details = f"Language: {user_profile.language}, Age: {user_profile.age or 'Not provided'}"
            if user_profile.has_diabetes:
                profile_details += ", Condition: Diabetes"
            if user_profile.has_hypertension:
                profile_details += ", Condition: Hypertension"
            if user_profile.other_conditions:
                profile_details += f", Other Conditions: {user_profile.other_conditions}"

            # 2. Format the recent chat history for context
            history_text = "\n".join([f"{msg['sender'].capitalize()}: {msg['message_text']}" for msg in chat_history])

            # 3. Construct the final, multi-part prompt
            full_prompt = f"""
            **System Instruction:**
            {SYSTEM_INSTRUCTION}

            ---

            **User's Health Profile:**
            {profile_details}

            ---

            **Recent Conversation History:**
            {history_text}

            ---

            **Current User Message:**
            {user_message}
            """

            # 4. Send the prompt to the API asynchronously
            response = await self.model.generate_content_async(full_prompt)
            
            # 5. Safely extract and return the text
            return response.text

        except Exception as e:
            # Handle API errors, including safety blocks
            logger.error(f"An error occurred with the Gemini API: {e}")
            return "I'm sorry, I was unable to process your request. Please ask in a different way or try again later."
