import asyncio
import logging
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

from core.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NotificationService:
    """
    Manages sending SMS notifications via the Twilio API.
    """
    def __init__(self):
        """
        Initializes the Twilio client using credentials from settings.
        """
        try:
            self.client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            self.sender_number = settings.TWILIO_PHONE_NUMBER
            logger.info(f"Twilio client initialized successfully for sender: {self.sender_number}")
        except Exception as e:
            logger.error(f"Failed to initialize Twilio client: {e}")
            self.client = None
            self.sender_number = None

    async def send_sms(self, to_number: str, message_body: str):
        """
        Sends an SMS message asynchronously.

        This function runs the synchronous Twilio library call in a separate
        thread to avoid blocking the main application event loop.
        """
        if not self.client:
            logger.error("Cannot send SMS: Twilio client is not available.")
            return

        try:
            # The Twilio library is synchronous (blocking).
            # asyncio.to_thread runs this blocking code in a separate thread,
            # allowing our async FastAPI app to remain responsive.
            message = await asyncio.to_thread(
                self.client.messages.create,
                to=to_number,
                from_=self.sender_number,
                body=message_body
            )
            logger.info(f"SMS sent successfully to {to_number}. SID: {message.sid}")
        except TwilioRestException as e:
            # Handle specific Twilio API errors (e.g., invalid phone number)
            logger.error(f"Failed to send SMS to {to_number}. Twilio error: {e}")
        except Exception as e:
            # Handle other unexpected errors
            logger.error(f"An unexpected error occurred while sending SMS: {e}")
