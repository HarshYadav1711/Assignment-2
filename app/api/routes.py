"""
REST API routes for session management and health checks.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.db.client import db_client

router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str
    message: str


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        Health status
    """
    return HealthResponse(
        status="healthy",
        message="Conversational AI backend is operational"
    )


@router.get("/sessions/{session_id}/summary")
async def get_session_summary(session_id: str):
    """
    Retrieve session summary.
    
    Args:
        session_id: Session identifier
        
    Returns:
        Session summary data
    """
    # In a full implementation, this would query the database
    # For now, return a placeholder
    return {
        "session_id": session_id,
        "message": "Use Supabase client to fetch session data"
    }

