import os
from dotenv import load_dotenv

load_dotenv()

RENTCAST_API_KEY = os.getenv("RENTCAST_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
SCRAPINGBEE_API_KEY = os.getenv("SCRAPINGBEE_API_KEY")
GOOGLE_MAPS_KEY = os.getenv("GOOGLE_MAPS_KEY")
ZILLOW_API_KEY = os.getenv("ZILLOW_API_KEY")
MAPILLARY_TOKEN = os.getenv("MAPILLARY_TOKEN")

OVERPASS_URL = "https://overpass-api.de/api/interpreter"