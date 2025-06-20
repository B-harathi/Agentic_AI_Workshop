import os
from dotenv import load_dotenv

load_dotenv()

# Configuration settings
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyCi1Fr-z-A8fDB3ahs8Iduz3nsM1gIOKxk")
EMAIL_USER = "gbharathitrs@gmail.com"
EMAIL_PASS = "isvhhcmhhcnlqaaq"

# Paths
VECTOR_STORE_PATH = "data/vector_store"
UPLOAD_PATH = "data/uploads"

# Agent endpoints
AGENT_PORT = 8000
BACKEND_URL = "http://localhost:3002"