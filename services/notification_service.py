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
   
        if not self.client:
            logger.error("Twilio client not initialized.")
            return

        try:
            from_number = self.sender_number # Default to your SMS number

            # Check if the destination is a WhatsApp number
            if to_number.startswith('whatsapp:'):
                # If so, the sender must also be the WhatsApp sandbox number
                from_number = f"whatsapp:{settings.TWILIO_WHATSAPP_NUMBER}"

            # Run the synchronous Twilio call in a separate thread
            await asyncio.to_thread(
                self.client.messages.create,
                from_=from_number,
                to=to_number,
                body=message_body
            )
            logger.info(f"Successfully sent message to {to_number}")
        except Exception as e:
            logger.error(f"Failed to send message to {to_number}. Twilio error: {e}")
