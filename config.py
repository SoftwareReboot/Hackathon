import os
from dotenv import load_dotenv

load_dotenv()

LM_BASE_URL = os.getenv("LM_BASE_URL")
LM_API_LEY = os.getenv("LM_API_KEY")
LM_MODEL = os.getenv("LM_MODEL")