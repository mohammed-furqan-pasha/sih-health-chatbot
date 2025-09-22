import os
import pytest
from dotenv import load_dotenv

# This import works because of the pyproject.toml setup
from services.notification_service import NotificationService

# Load environment variables from .env file for testing
load_dotenv()

# Condition to skip the test if any Twilio credentials are not set
skip_if_no_twilio_creds = pytest.mark.skipif(
    not all([
        os.getenv("TWILIO_ACCOUNT_SID"),
        os.getenv("TWILIO_AUTH_TOKEN"),
        os.getenv("TWILIO_PHONE_NUMBER")
    ]),
    reason="Twilio credentials are not fully set in the environment."
)

@skip_if_no_twilio_creds
def test_twilio_client_initialization():
    """
    Tests that the NotificationService successfully initializes the Twilio client.
    This confirms that the API credentials are valid without sending an actual SMS.
    """
    # ARRANGE & ACT: Attempt to create an instance of the service.
    # The initialization logic is in the constructor (__init__).
    notification_service = NotificationService()

    # ASSERT: Check that the client object was created successfully.
    # If __init__ fails, self.client will be None.
    assert notification_service.client is not None, "Twilio client should be initialized."
    assert notification_service.sender_number is not None, "Twilio sender number should be set."
