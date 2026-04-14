import os
from pydantic_settings import BaseSettings



class Settings(BaseSettings):
    # Look for both POSTGRES_ and standard PG prefix
    POSTGRES_USER: str = os.getenv("POSTGRES_USER") or os.getenv("PGUSER") or "admin"
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD") or os.getenv("PGPASSWORD") or "password"
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER") or os.getenv("PGHOST") or "localhost" 
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT") or os.getenv("PGPORT") or "5432"
    POSTGRES_DB: str = os.getenv("POSTGRES_DB") or os.getenv("PGDATABASE") or "marketplace"

    # Construct the PostgreSQL Connection String
    # Prioritize DATABASE_URL, then DATABASE_PUBLIC_URL
    DATABASE_URL: str | None = os.getenv("DATABASE_URL") or os.getenv("DATABASE_PUBLIC_URL")

    def __init__(self, **values):
        super().__init__(**values)
        # If DATABASE_URL is provided in environment, ensure it uses the asyncpg driver
        if self.DATABASE_URL:
            # Clean up empty ports (e.g., "host:/db" or "host: /db" -> "host/db")
            import re
            self.DATABASE_URL = re.sub(r':(?=/|@|$|\?)', '', self.DATABASE_URL)
            self.DATABASE_URL = re.sub(r':\s+(?=/|@|$|\?)', '', self.DATABASE_URL)

            # Handle protocol
            if self.DATABASE_URL.startswith("postgres://"):
                self.DATABASE_URL = self.DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)
            elif self.DATABASE_URL.startswith("postgresql://") and "asyncpg" not in self.DATABASE_URL:
                self.DATABASE_URL = self.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
            
            # Handle SSL for Railway Public URLs
            if (".railway.app" in self.DATABASE_URL or "railway" in self.DATABASE_URL) and "ssl=" not in self.DATABASE_URL:
                separator = "&" if "?" in self.DATABASE_URL else "?"
                self.DATABASE_URL += f"{separator}ssl=require"
        else:
            # Fallback to constructed URL
            # Ensure port is a valid number otherwise exclude it
            port_str = f":{self.POSTGRES_PORT}" if self.POSTGRES_PORT and self.POSTGRES_PORT.strip() else ""
            self.DATABASE_URL = f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}{port_str}/{self.POSTGRES_DB}"

    RECEIVER_WALLET_ADDRESS: str = "0xYOUR_WALLET_ADDRESS_HERE" 
    
    # Base Sepolia RPC URL (Get one from Alchemy or Infura, or use a public one)
    WEB3_RPC_URL: str = "https://sepolia.base.org"
    
    # --- JWT Settings ---
    SECRET_KEY: str = "your-super-secret-key-that-is-long-and-random"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30 

    GROQ_API_KEY: str | None = None

    # --- Other Keys ---
    STRIPE_KEY: str | None = None
    COINBASE_KEY: str | None = None
    RENDER_API_KEY: str | None = None
    RENDER_OWNER_ID: str | None = None

    class Config:
        env_file = ".env"
        
settings = Settings()