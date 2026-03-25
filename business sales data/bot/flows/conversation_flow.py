"""Guided conversation logging flow."""

from datetime import date

from database.engine import get_session
from database.models import (
    Contact, Conversation, ConversationMedium, ConversationOutcome,
)
from bot.flows.base import ConversationFlow as BaseFlow, FlowCancelled, FlowTimeout
from bot.formatters.embeds import conversation_summary_embed
from utils.validators import validate_date_input, parse_date_input


MEDIUMS = [m.value for m in ConversationMedium]
OUTCOMES = [o.value for o in ConversationOutcome]


class LogConvoFlow(BaseFlow):
    async def run(self) -> Conversation | None:
        try:
            await self.channel.send(
                "**Log Conversation** — I'll walk you through it. Type **cancel** at any time."
            )

            # Step 1: Find contact
            contact_id = None
            contact_name = None

            while contact_id is None:
                search = await self.ask("Contact name? (search)")
                with get_session() as session:
                    matches = (
                        session.query(Contact)
                        .filter(Contact.name.ilike(f"%{search}%"))
                        .filter(Contact.is_active == True)
                        .limit(5)
                        .all()
                    )
                    if not matches:
                        await self.channel.send(
                            "No contacts found. Use `!newcontact` first."
                        )
                        return None
                    if len(matches) == 1:
                        contact_id = matches[0].id
                        contact_name = matches[0].name
                        await self.channel.send(f"Selected: **{contact_name}**")
                    else:
                        names = [m.name for m in matches]
                        chosen = await self.ask_choice("Which contact?", names)
                        for m in matches:
                            if m.name == chosen:
                                contact_id = m.id
                                contact_name = m.name
                                break

            # Step 2: Date
            date_str = await self.ask(
                "Conversation date? (YYYY-MM-DD, today, or tomorrow — default: today)",
                validator=lambda t: None if t.lower() == "today" else validate_date_input(t),
                optional=True,
            )
            if date_str:
                conv_date = parse_date_input(date_str)
            else:
                conv_date = date.today()

            # Step 3: Medium
            medium = await self.ask_choice("Medium?", MEDIUMS)

            # Step 4: Summary
            summary = await self.ask("Summary of the conversation?")

            # Step 5: Outcome
            outcome = await self.ask_choice("Outcome?", OUTCOMES)

            # Step 6: Follow-up date
            follow_up_str = await self.ask(
                "Follow-up date? (YYYY-MM-DD, today, or tomorrow)",
                validator=validate_date_input,
                optional=True,
            )
            follow_up_date = parse_date_input(follow_up_str) if follow_up_str else None

            # Step 7: Notes
            notes = await self.ask("Notes?", optional=True)

            # Confirm
            data = {
                "contact_name": contact_name,
                "conversation_date": conv_date,
                "medium": medium,
                "summary": summary,
                "outcome": outcome,
                "follow_up_date": follow_up_date,
                "notes": notes,
            }
            embed = conversation_summary_embed(data)
            confirmed = await self.confirm(embed)

            if not confirmed:
                await self.channel.send("Conversation logging cancelled.")
                return None

            with get_session() as session:
                conv = Conversation(
                    contact_id=contact_id,
                    conversation_date=conv_date,
                    medium=ConversationMedium(medium),
                    summary=summary,
                    outcome=ConversationOutcome(outcome),
                    follow_up_date=follow_up_date,
                    notes=notes,
                    recorded_by=str(self.author.id),
                )
                session.add(conv)
                session.flush()
                conv_id = conv.id

            await self.channel.send(
                f"Conversation **#{conv_id}** logged with **{contact_name}**."
            )
            return conv

        except (FlowCancelled, FlowTimeout):
            return None
