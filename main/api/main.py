from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from main.config import API_HOST, API_PORT, API_DEBUG, API_SECRET_KEY
from main.logger import logger_api
from main.api.routes import router
from main.api.middleware import TimingMiddleware
from main.api.database import init_db

# Initialize database
init_db()

# Application Factory
app = FastAPI(
    title="Intelligent News Credibility API",
    description="Backend API for Fact-Checking and Analyzing News Claims via LangGraph Agents",
    version="2.0.0",
)

# Apply CORS (Allow the upcoming Streamlit UI to ping us if they are on different ports)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Apply Custom Middleware
app.add_middleware(TimingMiddleware)

# Bind the Routing module
app.include_router(router, prefix="/api", tags=["Analysis Core"])

@app.get("/", tags=["Health"])
def health_check():
    """Simple verification that the API server is alive."""
    return {"status": "online", "message": "News Credibility API is running. Access /docs for swagger GUI."}

@app.head("/", tags=["Health"])
def health_check_head():
    """HEAD endpoint for uptime monitoring."""
    return {}

if __name__ == "__main__":
    logger_api.info(f"Starting API server on {API_HOST}:{API_PORT}")
    uvicorn.run(
        "main.api.main:app", 
        host=API_HOST, 
        port=API_PORT, 
        reload=API_DEBUG
    )
