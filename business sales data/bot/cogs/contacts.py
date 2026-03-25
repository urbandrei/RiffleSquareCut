"""Contact & conversation commands: !newcontact, !contact, !contacts, !newconvo, !convos, !followups."""

from datetime import date

import discord
from discord.ext import commands

from database.engine import get_session
from database.models import Contact, Conversation
from bot.flows.contact_flow import ContactFlow
from bot.flows.conversation_flow import LogConvoFlow
from bot.formatters.embeds import (
    contact_embed, conversation_embed, COLOR_INFO, COLOR_WARN,
)


class ContactsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="newcontact")
    async def new_contact(self, ctx: commands.Context):
        """Add a new contact (guided flow)."""
        flow = ContactFlow(ctx)
        await flow.run()

    @commands.command(name="contact")
    async def lookup_contact(self, ctx: commands.Context, *, name: str):
        """Search contacts by name."""
        with get_session() as session:
            matches = (
                session.query(Contact)
                .filter(Contact.name.ilike(f"%{name}%"))
                .limit(5)
                .all()
            )
            if not matches:
                await ctx.send(f"No contacts matching **{name}**.")
                return
            for c in matches:
                await ctx.send(embed=contact_embed(c))

    @commands.command(name="contacts")
    async def list_contacts(self, ctx: commands.Context):
        """List all active contacts."""
        with get_session() as session:
            contacts = (
                session.query(Contact)
                .filter(Contact.is_active == True)
                .order_by(Contact.name)
                .all()
            )
            if not contacts:
                await ctx.send("No contacts yet. Use `!newcontact` to add one.")
                return

            lines = []
            for c in contacts:
                org = f" ({c.organization})" if c.organization else ""
                lines.append(f"**#{c.id}** {c.name}{org} — {c.role.value}")

            embed = discord.Embed(
                title=f"Contacts ({len(contacts)})",
                description="\n".join(lines),
                color=COLOR_INFO,
            )
            await ctx.send(embed=embed)

    @commands.command(name="newconvo")
    async def new_conversation(self, ctx: commands.Context):
        """Log a conversation with a contact (guided flow)."""
        flow = LogConvoFlow(ctx)
        await flow.run()

    @commands.command(name="convos")
    async def list_conversations(self, ctx: commands.Context, *, name: str):
        """Show recent conversations for a contact."""
        with get_session() as session:
            contacts = (
                session.query(Contact)
                .filter(Contact.name.ilike(f"%{name}%"))
                .limit(1)
                .all()
            )
            if not contacts:
                await ctx.send(f"No contact matching **{name}**.")
                return

            contact = contacts[0]
            convos = (
                session.query(Conversation)
                .filter_by(contact_id=contact.id)
                .order_by(Conversation.conversation_date.desc())
                .limit(10)
                .all()
            )
            if not convos:
                await ctx.send(f"No conversations logged for **{contact.name}**.")
                return

            for conv in convos:
                await ctx.send(embed=conversation_embed(conv, contact.name))

    @commands.command(name="followups")
    async def follow_ups(self, ctx: commands.Context):
        """List conversations with follow-up dates due today or earlier."""
        today = date.today()
        with get_session() as session:
            convos = (
                session.query(Conversation)
                .filter(Conversation.follow_up_date <= today)
                .order_by(Conversation.follow_up_date)
                .all()
            )
            if not convos:
                await ctx.send("No follow-ups due.")
                return

            lines = []
            for conv in convos:
                contact = session.query(Contact).get(conv.contact_id)
                days = (today - conv.follow_up_date).days
                overdue = f" ({days}d overdue)" if days > 0 else " (today)"
                lines.append(
                    f"**#{conv.id}** {contact.name} — {conv.medium.value} — "
                    f"{conv.follow_up_date}{overdue}"
                )

            embed = discord.Embed(
                title=f"Follow-ups Due ({len(convos)})",
                description="\n".join(lines),
                color=COLOR_WARN,
            )
            await ctx.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(ContactsCog(bot))
