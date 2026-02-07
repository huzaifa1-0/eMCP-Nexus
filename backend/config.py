import os
from pydantic_settings import BaseSettings

# 1. Calculate the absolute path to the project root
# This gets the folder containing this config file (backend/)
current_file_dir = os.path.dirname(os.path.abspath(__file__))
# This gets the parent folder (project root)
project_root = os.path.dirname(current_file_dir)
# This points specifically to the marketplace.db in the root
db_path = os.path.join(project_root, "marketplace.db")

class Settings(BaseSettings):
    # 2. Use the absolute path for the database connection
    # The 'f' string inserts the calculate path dynamically
    DATABASE_URL: str = f"sqlite+aiosqlite:///{db_path}"
    
    # --- JWT Settings ---
    SECRET_KEY: str = "your-super-secret-key-that-is-long-and-random"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30 

    GROQ_API_KEY: str | None = None

    # --- Other Keys ---
    STRIPE_KEY: str
    COINBASE_KEY: str
    RENDER_API_KEY: str
    RENDER_OWNER_ID: str

    class Config:
        env_file = ".env"
        
settings = Settings()