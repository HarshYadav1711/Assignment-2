"""
Supabase client wrapper with async operations.
Handles all database interactions with proper error handling and logging.
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
import logging
from supabase import create_client, Client
from app.config import settings

logger = logging.getLogger(__name__)


class SupabaseClient:
    """
    Async-safe Supabase client wrapper.
    
    Note: Supabase Python client uses httpx internally which is async-compatible,
    but we wrap operations to ensure proper error handling and type safety.
    """
    
    def __init__(self):
        """Initialize Supabase client with credentials from settings."""
        self.client: Client = create_client(
            settings.supabase_url,
            settings.supabase_key
        )
        logger.info("Supabase client initialized")
    
    async def create_session(
        self,
        session_id: str,
        user_id: str,
        start_time: datetime
    ) -> bool:
        """
        Create a new session record.
        
        Args:
            session_id: Unique session identifier
            user_id: User identifier
            start_time: Session start timestamp
            
        Returns:
            True if successful, False otherwise
        """
        try:
            result = self.client.table("sessions").insert({
                "session_id": session_id,
                "user_id": user_id,
                "start_time": start_time.isoformat(),
                "end_time": None,
                "duration_seconds": None,
                "final_summary": None
            }).execute()
            
            logger.info(f"Session {session_id} created successfully")
            return len(result.data) > 0
        except Exception as e:
            logger.error(f"Failed to create session {session_id}: {e}")
            return False
    
    async def log_event(
        self,
        session_id: str,
        event_type: str,
        content: str,
        timestamp: Optional[datetime] = None
    ) -> bool:
        """
        Log an event to session_events table.
        
        Args:
            session_id: Session identifier
            event_type: Type of event (user_message, ai_token, tool_call, etc.)
            content: Event content/payload
            timestamp: Event timestamp (defaults to now)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if timestamp is None:
                timestamp = datetime.utcnow()
            
            result = self.client.table("session_events").insert({
                "session_id": session_id,
                "event_type": event_type,
                "content": content,
                "timestamp": timestamp.isoformat()
            }).execute()
            
            return len(result.data) > 0
        except Exception as e:
            logger.error(f"Failed to log event for session {session_id}: {e}")
            return False
    
    async def get_session_events(
        self,
        session_id: str
    ) -> List[Dict[str, Any]]:
        """
        Retrieve all events for a session, ordered chronologically.
        
        Args:
            session_id: Session identifier
            
        Returns:
            List of event dictionaries
        """
        try:
            result = self.client.table("session_events")\
                .select("*")\
                .eq("session_id", session_id)\
                .order("timestamp", desc=False)\
                .execute()
            
            return result.data if result.data else []
        except Exception as e:
            logger.error(f"Failed to retrieve events for session {session_id}: {e}")
            return []
    
    async def update_session_summary(
        self,
        session_id: str,
        summary: str,
        end_time: datetime,
        duration_seconds: int
    ) -> bool:
        """
        Update session with final summary and end time.
        
        Args:
            session_id: Session identifier
            summary: AI-generated session summary
            end_time: Session end timestamp
            duration_seconds: Calculated session duration
            
        Returns:
            True if successful, False otherwise
        """
        try:
            result = self.client.table("sessions")\
                .update({
                    "final_summary": summary,
                    "end_time": end_time.isoformat(),
                    "duration_seconds": duration_seconds
                })\
                .eq("session_id", session_id)\
                .execute()
            
            logger.info(f"Session {session_id} summary updated")
            return len(result.data) > 0
        except Exception as e:
            logger.error(f"Failed to update session {session_id}: {e}")
            return False


# Global database client instance
db_client = SupabaseClient()

