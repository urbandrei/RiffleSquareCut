"""WebSocket handler for live chat connections from the browser widget."""

import asyncio
import json

import aiohttp
import aiohttp.web

from database.engine import get_session
from database.models import ChatSession, ChatSessionStatus
from bot.livechat.bridge import (
    handle_visitor_message,
    handle_offline_message,
    post_email_to_channel,
    is_staff_online,
)

STAFF_RESPONSE_TIMEOUT = 120  # seconds


async def _start_response_timer(ws, session):
    """Wait for STAFF_RESPONSE_TIMEOUT, then prompt visitor to leave email."""
    try:
        await asyncio.sleep(STAFF_RESPONSE_TIMEOUT)
        if not ws.closed:
            await ws.send_json({"type": "timeout_prompt"})
    except asyncio.CancelledError:
        pass


async def websocket_handler(request):
    ws = aiohttp.web.WebSocketResponse()
    await ws.prepare(request)

    bot = request.app["bot"]
    session_manager = request.app["session_manager"]
    session = None

    async for msg in ws:
        if msg.type == aiohttp.WSMsgType.TEXT:
            try:
                data = json.loads(msg.data)
            except json.JSONDecodeError:
                continue

            action = data.get("action")

            if action == "connect":
                # Reconnect to existing session if possible
                existing_id = data.get("session_id")
                if existing_id:
                    session = session_manager.get_session(existing_id)
                    if session:
                        session.ws = ws

                # Create new session if no reconnect
                if not session:
                    session = session_manager.create_session()
                    session.ws = ws
                    with get_session() as db:
                        db.add(ChatSession(
                            session_id=session.session_id,
                            status=ChatSessionStatus.active,
                        ))

                online = is_staff_online()
                await ws.send_json({
                    "type": "connected",
                    "session_id": session.session_id,
                    "staff_online": online,
                })

            elif action == "message":
                if not session:
                    continue
                text = data.get("text", "").strip()
                if not text:
                    continue

                online = is_staff_online()
                if not online and not session.discord_channel_id:
                    # No staff online and no active channel — queue as pending
                    # The visitor should provide email via the email action
                    session._pending_text = text
                    await ws.send_json({
                        "type": "email_required",
                        "reason": "Our team is currently offline. Leave your email and message and we'll get back to you.",
                    })
                    continue

                await handle_visitor_message(session_manager, bot, session, text)

                # Start response timer (cancel previous if any)
                if session.response_timer_task:
                    session.response_timer_task.cancel()
                session.response_timer_task = asyncio.create_task(
                    _start_response_timer(ws, session)
                )

            elif action == "email":
                if not session:
                    continue
                email = data.get("email", "").strip()
                if not email:
                    continue

                session.visitor_email = email
                pending_text = getattr(session, "_pending_text", "")

                if not session.discord_channel_id:
                    # Offline message — goes to #offline-messages
                    await handle_offline_message(bot, session, email, pending_text)
                    await ws.send_json({
                        "type": "email_confirmed",
                        "message": f"Message sent! We'll get back to you at {email}.",
                    })
                else:
                    # Active session — just attach email to existing channel
                    await post_email_to_channel(bot, session, email)
                    await ws.send_json({
                        "type": "email_confirmed",
                        "message": f"Thanks! We'll follow up at {email} if needed.",
                    })

                session._pending_text = ""

            elif action == "typing":
                # Could forward typing indicator to Discord — skip for MVP
                pass

        elif msg.type in (aiohttp.WSMsgType.ERROR, aiohttp.WSMsgType.CLOSE):
            break

    # Connection closed — detach WebSocket but keep session alive for reconnect
    if session:
        session.ws = None
        if session.response_timer_task:
            session.response_timer_task.cancel()
            session.response_timer_task = None

    return ws
