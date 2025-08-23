import os
import logging
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration constants
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "Your-Gemini-API-KEY")
FIREBASE_SERVICE_ACCOUNT_PATH = "serviceAccount.json"

# API Configuration
def get_gemini_api_url():
    """Get Gemini API URL with API key from environment"""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "Your-Gemini-API-KEY":
        logger.error("GEMINI_API_KEY not found in environment variables")
        raise ValueError("GEMINI_API_KEY must be set in .env file")
    return f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
GEMINI_CONFIG = {
    "temperature": 0.7,
    "maxOutputTokens": 1000,
    "topP": 1.0
}