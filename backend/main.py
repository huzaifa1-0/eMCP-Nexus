from fastapi import FastAPI
from contextlib import asynccontextmanager
from backend.routers import tools, payments, search, monitoring, reputation, monetization, auth, seller_dashboard
from backend.db import init_db
from backend.ai_services.search_engine import load_faiss_index
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os 
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handles application startup and shutdown events.
    """
    print("Application startup...")
    
    # Initialize database
    try:
        await init_db()
        print("Database tables initialized.")
    except Exception as e:
        print(f"Database initialization error: {e}")
    
    # Load FAISS index
    try:
        load_faiss_index()
        print("FAISS index loaded.")
    except Exception as e:
        print(f"FAISS index loading error: {e}")
    
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
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ FIXED: Better path handling
frontend_dir = os.path.join(project_root, "frontend")
print(f"Frontend directory: {frontend_dir}")

# Check if frontend directory exists
if not os.path.exists(frontend_dir):
    print(f"❌ ERROR: Frontend directory not found at {frontend_dir}")
    print("Please make sure the 'frontend' folder exists in your project root")
else:
    print(f"✅ Frontend directory found: {frontend_dir}")
    # List files in frontend directory for debugging
    try:
        frontend_files = os.listdir(frontend_dir)
        print(f"Frontend files: {frontend_files}")
    except Exception as e:
        print(f"Error listing frontend files: {e}")

    # Serve static files (CSS, JS, etc.)
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

# ✅ FIXED: Define API routes BEFORE including routers to avoid conflicts
@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy", 
        "message": "eMCP Nexus Backend is running",
        "frontend_dir": frontend_dir,
        "frontend_exists": os.path.exists(frontend_dir)
    }

@app.get("/api")
async def root():
    return {"message": "🚀 eMCP Nexus Backend is running"}

# ✅ FIXED: Add debug endpoint with proper path
@app.get("/api/debug/files")
async def debug_files():
    try:
        frontend_files = []
        if os.path.exists(frontend_dir):
            frontend_files = os.listdir(frontend_dir)
        
        return {
            "project_root": project_root,
            "frontend_dir": frontend_dir,
            "frontend_exists": os.path.exists(frontend_dir),
            "files": frontend_files,
            "current_directory": os.getcwd()
        }
    except Exception as e:
        return {"error": str(e)}


app.include_router(tools.router, prefix="/api/tools", tags=["Tools"])
app.include_router(payments.router, prefix="/api/payments", tags=["Payments"])
app.include_router(search.router, prefix="/api/search", tags=["Search"])
app.include_router(monitoring.router, prefix="/api/monitoring", tags=["Monitoring"])
app.include_router(reputation.router, prefix="/api/reputation", tags=["Reputation"])
app.include_router(monetization.router, prefix="/api/monetization", tags=["Monetization"]) 
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"]) 
app.include_router(seller_dashboard.router, prefix="/api/seller_dashboard", tags=["Seller Dashboard"])


@app.get("/")
async def serve_index():
    index_path = os.path.join(frontend_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    else:
        return {"error": "index.html not found", "path": index_path}

@app.get("/marketplace")
async def serve_marketplace():
    marketplace_path = os.path.join(frontend_dir, "marketplace.html")
    if os.path.exists(marketplace_path):
        return FileResponse(marketplace_path)
    else:
        return {"error": "marketplace.html not found", "path": marketplace_path}
    

@app.get("/seller_dashboard.html")
async def serve_seller_dashboard():
    path = os.path.join(frontend_dir, "seller_dashboard.html")
    if os.path.exists(path):
        return FileResponse(path)
    return {"error": "file not found"}

@app.get("/newmcp.html")
async def serve_new_mcp():
    path = os.path.join(frontend_dir, "newmcp.html")
    if os.path.exists(path):
        return FileResponse(path)
    return {"error": "file not found"}

# ✅ ADD: Catch-all route for SPA routing (should be last)
@app.get("/{full_path:path}")
async def catch_all(full_path: str):
    # If it's an API route that doesn't exist, return 404
    if full_path.startswith('api/'):
        return {"detail": "Not Found"}, 404
    
    # Otherwise, try to serve the frontend
    index_path = os.path.join(frontend_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    else:
        return {"error": "Frontend not available"}