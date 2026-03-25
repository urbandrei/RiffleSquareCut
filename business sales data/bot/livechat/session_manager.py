"""In-memory session state for live chat."""

import uuid
from datetime import datetime
from dataclasses import dataclass, field

import aiohttp.web


@dataclass
class LiveSession:
    """Represents an active chat session bridging a browser visitor to Discord."""

    session_id: str
    ws: aiohttp.web.WebSocketResponse | None = None
    discord_channel_id: int | None = None
    visitor_email: str | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_activity: datetime = field(default_factory=datetime.utcnow)
    first_message_sent: bool = False
    response_timer_task: object | None = field(default=None, repr=False)


class SessionManager:
    """Manages the mapping between session IDs, WebSocket connections, and Discord channels."""

    def __init__(self):
        self.sessions: dict[str, LiveSession] = {}

    def create_session(self) -> LiveSession:
        session_id = uuid.uuid4().hex[:8]
        session = LiveSession(session_id=session_id)
        self.sessions[session_id] = session
        return session

    def get_session(self, session_id: str) -> LiveSession | None:
        return self.sessions.get(session_id)

    def get_session_by_channel(self, channel_id: int) -> LiveSession | None:
        for s in self.sessions.values():
            if s.discord_channel_id == channel_id:
                return s
        return None

    def remove_session(self, session_id: str):
        session = self.sessions.pop(session_id, None)
        if session and session.response_timer_task:
            session.response_timer_task.cancel()
