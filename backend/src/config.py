import os
from dotenv import load_dotenv

# Load the .env file
load_dotenv()

class Settings:
    # T001: Extract the OpenAI key from the environment
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    
    # You can also move other things here later
    PROJECT_NAME: str = "Todo API"

# Initialize a single instance to be used everywhere
settings = Settings()