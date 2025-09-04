from fastapi import FastAPI
from backend.routers import tools, payments, search, auth, monitoring, reputation
from backend.db import init_db

app = FastAPI(title="eMCP Nexus Backend")

app.include_router(tools.router, prefix="/tools", tags=["Tools"])
app.include_router(payments.router, prefix="/payments", tags=["Payments"])
app.include_router(search.router, prefix="/search", tags=["Search"])
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(monitoring.router, prefix="/monitoring", tags=["Monitoring"])
app.include_router(reputation.router, prefix="/reputation", tags=["Reputation"])

@app.on_event("startup")
async def startup_event():
    await init_db()


@app.get("/")
async def root():
    return {"message": "🚀 eMCP Nexus Backend is running"}