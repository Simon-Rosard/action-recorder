import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.controllers import recording_controller
from app.services.recording_service import recording_service
import uvicorn

app = FastAPI(
    title="Action Recorder API",
    description="API pour enregistrer et rejouer les actions utilisateur",
    version="1.0.0"
)

# Charger les sessions existantes au démarrage
recording_service.load_sessions()

# Include routers
app.include_router(recording_controller.router, prefix="/api/recording", tags=["recording"])

@app.get("/")
async def root():
    return {
        "message": "Action Recorder API",
        "documentation": "/docs",
        "health": "/health"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "is_recording": recording_service.is_recording,
        "total_sessions": len(recording_service.sessions)
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 19000))
    uvicorn.run(app, host="0.0.0.0", port=port)
