from fastapi import FastAPI
from contextlib import asynccontextmanager
from backend.routers import tools, payments, search, monitoring, reputation, monetization, auth, seller_dashboard, chat, stripe_payments, web3_payments
from backend.db import init_db
from backend.ai_services.search_engine import load_faiss_index
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
try:
    from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware
except ImportError:
    ProxyHeadersMiddleware = None
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
import os 
import sys
from backend.db import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from backend import crud
from backend.routers import proxy

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
    
    # Load FAISS index and Re-index to ensure sync
    try:
        from backend.ai_services.search_engine import reindex_all_tools
        from backend.db import async_session_factory
        
        # We re-index on every startup to ensure the vectors match the current DB state
        # especially if columns like 'readme' were just added.
        async with async_session_factory() as session:
            await reindex_all_tools(session)
    except Exception as e:
        print(f"FAISS re-indexing error: {e}")
    
    yield
    
    print("Application shutdown...")

from fastapi import Request
from fastapi.responses import JSONResponse
import traceback
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="eMCP Nexus Backend",
    description="A modern backend for the eMCP Nexus marketplace.",
    version="1.0.0",
    lifespan=lifespan
)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception caught: {exc}")
    logger.error(traceback.format_exc())
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc), "traceback": traceback.format_exc() if os.getenv("DEBUG") else None},
    )

origins = [
    "https://e-mcp-nexus.vercel.app",
    "http://localhost:5173",
    "http://localhost:3000",
]

# ✅ ADD: Proxy headers support for production (Railway/Render)
if ProxyHeadersMiddleware:
    app.add_middleware(ProxyHeadersMiddleware, trusted_hosts="*")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(SessionMiddleware, secret_key=os.getenv("SECRET_KEY") or "oauth-session-secret-key")

# ✅ Frontend: Serve React build (frontend-react/dist/)
frontend_dir = os.path.join(project_root, "frontend-react", "dist")

if os.path.exists(frontend_dir):
    print(f"✅ React build found: {frontend_dir}")
    
    # Serve React static assets
    assets_dir = os.path.join(frontend_dir, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")
else:
    print(f"⚠️ React build not found at {frontend_dir}. Run 'npm run build' in frontend-react/")

# ============ TOOL PAGE ROUTE - MUST BE FIRST (BEFORE ANY HTML ROUTES) ============
@app.get("/tool/background-remover")
async def serve_background_remover():
    """Serve the background remover tool page for paid subscribers"""
    tool_path = os.path.join(frontend_dir, "tool", "background-remover.html")
    print(f"🔍 Looking for tool at: {tool_path}")
    print(f"📁 File exists: {os.path.exists(tool_path)}")
    if os.path.exists(tool_path):
        return FileResponse(tool_path)
    return {"error": "Tool page not found", "path": tool_path}

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
app.include_router(chat.router, prefix="/api/chat", tags=["AI Chat"])
app.include_router(stripe_payments.router, prefix="/api/stripe", tags=["stripe"])
app.include_router(web3_payments.router, prefix="/api/web3", tags=["Web3"])
app.include_router(proxy.router, prefix="/api/proxy", tags=["MCP Proxy"])  # Proxy router should be last to avoid conflicts

@app.get("/api/stats")
async def read_stats(session: AsyncSession = Depends(get_async_session)):
    """
    Returns platform statistics:
    - Active Users (from DB)
    - MCP Tools (from DB)
    - Uptime (Static/Calculated)
    """
    stats = await crud.get_stats(session)
    
    return {
        "active_users": stats["user_count"],
        "mcp_tools": stats["tool_count"],
        "uptime": "99.9%"  # Keeping this static as it's usually calculated by external monitoring
    }

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
        return JSONResponse(status_code=404, content={"detail": "Not Found"})
    
    # Otherwise, try to serve the frontend
    index_path = os.path.join(frontend_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    else:
        return {"error": "Frontend not available"}