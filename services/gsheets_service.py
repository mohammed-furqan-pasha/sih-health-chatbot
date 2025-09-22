import gspread
import json
import logging
from typing import Dict, Optional, List, Any

from ..core.config import settings

# Configure logging for better debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GSheetsService:
    """
    Manages connection to and retrieval of data from the Google Sheet knowledge base.
    The sheet data is loaded into memory on initialization for fast lookups.
    """
    def __init__(self, sheet_name: str = "HealthDB"):
        """
        Initializes the service by authenticating with Google Sheets and
        loading the entire first worksheet into an in-memory list.
        """
        self.records: List[Dict[str, Any]] = []
        try:
            # Parse the JSON string from the environment variable into a dict
            creds_json = json.loads(settings.GOOGLE_APPLICATION_CREDENTIALS_JSON)
            
            # Authenticate with Google Sheets using the parsed credentials
            gc = gspread.service_account_from_dict(creds_json)
            
            # Open the workbook and select the first sheet
            spreadsheet = gc.open(sheet_name)
            worksheet = spreadsheet.sheet1
            
            # Load all records from the worksheet into a list of dictionaries
            self.records = worksheet.get_all_records()
            
            logger.info(f"Successfully loaded {len(self.records)} records from Google Sheet '{sheet_name}'.")

        except json.JSONDecodeError:
            logger.error("Failed to parse GOOGLE_APPLICATION_CREDENTIALS_JSON. Check the .env file format.")
        except gspread.exceptions.SpreadsheetNotFound:
            logger.error(f"Google Sheet '{sheet_name}' not found. Check the name and sharing settings.")
        except Exception as e:
            logger.error(f"An unexpected error occurred while connecting to Google Sheets: {e}")

    async def get_health_info(self, topic: str) -> Optional[Dict[str, Any]]:
        """
        Performs a case-insensitive search for a health topic in the loaded records.

        Args:
            topic: The health topic to search for (e.g., 'Dengue').

        Returns:
            A dictionary representing the entire row if a match is found, otherwise None.
        """
        search_topic = topic.lower()
        for record in self.records:
            # Ensure the 'topic' key exists and is a string before searching
            if 'topic' in record and isinstance(record['topic'], str) and record['topic'].lower() == search_topic:
                logger.info(f"Found health info for topic: {topic}")
                return record
        
        logger.warning(f"No health info found for topic: {topic}")
        return None
