"""Live chat cog — staff availability and message bridging."""

from datetime import datetime, timedelta

import discord
from discord.ext import commands, tasks

from database.engine import get_session
from database.models import ChatSession, ChatSessionStatus, StaffCheckin, ChatMessage
from bot.formatters.embeds import COLOR_SUCCESS, COLOR_INFO, COLOR_WARN, COLOR_ERROR
from bot.livechat.bridge import (
    is_staff_online, LIVE_CHAT_CATEGORY,
)


CHECKIN_DURATION_MINUTES = 30
INACTIVITY_TIMEOUT_MINUTES = 15


class LiveChatCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.cleanup_loop.start()

    def cog_unload(self):
        self.cleanup_loop.cancel()

    # ── Commands ──────────────────────────────────────────────────

    @commands.command(name="checkin")
    async def check_in(self, ctx: commands.Context, minutes: int = CHECKIN_DURATION_MINUTES):
        """Check in as available for live chat."""
        expires = datetime.utcnow() + timedelta(minutes=minutes)
        with get_session() as session:
            session.query(StaffCheckin).filter_by(
                discord_user_id=str(ctx.author.id)
            ).delete()
            session.add(StaffCheckin(
                discord_user_id=str(ctx.author.id),
                display_name=ctx.author.display_name,
                expires_at=expires,
            ))

        embed = discord.Embed(
            title="Checked In for Live Chat",
            description=(
                f"You are now available for **{minutes} minutes**.\n"
                f"Expires at {expires.strftime('%H:%M UTC')}."
            ),
            color=COLOR_SUCCESS,
        )
        await ctx.send(embed=embed)
        await self._push_staff_status(True)

    @commands.command(name="checkout")
    async def check_out(self, ctx: commands.Context):
        """Check out from live chat availability."""
        with get_session() as session:
            deleted = session.query(StaffCheckin).filter_by(
                discord_user_id=str(ctx.author.id)
            ).delete()

        if deleted:
            await ctx.send("You are now **offline** for live chat.")
        else:
            await ctx.send("You weren't checked in.")

        online = is_staff_online()
        await self._push_staff_status(online)

    @commands.command(name="closechat")
    async def close_chat(self, ctx: commands.Context):
        """Close the current live chat session (run in the chat channel)."""
        session_manager = self.bot.session_manager
        session = session_manager.get_session_by_channel(ctx.channel.id)
        if not session:
            await ctx.send("This channel is not a live chat session.")
            return

        # Notify visitor
        if session.ws and not session.ws.closed:
            await session.ws.send_json({"type": "session_closed"})

        # Update DB
        with get_session() as db:
            chat = db.query(ChatSession).filter_by(
                session_id=session.session_id
            ).first()
            if chat:
                chat.status = ChatSessionStatus.closed
                chat.closed_at = datetime.utcnow()

        session_manager.remove_session(session.session_id)
        await ctx.send("Chat session closed. Channel will be deleted in 10 seconds.")

        import asyncio
        await asyncio.sleep(10)
        try:
            await ctx.channel.delete(reason="Live chat session closed")
        except discord.HTTPException:
            pass

    # ── Listener ──────────────────────────────────────────────────

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Forward staff messages from live chat channels to the browser."""
        if message.author.bot:
            return

        # Only process messages in the Live Chat category
        if not (
            isinstance(message.channel, discord.TextChannel)
            and message.channel.category
            and message.channel.category.name == LIVE_CHAT_CATEGORY
            and message.channel.name.startswith("live-chat-")
        ):
            return

        session_manager = self.bot.session_manager
        session = session_manager.get_session_by_channel(message.channel.id)
        if not session:
            return

        # Cancel the response timer since staff replied
        if session.response_timer_task:
            session.response_timer_task.cancel()
            session.response_timer_task = None

        # Forward to visitor's WebSocket
        if session.ws and not session.ws.closed:
            await session.ws.send_json({
                "type": "message",
                "sender": "staff",
                "name": message.author.display_name,
                "text": message.content,
                "timestamp": datetime.utcnow().isoformat(),
            })

        # Update activity and persist
        session.last_activity = datetime.utcnow()
        with get_session() as db:
            chat = db.query(ChatSession).filter_by(
                session_id=session.session_id
            ).first()
            if chat:
                chat.last_activity = datetime.utcnow()
                chat.status = ChatSessionStatus.active
                if not chat.staff_user_id:
                    chat.staff_user_id = str(message.author.id)
                db.add(ChatMessage(
                    chat_session_id=chat.id,
                    sender_type="staff",
                    sender_name=message.author.display_name,
                    content=message.content,
                ))

    # ── Background cleanup ────────────────────────────────────────

    @tasks.loop(minutes=5)
    async def cleanup_loop(self):
        """Clean up expired checkins and inactive chat sessions."""
        now = datetime.utcnow()

        # Remove expired checkins
        with get_session() as session:
            session.query(StaffCheckin).filter(
                StaffCheckin.expires_at <= now
            ).delete()

        # Close inactive sessions
        cutoff = now - timedelta(minutes=INACTIVITY_TIMEOUT_MINUTES)
        session_manager = self.bot.session_manager
        to_remove = []

        for sid, s in list(session_manager.sessions.items()):
            if s.last_activity < cutoff:
                to_remove.append(sid)
                if s.ws and not s.ws.closed:
                    try:
                        await s.ws.send_json({"type": "session_closed"})
                    except Exception:
                        pass
                if s.discord_channel_id:
                    channel = self.bot.get_channel(s.discord_channel_id)
                    if channel:
                        try:
                            await channel.send("Session timed out due to inactivity.")
                            await channel.delete(reason="Live chat inactivity timeout")
                        except discord.HTTPException:
                            pass

        for sid in to_remove:
            with get_session() as db:
                chat = db.query(ChatSession).filter_by(session_id=sid).first()
                if chat:
                    chat.status = ChatSessionStatus.closed
                    chat.closed_at = now
            session_manager.remove_session(sid)

    @cleanup_loop.before_loop
    async def before_cleanup(self):
        await self.bot.wait_until_ready()

    # ── Helpers ───────────────────────────────────────────────────

    async def _push_staff_status(self, online: bool):
        """Push staff online/offline status to all connected widget clients."""
        session_manager = self.bot.session_manager
        for s in list(session_manager.sessions.values()):
            if s.ws and not s.ws.closed:
                try:
                    await s.ws.send_json({"type": "staff_status", "online": online})
                except Exception:
                    pass


async def setup(bot: commands.Bot):
    await bot.add_cog(LiveChatCog(bot))
