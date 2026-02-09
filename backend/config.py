import os
from pydantic_settings import BaseSettings



class Settings(BaseSettings):
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "admin")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "password")
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "localhost") 
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "marketplace")

    # Construct the PostgreSQL Connection String
    # Format: postgresql+asyncpg://user:password@host:port/dbname
    DATABASE_URL: str = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"

    RECEIVER_WALLET_ADDRESS: str = "0xYOUR_WALLET_ADDRESS_HERE" 
    
    # Base Sepolia RPC URL (Get one from Alchemy or Infura, or use a public one)
    WEB3_RPC_URL: str = "https://sepolia.base.org"
    
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