"""Bridge logic between WebSocket visitors and Discord channels."""

import os
from datetime import datetime

import discord
from discord.ext.commands import Bot

from database.engine import get_session
from database.models import (
    ChatSession, ChatMessage, ChatSessionStatus, StaffCheckin,
)
from bot.livechat.session_manager import LiveSession, SessionManager
from bot.formatters.embeds import COLOR_INFO, COLOR_WARN


LIVE_CHAT_CATEGORY = "Live Chat"
OFFLINE_CHANNEL = "offline-messages"


def is_staff_online() -> bool:
    """Check if any staff are currently checked in."""
    now = datetime.utcnow()
    with get_session() as session:
        count = (
            session.query(StaffCheckin)
            .filter(StaffCheckin.expires_at > now)
            .count()
        )
    return count > 0


async def get_or_create_category(guild: discord.Guild) -> discord.CategoryChannel:
    """Find or create the 'Live Chat' category."""
    for cat in guild.categories:
        if cat.name == LIVE_CHAT_CATEGORY:
            return cat
    return await guild.create_category(LIVE_CHAT_CATEGORY)


async def get_or_create_offline_channel(guild: discord.Guild) -> discord.TextChannel:
    """Find or create the #offline-messages channel under Live Chat category."""
    category = await get_or_create_category(guild)
    for ch in category.text_channels:
        if ch.name == OFFLINE_CHANNEL:
            return ch
    return await guild.create_text_channel(OFFLINE_CHANNEL, category=category)


async def create_chat_channel(
    bot: Bot, guild: discord.Guild, session_id: str
) -> discord.TextChannel:
    """Create a new text channel for a live chat session."""
    category = await get_or_create_category(guild)
    channel = await guild.create_text_channel(
        f"live-chat-{session_id}",
        category=category,
        topic=f"Live chat session {session_id}",
    )
    embed = discord.Embed(
        title="New Live Chat",
        description=(
            f"Session **{session_id}** — a visitor started chatting on the website.\n"
            "Reply here and your messages will appear in their chat widget."
        ),
        color=COLOR_INFO,
    )
    embed.set_footer(text="Use !closechat to end this session.")
    await channel.send(embed=embed)
    return channel


async def handle_visitor_message(
    session_manager: SessionManager,
    bot: Bot,
    session: LiveSession,
    text: str,
):
    """Forward a visitor message to the corresponding Discord channel."""
    guild_id = os.getenv("GUILD_ID")
    if not guild_id:
        return
    guild = bot.get_guild(int(guild_id))
    if not guild:
        return

    # Create channel on first message
    if not session.discord_channel_id:
        channel = await create_chat_channel(bot, guild, session.session_id)
        session.discord_channel_id = channel.id
        session.first_message_sent = True

        # Update DB with channel ID
        with get_session() as db:
            chat = db.query(ChatSession).filter_by(
                session_id=session.session_id
            ).first()
            if chat:
                chat.discord_channel_id = str(channel.id)
                chat.status = ChatSessionStatus.waiting
    else:
        channel = bot.get_channel(session.discord_channel_id)
        if not channel:
            return

    # Send message to Discord
    embed = discord.Embed(
        description=text,
        color=0xEF3B38,  # RSC red
    )
    embed.set_author(name="Visitor")
    embed.timestamp = datetime.utcnow()
    await channel.send(embed=embed)

    # Update timestamps
    session.last_activity = datetime.utcnow()
    with get_session() as db:
        chat = db.query(ChatSession).filter_by(
            session_id=session.session_id
        ).first()
        if chat:
            chat.last_activity = datetime.utcnow()
            db.add(ChatMessage(
                chat_session_id=chat.id,
                sender_type="visitor",
                content=text,
            ))


async def handle_offline_message(
    bot: Bot, session: LiveSession, email: str, text: str
):
    """Post an offline message to the #offline-messages channel."""
    guild_id = os.getenv("GUILD_ID")
    if not guild_id:
        return
    guild = bot.get_guild(int(guild_id))
    if not guild:
        return

    channel = await get_or_create_offline_channel(guild)

    embed = discord.Embed(
        title="Offline Message",
        color=COLOR_WARN,
    )
    embed.add_field(name="Email", value=email, inline=False)
    embed.add_field(name="Message", value=text or "(no message)", inline=False)
    embed.set_footer(text=f"Session {session.session_id}")
    embed.timestamp = datetime.utcnow()
    await channel.send(embed=embed)

    # Persist
    with get_session() as db:
        chat = db.query(ChatSession).filter_by(
            session_id=session.session_id
        ).first()
        if chat:
            chat.visitor_email = email
            chat.status = ChatSessionStatus.offline
            if text:
                db.add(ChatMessage(
                    chat_session_id=chat.id,
                    sender_type="visitor",
                    content=text,
                ))


async def post_email_to_channel(
    bot: Bot, session: LiveSession, email: str
):
    """Post the visitor's email in the existing chat channel."""
    if not session.discord_channel_id:
        return
    channel = bot.get_channel(session.discord_channel_id)
    if not channel:
        return

    embed = discord.Embed(
        title="Visitor Left Email",
        description=f"The visitor provided their email for follow-up: **{email}**",
        color=COLOR_WARN,
    )
    await channel.send(embed=embed)

    with get_session() as db:
        chat = db.query(ChatSession).filter_by(
            session_id=session.session_id
        ).first()
        if chat:
            chat.visitor_email = email
