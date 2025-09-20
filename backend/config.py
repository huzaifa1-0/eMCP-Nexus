
from pydantic_settings import BaseSettings




class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://admin:password@db:5432/marketplace"
    STRIPE_KEY: str
    COINBASE_KEY: str
    SECRET_KEY: str = "your-secret-key"  
    ALGORITHM: str = "HS256" 
    RENDER_API_KEY: str
    RENDER_OWNER_ID: str
    CLERK_SECRET_KEY: str # Add this line 
    


    class Config:
        env_file = ".env"
        

settings = Settings()