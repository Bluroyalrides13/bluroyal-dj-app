"""
WebSocket for Real-time Chat
Handles WebSocket connections for live chat with the AI agent
"""

import logging
import json
from fastapi import WebSocket, WebSocketDisconnect
from typing import Set

from src.agent.chat_interface import ChatInterface
from src.models.schemas import ChatMessage

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections"""
    
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self.chat_interface = ChatInterface()
    
    async def connect(self, websocket: WebSocket):
        """Accept a new WebSocket connection"""
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"Client connected. Total connections: {len(self.active_connections)}")
    
    async def disconnect(self, websocket: WebSocket):
        """Remove a disconnected WebSocket"""
        self.active_connections.discard(websocket)
        logger.info(f"Client disconnected. Total connections: {len(self.active_connections)}")
    
    async def process_message(self, websocket: WebSocket, data: dict):
        """
        Process incoming WebSocket message and send agent response
        
        Expected data format:
        {
            "type": "chat",
            "message": "Hello, I need a ride",
            "session_id": "optional-session-id"
        }
        """
        
        try:
            msg_type = data.get("type", "chat")
            
            if msg_type == "chat":
                # Process chat message
                message_text = data.get("message")
                session_id = data.get("session_id")
                
                if not message_text:
                    await websocket.send_json({
                        "type": "error",
                        "error": "Message is required"
                    })
                    return
                
                # Create ChatMessage
                chat_msg = ChatMessage(
                    message=message_text,
                    session_id=session_id
                )
                
                # Process through agent
                response = self.chat_interface.process_message(chat_msg)
                
                # Send response back to client
                await websocket.send_json({
                    "type": "response",
                    "response": response.response,
                    "session_id": response.session_id,
                    "lead_score": response.lead_score,
                    "conversation_state": response.conversation_state,
                    "extracted_data": response.extracted_data
                })
            
            elif msg_type == "end_session":
                # End conversation and create lead if qualified
                session_id = data.get("session_id")
                lead_id = self.chat_interface.end_conversation(session_id)
                
                await websocket.send_json({
                    "type": "session_ended",
                    "lead_id": lead_id,
                    "message": "Chat session ended"
                })
            
            else:
                await websocket.send_json({
                    "type": "error",
                    "error": f"Unknown message type: {msg_type}"
                })
        
        except Exception as e:
            logger.error(f"Error processing WebSocket message: {e}")
            await websocket.send_json({
                "type": "error",
                "error": "Error processing message"
            })


# Global connection manager instance
manager = ConnectionManager()


def setup_websocket(app):
    """Set up WebSocket routes on FastAPI app"""
    
    @app.websocket("/ws/chat/{session_id}")
    async def websocket_endpoint(websocket: WebSocket, session_id: str):
        """WebSocket endpoint for real-time chat"""
        
        await manager.connect(websocket)
        
        try:
            while True:
                # Receive message from client
                data = await websocket.receive_text()
                
                try:
                    message_data = json.loads(data)
                except json.JSONDecodeError:
                    await websocket.send_json({
                        "type": "error",
                        "error": "Invalid JSON format"
                    })
                    continue
                
                # Ensure session_id is set
                message_data["session_id"] = session_id
                
                # Process message
                await manager.process_message(websocket, message_data)
        
        except WebSocketDisconnect:
            await manager.disconnect(websocket)
            logger.info(f"WebSocket disconnected for session {session_id}")
        
        except Exception as e:
            logger.error(f"WebSocket error for session {session_id}: {e}")
            await manager.disconnect(websocket)
