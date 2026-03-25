"""Guided event creation flow."""

from database.engine import get_session
from database.models import Event, EventType
from bot.flows.base import ConversationFlow, FlowCancelled, FlowTimeout
from bot.formatters.embeds import event_summary_embed
from utils.validators import validate_date_input, parse_date_input


EVENT_TYPES = [e.value for e in EventType]


class EventFlow(ConversationFlow):
    async def run(self) -> Event | None:
        try:
            await self.channel.send(
                "**New Event** — I'll walk you through it. Type **cancel** at any time."
            )

            title = await self.ask("Event title?")
            event_type = await self.ask_choice("Event type?", EVENT_TYPES)

            date_str = await self.ask(
                "Event date? (YYYY-MM-DD, today, or tomorrow)",
                validator=validate_date_input,
            )
            event_date = parse_date_input(date_str)

            end_date_str = await self.ask(
                "End date? (for multi-day events)",
                validator=validate_date_input,
                optional=True,
            )
            end_date = parse_date_input(end_date_str) if end_date_str else None

            location = await self.ask("Location?", optional=True)
            description = await self.ask("Description?", optional=True)
            notes = await self.ask("Notes?", optional=True)

            data = {
                "title": title,
                "event_type": event_type,
                "event_date": event_date,
                "end_date": end_date,
                "location": location,
                "description": description,
                "notes": notes,
            }
            embed = event_summary_embed(data)
            confirmed = await self.confirm(embed)

            if not confirmed:
                await self.channel.send("Event creation cancelled.")
                return None

            with get_session() as session:
                event = Event(
                    title=title,
                    event_type=EventType(event_type),
                    event_date=event_date,
                    end_date=end_date,
                    location=location,
                    description=description,
                    notes=notes,
                    created_by=str(self.author.id),
                )
                session.add(event)
                session.flush()
                event_id = event.id

            await self.channel.send(f"Event **#{event_id}** created — *{title}* on {event_date}")
            return event

        except (FlowCancelled, FlowTimeout):
            return None
