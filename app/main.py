import os
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.db.database import create_tables
from app.routers import content
from app.tasks.cleanup import start_scheduler
from app.services.token_service import get_token

# Create FastAPI app
app = FastAPI(
    title="Entropy Content Protection API",
    description="Secure content with time-limited tokens that prevent unauthorized access",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(content.router)

# Startup event
@app.on_event("startup")
async def startup_event():
    # Create database tables
    create_tables()
    
    # Start background scheduler
    app.state.scheduler = start_scheduler()
    
    print("Entropy Content Protection API is ready!")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    # Shutdown scheduler
    if hasattr(app.state, "scheduler"):
        app.state.scheduler.shutdown()

# Root endpoint
@app.get("/")
async def root():
    return {
        "name": "Entropy Content Protection API",
        "version": "1.0.0",
        "status": "running"
    }

# Error handlers
@app.exception_handler(404)
async def not_found_exception_handler(request: Request, exc):
    return JSONResponse(
        status_code=404,
        content={"message": "The requested resource was not found"}
    )

@app.exception_handler(500)
async def server_error_exception_handler(request: Request, exc):
    return JSONResponse(
        status_code=500,
        content={"message": "An internal server error occurred"}
    )

# Run the application
if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)