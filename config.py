import os
from dotenv import load_dotenv

load_dotenv()

API_KEYS = os.getenv("API_KEYS", "").split(",")
