from fastapi import FastAPI
from contextlib import asynccontextmanager
from backend.routers import tools, payments, search, monitoring, reputation, monetization, auth
from backend.db import init_db
from ai_services.search_engine import load_faiss_index
from fastapi.middleware.cors import CORSMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handles application startup and shutdown events.
    """
    print("Application startup...")
    
    await init_db()
    print("Database tables initialized.")
    load_faiss_index()
    yield
    print("Application shutdown...")
    


app = FastAPI(
    title="eMCP Nexus Backend",
    description="A modern backend for the eMCP Nexus marketplace.",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # This allows your frontend to make requests
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tools.router, prefix="/tools", tags=["Tools"])
app.include_router(payments.router, prefix="/payments", tags=["Payments"])
app.include_router(search.router, prefix="/search", tags=["Search"])
app.include_router(monitoring.router, prefix="/monitoring", tags=["Monitoring"])
app.include_router(reputation.router, prefix="/reputation", tags=["Reputation"])
app.include_router(monetization.router, prefix="/monetization", tags=["Monetization"]) 
app.include_router(auth.router, prefix="/auth", tags=["Authentication"]) 



@app.get("/", tags=["Root"])
async def root():
    return {"message": "🚀 eMCP Nexus Backend is running"}