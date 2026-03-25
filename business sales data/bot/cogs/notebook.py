"""Notes & events commands: !newnote, !notes, !newevent, !events, !upcoming."""

from datetime import date

import discord
from discord.ext import commands

from database.engine import get_session
from database.models import Note, Event
from bot.flows.note_flow import NoteFlow
from bot.flows.event_flow import EventFlow
from bot.formatters.embeds import note_embed, event_embed, COLOR_INFO


class NotebookCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="newnote")
    async def new_note(self, ctx: commands.Context):
        """Create a new note (guided flow)."""
        flow = NoteFlow(ctx)
        await flow.run()

    @commands.command(name="notes")
    async def list_notes(self, ctx: commands.Context, *, search: str = None):
        """List recent notes, optionally filtered by search term."""
        with get_session() as session:
            query = session.query(Note)
            if search:
                query = query.filter(
                    Note.title.ilike(f"%{search}%")
                    | Note.content.ilike(f"%{search}%")
                )
            notes = query.order_by(Note.created_at.desc()).limit(10).all()

            if not notes:
                msg = "No notes found."
                if search:
                    msg = f"No notes matching **{search}**."
                await ctx.send(msg)
                return

            for n in notes:
                await ctx.send(embed=note_embed(n))

    @commands.command(name="newevent")
    async def new_event(self, ctx: commands.Context):
        """Create a new event (guided flow)."""
        flow = EventFlow(ctx)
        await flow.run()

    @commands.command(name="events")
    async def list_events(self, ctx: commands.Context):
        """List all events."""
        with get_session() as session:
            events = (
                session.query(Event)
                .order_by(Event.event_date.desc())
                .limit(10)
                .all()
            )
            if not events:
                await ctx.send("No events recorded yet.")
                return

            for e in events:
                await ctx.send(embed=event_embed(e))

    @commands.command(name="upcoming")
    async def upcoming_events(self, ctx: commands.Context, n: int = 5):
        """Show next N upcoming events (default 5)."""
        today = date.today()
        with get_session() as session:
            events = (
                session.query(Event)
                .filter(Event.event_date >= today)
                .order_by(Event.event_date)
                .limit(n)
                .all()
            )
            if not events:
                await ctx.send("No upcoming events.")
                return

            lines = []
            for e in events:
                date_str = str(e.event_date)
                if e.end_date:
                    date_str += f" → {e.end_date}"
                loc = f" @ {e.location}" if e.location else ""
                lines.append(
                    f"**#{e.id}** {e.title} — {e.event_type.value} — {date_str}{loc}"
                )

            embed = discord.Embed(
                title=f"Upcoming Events ({len(events)})",
                description="\n".join(lines),
                color=COLOR_INFO,
            )
            await ctx.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(NotebookCog(bot))
