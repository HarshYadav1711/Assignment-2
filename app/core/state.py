"""
In-memory session state management.
Maintains conversation context, tool outputs, and routing decisions.
Designed for fast access and easy serialization.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field, asdict
from enum import Enum
import json


class EventType(str, Enum):
    """Event type enumeration for type safety."""
    USER_MESSAGE = "user_message"
    AI_TOKEN = "ai_token"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"
    SYSTEM_EVENT = "system_event"


@dataclass
class Message:
    """Represents a single message in the conversation."""
    role: str  # "user", "assistant", "system", "tool"
    content: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    tool_calls: Optional[List[Dict[str, Any]]] = None
    tool_call_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary for LLM API."""
        result = {
            "role": self.role,
            "content": self.content,
        }
        if self.tool_calls:
            result["tool_calls"] = self.tool_calls
        if self.tool_call_id:
            result["tool_call_id"] = self.tool_call_id
        return result


@dataclass
class SessionState:
    """
    In-memory session state.
    
    This state is maintained per WebSocket connection and provides:
    - Fast access to conversation history
    - Tool invocation tracking
    - Routing decision history
    - Serializable format for persistence
    """
    session_id: str
    user_id: str
    start_time: datetime
    messages: List[Message] = field(default_factory=list)
    tool_outputs: List[Dict[str, Any]] = field(default_factory=list)
    routing_decisions: List[Dict[str, Any]] = field(default_factory=list)
    message_count: int = 0
    tool_call_count: int = 0
    
    def add_message(self, message: Message) -> None:
        """Add a message to the conversation history."""
        self.messages.append(message)
        if message.role == "user":
            self.message_count += 1
    
    def add_tool_output(self, tool_name: str, result: Any) -> None:
        """Record a tool invocation and its result."""
        self.tool_outputs.append({
            "tool": tool_name,
            "result": result,
            "timestamp": datetime.utcnow().isoformat()
        })
        self.tool_call_count += 1
    
    def add_routing_decision(self, decision: Dict[str, Any]) -> None:
        """Record a routing decision for analysis."""
        self.routing_decisions.append({
            **decision,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get formatted conversation history for LLM API."""
        return [msg.to_dict() for msg in self.messages]
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize state to dictionary for persistence."""
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "start_time": self.start_time.isoformat(),
            "message_count": self.message_count,
            "tool_call_count": self.tool_call_count,
            "messages": [msg.to_dict() for msg in self.messages],
            "tool_outputs": self.tool_outputs,
            "routing_decisions": self.routing_decisions
        }


class SessionStateManager:
    """
    Global session state manager.
    
    Thread-safe in-memory storage for active sessions.
    In production, this could be replaced with Redis for distributed systems.
    """
    
    def __init__(self):
        """Initialize the state manager."""
        self._sessions: Dict[str, SessionState] = {}
    
    def create_session(
        self,
        session_id: str,
        user_id: str
    ) -> SessionState:
        """
        Create a new session state.
        
        Args:
            session_id: Unique session identifier
            user_id: User identifier
            
        Returns:
            New SessionState instance
        """
        state = SessionState(
            session_id=session_id,
            user_id=user_id,
            start_time=datetime.utcnow()
        )
        self._sessions[session_id] = state
        return state
    
    def get_session(self, session_id: str) -> Optional[SessionState]:
        """Retrieve session state by ID."""
        return self._sessions.get(session_id)
    
    def remove_session(self, session_id: str) -> Optional[SessionState]:
        """Remove session state (called on disconnect)."""
        return self._sessions.pop(session_id, None)
    
    def has_session(self, session_id: str) -> bool:
        """Check if session exists."""
        return session_id in self._sessions


# Global state manager instance
state_manager = SessionStateManager()

