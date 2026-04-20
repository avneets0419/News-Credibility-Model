import time
from fastapi import Request, HTTPException, Security
from fastapi.security import APIKeyHeader
from starlette.middleware.base import BaseHTTPMiddleware
from main.config import API_SECRET_KEY
from main.logger import logger_api

# Define that we expect "X-API-Key" in the header
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def verify_api_key(api_key_header: str = Security(api_key_header)):
    # If NO API key is set in .env, we assume testing environment and allow access
    if not API_SECRET_KEY:
        logger_api.warning("No API_SECRET_KEY set in environment. Skipping API key validation (testing mode).")
        return True
    
    # Log what we received vs what we expected
    logger_api.info(f"Validating API key - Received: '{api_key_header}' | Expected: '{API_SECRET_KEY}'")
        
    if api_key_header == API_SECRET_KEY:
        logger_api.info("✅ API Key validated successfully.")
        return True
    
    # Log the mismatch
    logger_api.error(f"❌ API Key validation FAILED - Received: '{api_key_header}' | Expected: '{API_SECRET_KEY}'")
    raise HTTPException(
        status_code=403, 
        detail="Could not validate credentials. Invalid or missing X-API-Key header."
    )


class TimingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        try:
            response = await call_next(request)
        except Exception as e:
            logger_api.error(f"Unhandled Exception caught by middleware: {e}")
            raise
            
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        return response
