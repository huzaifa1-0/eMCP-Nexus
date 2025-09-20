from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://admin:password@db:532/marketplace"
    
    # --- JWT Settings ---
    SECRET_KEY: str = "your-super-secret-key-that-is-long-and-random"  # Replace with a real secret key
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30 # Token will be valid for 30 minutes

    # --- Other Keys ---
    STRIPE_KEY: str
    COINBASE_KEY: str
    RENDER_API_KEY: str
    RENDER_OWNER_ID: str
    # You can now remove the CLERK_SECRET_KEY if you are not using it
    # CLERK_SECRET_KEY: str

    class Config:
        env_file = ".env"
        
settings = Settings()