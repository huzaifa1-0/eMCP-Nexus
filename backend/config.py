from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://admin:passsword@db:5432/marketplace"
    GOOGLE_PROJECT: str
    GOOGLE_DATASET: str
    STRIPE_KEY: str
    COINBASE_KEY: str
    SECRET_KEY: str = "your-secret-key"  
    ALGORITHM: str = "HS256"  


    class Config:
        env_file = ".env"
        

settings = Settings()