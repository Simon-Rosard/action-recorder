from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Optional
from app.models.recording_models import (
    RecordingSession, SessionRequest, PlaybackRequest, 
    RecordingConfig, RecordedAction
)
from app.services.recording_service import recording_service
from app.services.playback_service import playback_service

router = APIRouter()

@router.post("/start", response_model=dict)
async def start_recording(session_request: SessionRequest):
    """Démarre un nouvel enregistrement."""
    try:
        session_id = recording_service.start_recording(
            session_name=session_request.name,
            config=session_request.config
        )
        return {
            "status": "Recording started",
            "session_id": session_id,
            "message": f"Recording session '{session_id}' has been started"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start recording: {str(e)}")

@router.post("/stop", response_model=dict)
async def stop_recording():
    """Arrête l'enregistrement actuel."""
    try:
        session = recording_service.stop_recording()
        if session:
            return {
                "status": "Recording stopped",
                "session_id": session.id,
                "session_name": session.name,
                "total_actions": len(session.actions),
                "duration_seconds": (session.end_time - session.start_time).total_seconds() if session.end_time else 0
            }
        else:
            raise HTTPException(status_code=400, detail="No active recording session")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to stop recording: {str(e)}")

@router.get("/sessions", response_model=List[RecordingSession])
async def get_all_sessions():
    """Récupère toutes les sessions d'enregistrement."""
    try:
        return recording_service.get_all_sessions()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve sessions: {str(e)}")

@router.get("/sessions/{session_id}", response_model=RecordingSession)
async def get_session(session_id: str):
    """Récupère une session spécifique."""
    try:
        session = recording_service.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
        return session
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve session: {str(e)}")

@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """Supprime une session."""
    try:
        if recording_service.delete_session(session_id):
            return {"status": "Session deleted", "session_id": session_id}
        else:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete session: {str(e)}")

@router.get("/sessions/{session_id}/actions", response_model=List[RecordedAction])
async def get_session_actions(session_id: str, limit: Optional[int] = None, offset: int = 0):
    """Récupère les actions d'une session avec pagination."""
    try:
        session = recording_service.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
        
        actions = session.actions[offset:]
        if limit:
            actions = actions[:limit]
        
        return actions
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve actions: {str(e)}")

@router.post("/playback")
async def play_session(playback_request: PlaybackRequest, background_tasks: BackgroundTasks):
    """Lance la lecture d'une session en arrière-plan."""
    try:
        # Lancer la lecture en arrière-plan
        background_tasks.add_task(
            playback_service.play_session,
            playback_request.session_id,
            playback_request.speed_multiplier,
            playback_request.start_from_action,
            playback_request.end_at_action
        )
        
        return {
            "status": "Playback started",
            "session_id": playback_request.session_id,
            "speed_multiplier": playback_request.speed_multiplier
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start playback: {str(e)}")

@router.post("/playback/stop")
async def stop_playback():
    """Arrête la lecture en cours."""
    try:
        playback_service.stop_playback()
        return {"status": "Playback stopped"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to stop playback: {str(e)}")

@router.get("/status")
async def get_status():
    """Récupère le statut actuel du service."""
    return {
        "is_recording": recording_service.is_recording,
        "active_session_id": recording_service.active_session_id,
        "is_playing": playback_service.is_playing,
        "current_playback_session": playback_service.current_session_id,
        "total_sessions": len(recording_service.sessions)
    }
