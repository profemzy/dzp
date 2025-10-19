"""
Session management for API conversations
"""

import time
import uuid
from datetime import datetime
from typing import Dict, List, Optional

from src.api.models import ChatMessage, SessionInfo, ConversationHistory
from src.core.logger import get_logger

logger = get_logger(__name__)


class SessionManager:
    """Manages conversation sessions for the API"""

    def __init__(self):
        self.sessions: Dict[str, Dict] = {}
        self.session_timeout = 3600  # 1 hour in seconds

    def create_session(self) -> str:
        """Create a new session and return session ID"""
        session_id = str(uuid.uuid4())
        now = datetime.now()
        
        self.sessions[session_id] = {
            "session_id": session_id,
            "created_at": now,
            "last_activity": now,
            "messages": [],
            "status": "active",
            "conversation_history": []
        }
        
        logger.info(f"Created new session: {session_id}")
        return session_id

    def get_session(self, session_id: str) -> Optional[Dict]:
        """Get session by ID"""
        return self.sessions.get(session_id)

    def update_session_activity(self, session_id: str) -> bool:
        """Update last activity time for a session"""
        if session_id in self.sessions:
            self.sessions[session_id]["last_activity"] = datetime.now()
            return True
        return False

    def add_message(self, session_id: str, role: str, content: str) -> bool:
        """Add a message to the session"""
        if session_id not in self.sessions:
            return False

        message = ChatMessage(
            role=role,
            content=content,
            timestamp=datetime.now()
        )

        self.sessions[session_id]["messages"].append(message.dict())
        self.sessions[session_id]["last_activity"] = datetime.now()
        
        # Also update conversation history for agent compatibility
        self.sessions[session_id]["conversation_history"].append({
            "role": role,
            "content": content
        })
        
        logger.debug(f"Added {role} message to session {session_id}")
        return True

    def get_messages(self, session_id: str) -> List[ChatMessage]:
        """Get all messages for a session"""
        if session_id not in self.sessions:
            return []

        messages_data = self.sessions[session_id]["messages"]
        return [ChatMessage(**msg) for msg in messages_data]

    def get_conversation_history(self, session_id: str) -> List[Dict[str, str]]:
        """Get conversation history in agent-compatible format"""
        if session_id not in self.sessions:
            return []

        return self.sessions[session_id]["conversation_history"]

    def get_session_info(self, session_id: str) -> Optional[SessionInfo]:
        """Get session information"""
        if session_id not in self.sessions:
            return None

        session = self.sessions[session_id]
        return SessionInfo(
            session_id=session["session_id"],
            created_at=session["created_at"],
            last_activity=session["last_activity"],
            message_count=len(session["messages"]),
            status=session["status"]
        )

    def get_conversation_history_model(self, session_id: str) -> Optional[ConversationHistory]:
        """Get conversation history as a model"""
        if session_id not in self.sessions:
            return None

        session = self.sessions[session_id]
        messages = [ChatMessage(**msg) for msg in session["messages"]]
        
        return ConversationHistory(
            session_id=session["session_id"],
            messages=messages,
            created_at=session["created_at"],
            last_activity=session["last_activity"]
        )

    def cleanup_expired_sessions(self) -> int:
        """Remove expired sessions and return count of cleaned up sessions"""
        now = datetime.now()
        expired_sessions = []
        
        for session_id, session in self.sessions.items():
            last_activity = session["last_activity"]
            age_seconds = (now - last_activity).total_seconds()
            
            if age_seconds > self.session_timeout:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            del self.sessions[session_id]
            logger.info(f"Cleaned up expired session: {session_id}")
        
        return len(expired_sessions)

    def delete_session(self, session_id: str) -> bool:
        """Delete a session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"Deleted session: {session_id}")
            return True
        return False

    def get_all_sessions(self) -> List[SessionInfo]:
        """Get information about all active sessions"""
        return [
            SessionInfo(
                session_id=session["session_id"],
                created_at=session["created_at"],
                last_activity=session["last_activity"],
                message_count=len(session["messages"]),
                status=session["status"]
            )
            for session in self.sessions.values()
        ]

    def get_session_count(self) -> int:
        """Get total number of active sessions"""
        return len(self.sessions)

    def update_agent_conversation_history(self, session_id: str, history: List[Dict[str, str]]) -> bool:
        """Update conversation history from agent (for synchronization)"""
        if session_id not in self.sessions:
            return False

        # Update the conversation history
        self.sessions[session_id]["conversation_history"] = history
        
        # Also update messages list
        messages = []
        for msg in history:
            messages.append(ChatMessage(
                role=msg["role"],
                content=msg["content"],
                timestamp=datetime.now()  # Use current time as fallback
            ).dict())
        
        self.sessions[session_id]["messages"] = messages
        self.sessions[session_id]["last_activity"] = datetime.now()
        
        return True

    def set_session_status(self, session_id: str, status: str) -> bool:
        """Set session status"""
        if session_id not in self.sessions:
            return False

        self.sessions[session_id]["status"] = status
        logger.debug(f"Set session {session_id} status to {status}")
        return True
