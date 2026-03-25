"""Guided note creation flow."""

from database.engine import get_session
from database.models import Note
from bot.flows.base import ConversationFlow, FlowCancelled, FlowTimeout
from bot.formatters.embeds import note_summary_embed


class NoteFlow(ConversationFlow):
    async def run(self) -> Note | None:
        try:
            await self.channel.send(
                "**New Note** — I'll walk you through it. Type **cancel** at any time."
            )

            title = await self.ask("Title?")
            content = await self.ask("Content?", optional=True)

            data = {"title": title, "content": content}
            embed = note_summary_embed(data)
            confirmed = await self.confirm(embed)

            if not confirmed:
                await self.channel.send("Note creation cancelled.")
                return None

            with get_session() as session:
                note = Note(
                    title=title,
                    content=content,
                    created_by=str(self.author.id),
                )
                session.add(note)
                session.flush()
                note_id = note.id

            await self.channel.send(f"Note **#{note_id}** created — *{title}*")
            return note

        except (FlowCancelled, FlowTimeout):
            return None
