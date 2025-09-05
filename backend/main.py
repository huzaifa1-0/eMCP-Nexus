from fastapi import FastAPI
from contextlib import asynccontextmanager
from .routers import tools, payments, search, auth, monitoring, reputation
from backend.db import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handles application startup and shutdown events.
    """
    print("Application startup...")
    
    await init_db()
    print("Database tables initialized.")
    yield
    print("Application shutdown...")
    


app = FastAPI(
    title="eMCP Nexus Backend",
    description="A modern backend for the eMCP Nexus marketplace.",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(tools.router, prefix="/tools", tags=["Tools"])
app.include_router(payments.router, prefix="/payments", tags=["Payments"])
app.include_router(search.router, prefix="/search", tags=["Search"])
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(monitoring.router, prefix="/monitoring", tags=["Monitoring"])
app.include_router(reputation.router, prefix="/reputation", tags=["Reputation"])



@app.get("/", tags=["Root"])
async def root():
    return {"message": "🚀 eMCP Nexus Backend is running"}