import logging
from fastapi import FastAPI, Form, BackgroundTasks, Response

# Import your data models (schemas) and service classes
from models.schemas import User, ChatMessage
from services.database_service import DatabaseService
from services.gsheets_service import GSheetsService
from services.gemini_service import GeminiService
from services.notification_service import NotificationService

# --- Global Setup ---
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Instantiate the FastAPI app
app = FastAPI(title="Arogya Mitra AI Assistant")

# Instantiate all service classes at the global level
db_service = DatabaseService()
gsheets_service = GSheetsService()
gemini_service = GeminiService()
notification_service = NotificationService()

# Define critical keywords for immediate safety response
CRITICAL_KEYWORDS = [
    'suicide', 'kill myself', 'want to die', 'heart attack', 'chest pain',
    'can\'t breathe', 'unconscious', 'poison', 'accident', 'bleeding heavily'
]
CRITICAL_RESPONSE_MESSAGE = "This seems like a critical situation. Please contact emergency services immediately by calling 108. This is an AI assistant and not a substitute for a medical professional."
# --- End Global Setup ---


# --- Background Task Logic ---
async def process_message_logic(user_phone: str, user_message: str):
    """
    This function contains the core logic for handling a non-critical message.
    It runs in the background to avoid timing out the Twilio webhook.
    """
    try:
        # a. Fetch User Profile
        user_profile_data = await db_service.get_user(user_phone)

        # b. Handle New Users
        if user_profile_data:
            user_profile = User(**user_profile_data)
        else:
            # Create a default profile for the new user
            user_profile = User(phone_number=user_phone)
            # You might want to save this new user profile to the DB immediately
            await db_service.create_or_update_user(user_profile)
            logger.info(f"Created new user profile for {user_phone}")

        # c. Fetch Chat History
        history = await db_service.get_chat_history(user_phone)

        # d. Call AI Service
        ai_response_text = await gemini_service.get_ai_response(
            user_message=user_message,
            user_profile=user_profile,
            chat_history=history
        )

        # e. Save Conversation to DB
        # Save user's message
        await db_service.save_chat_message(
            ChatMessage(phone_number=user_phone, sender='user', message_text=user_message)
        )
        # Save bot's response
        await db_service.save_chat_message(
            ChatMessage(phone_number=user_phone, sender='bot', message_text=ai_response_text)
        )

        # f. Send AI Reply back to the user
        await notification_service.send_sms(to_number=user_phone, message_body=ai_response_text)

    except Exception as e:
        logger.error(f"Error processing message for {user_phone}: {e}")
# --- End Background Task Logic ---


# --- API Endpoints ---
@app.get("/", tags=["Status"])
async def root():
    """Root endpoint to check if the service is running."""
    return {"status": "Arogya Mitra is running"}

@app.post("/api/message", tags=["Webhook"])
async def handle_message(
    background_tasks: BackgroundTasks,
    From: str = Form(...),
    Body: str = Form(...)
):
    """
    Main webhook endpoint to receive incoming SMS messages from Twilio.
    """
    user_phone = From
    user_message = Body.strip()
    logger.info(f"Received message from {user_phone}: '{user_message}'")

    # Critical Keyword Check (Safety First)
    if any(keyword in user_message.lower() for keyword in CRITICAL_KEYWORDS):
        logger.warning(f"Critical keyword detected from {user_phone}. Sending immediate response.")
        background_tasks.add_task(
            notification_service.send_sms,
            to_number=user_phone,
            message_body=CRITICAL_RESPONSE_MESSAGE
        )
    else:
        # Process Normal Message in the background
        background_tasks.add_task(process_message_logic, user_phone, user_message)
    
    # Return an empty response to Twilio immediately to prevent timeouts
    return Response(status_code=204)
# --- End API Endpoints ---
