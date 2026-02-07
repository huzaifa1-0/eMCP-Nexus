import os
from pydantic_settings import BaseSettings



# Calculate the project root directory strictly
# This gets the folder containing config.py (backend/)
current_dir = os.path.dirname(os.path.abspath(__file__))
# This gets the parent folder (project root)
project_root = os.path.dirname(current_dir)
# This points specifically to the marketplace.db in the root
db_path = os.path.join(project_root, "marketplace.db")
class Settings(BaseSettings):
    DATABASE_URL: str = f"sqlite+aiosqlite:///{db_path}"
    
    # --- JWT Settings ---
    SECRET_KEY: str = "your-super-secret-key-that-is-long-and-random"  # Replace with a real secret key
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30 # Token will be valid for 30 minutes

    GROQ_API_KEY: str | None = None

    # --- Other Keys ---
    STRIPE_KEY: str
    COINBASE_KEY: str
    RENDER_API_KEY: str
    RENDER_OWNER_ID: str

    class Config:
        env_file = ".env"
        
settings = Settings()