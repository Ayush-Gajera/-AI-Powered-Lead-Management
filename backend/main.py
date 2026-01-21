"""
Main FastAPI application
Outbound Email Sender + Reply Tracking MVP
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import leads, emails, sync, replies

# Create FastAPI app
app = FastAPI(
    title="Outbound Email Sender + Reply Tracking",
    description="MVP for sending emails and tracking replies via IMAP",
    version="1.0.0"
)

# CORS middleware - allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(leads.router)
app.include_router(emails.router)
app.include_router(sync.router)
app.include_router(replies.router)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "message": "Outbound Email Sender + Reply Tracking API",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
