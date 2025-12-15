"""
WebSocket session handler.
Implements real-time bidirectional communication with token-level streaming.
"""

import json
import logging
from typing import Optional
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect, Query
from app.core.state import state_manager, SessionState, Message, EventType
from app.core.routing import analyze_conversation_context, get_system_prompt
from app.llm.client import llm_client
from app.db.client import db_client
from app.tasks.summarization import generate_session_summary
import asyncio

logger = logging.getLogger(__name__)


class WebSocketSessionManager:
    """
    Manages WebSocket connections and session lifecycle.
    
    Handles:
    - Connection establishment
    - Message routing
    - Token streaming
    - Graceful disconnection
    - Post-session processing
    """
    
    def __init__(self):
        """Initialize the WebSocket manager."""
        self.active_connections: dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, session_id: str, user_id: str) -> None:
        """
        Handle new WebSocket connection.
        
        Args:
            websocket: WebSocket connection
            session_id: Session identifier
            user_id: User identifier
        """
        await websocket.accept()
        self.active_connections[session_id] = websocket
        
        # Initialize session state
        state = state_manager.create_session(session_id, user_id)
        
        # Persist session creation
        await db_client.create_session(
            session_id=session_id,
            user_id=user_id,
            start_time=state.start_time
        )
        
        # Log system event
        await db_client.log_event(
            session_id=session_id,
            event_type=EventType.SYSTEM_EVENT.value,
            content="Session started"
        )
        
        logger.info(f"WebSocket connected: session={session_id}, user={user_id}")
    
    async def disconnect(self, session_id: str) -> None:
        """
        Handle WebSocket disconnection.
        
        Args:
            session_id: Session identifier
        """
        if session_id in self.active_connections:
            del self.active_connections[session_id]
        
        # Get session state before removal
        state = state_manager.get_session(session_id)
        
        # Log disconnect event
        await db_client.log_event(
            session_id=session_id,
            event_type=EventType.SYSTEM_EVENT.value,
            content="Session ended"
        )
        
        # Remove from state manager
        state_manager.remove_session(session_id)
        
        # Trigger background summarization (non-blocking)
        asyncio.create_task(generate_session_summary(session_id))
        
        logger.info(f"WebSocket disconnected: session={session_id}")
    
    async def handle_message(self, session_id: str, message: str) -> None:
        """
        Process incoming user message and stream response.
        
        This is the core message handling logic that:
        1. Logs user message
        2. Analyzes conversation context
        3. Routes through LLM with appropriate strategy
        4. Streams tokens incrementally
        5. Handles tool calls
        6. Updates session state
        
        Args:
            session_id: Session identifier
            message: User message content
        """
        websocket = self.active_connections.get(session_id)
        if not websocket:
            logger.warning(f"No active connection for session {session_id}")
            return
        
        state = state_manager.get_session(session_id)
        if not state:
            logger.warning(f"No state found for session {session_id}")
            return
        
        try:
            # Add user message to state
            user_msg = Message(role="user", content=message)
            state.add_message(user_msg)
            
            # Log user message
            await db_client.log_event(
                session_id=session_id,
                event_type=EventType.USER_MESSAGE.value,
                content=message
            )
            
            # Analyze context and determine routing
            routing_decision = analyze_conversation_context(state)
            state.add_routing_decision(routing_decision)
            
            # Get system prompt based on routing
            system_prompt = get_system_prompt(routing_decision)
            
            # Stream LLM response
            accumulated_response = ""
            tool_calls_made = []
            
            async for event in llm_client.stream_response(
                messages=state.get_conversation_history(),
                system_prompt=system_prompt,
                session_id=session_id
            ):
                event_type = event.get("type")
                
                if event_type == "token":
                    # Stream token to client
                    token = event["content"]
                    accumulated_response += token
                    
                    await websocket.send_json({
                        "type": "token",
                        "content": token
                    })
                    
                    # Log token (in production, might batch these)
                    await db_client.log_event(
                        session_id=session_id,
                        event_type=EventType.AI_TOKEN.value,
                        content=token
                    )
                
                elif event_type == "tool_call":
                    # Log tool call
                    tool_name = event["tool"]
                    tool_args = event.get("arguments", {})
                    tool_calls_made.append({"tool": tool_name, "arguments": tool_args})
                    
                    await db_client.log_event(
                        session_id=session_id,
                        event_type=EventType.TOOL_CALL.value,
                        content=json.dumps({"tool": tool_name, "arguments": tool_args})
                    )
                    
                    # Notify client
                    await websocket.send_json({
                        "type": "tool_call",
                        "tool": tool_name,
                        "arguments": tool_args
                    })
                
                elif event_type == "tool_result":
                    # Log tool result
                    tool_name = event["tool"]
                    tool_result = event["result"]
                    state.add_tool_output(tool_name, tool_result)
                    
                    await db_client.log_event(
                        session_id=session_id,
                        event_type=EventType.TOOL_RESULT.value,
                        content=json.dumps({"tool": tool_name, "result": tool_result})
                    )
                    
                    # Notify client
                    await websocket.send_json({
                        "type": "tool_result",
                        "tool": tool_name,
                        "result": tool_result
                    })
                
                elif event_type == "done":
                    # Add assistant message to state
                    if accumulated_response:
                        assistant_msg = Message(role="assistant", content=accumulated_response)
                        state.add_message(assistant_msg)
                    
                    await websocket.send_json({
                        "type": "done"
                    })
                
                elif event_type == "error":
                    await websocket.send_json({
                        "type": "error",
                        "content": event.get("content", "Unknown error")
                    })
        
        except Exception as e:
            logger.error(f"Error handling message for session {session_id}: {e}")
            await websocket.send_json({
                "type": "error",
                "content": f"Error processing message: {str(e)}"
            })


# Global WebSocket manager
ws_manager = WebSocketSessionManager()


async def websocket_endpoint(
    websocket: WebSocket,
    session_id: str,
    user_id: Optional[str] = Query(None)
):
    """
    WebSocket endpoint handler.
    
    This is the main entry point for WebSocket connections.
    
    Args:
        websocket: WebSocket connection
        session_id: Session identifier from path
        user_id: Optional user identifier (defaults to session_id if not provided)
    """
    if not user_id:
        user_id = session_id  # Default to session_id if no user_id provided
    
    await ws_manager.connect(websocket, session_id, user_id)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            
            try:
                message_data = json.loads(data)
                message_content = message_data.get("message", data)
            except json.JSONDecodeError:
                message_content = data
            
            # Handle message
            await ws_manager.handle_message(session_id, message_content)
    
    except WebSocketDisconnect:
        await ws_manager.disconnect(session_id)
    except Exception as e:
        logger.error(f"WebSocket error for session {session_id}: {e}")
        await ws_manager.disconnect(session_id)

