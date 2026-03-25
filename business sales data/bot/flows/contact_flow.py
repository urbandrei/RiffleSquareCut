"""Guided contact creation flow."""

from database.engine import get_session
from database.models import Contact, ContactRole
from bot.flows.base import ConversationFlow, FlowCancelled, FlowTimeout
from bot.formatters.embeds import contact_summary_embed


CONTACT_ROLES = [r.value for r in ContactRole]


class ContactFlow(ConversationFlow):
    async def run(self) -> Contact | None:
        try:
            await self.channel.send(
                "**New Contact** — I'll walk you through it. Type **cancel** at any time."
            )

            name = await self.ask("Contact name?")
            role = await self.ask_choice("Role?", CONTACT_ROLES)
            email = await self.ask("Email?", optional=True)
            phone = await self.ask("Phone?", optional=True)
            organization = await self.ask("Organization?", optional=True)
            notes = await self.ask("Notes?", optional=True)

            data = {
                "name": name,
                "role": role,
                "email": email,
                "phone": phone,
                "organization": organization,
                "notes": notes,
            }
            embed = contact_summary_embed(data)
            confirmed = await self.confirm(embed)

            if not confirmed:
                await self.channel.send("Contact creation cancelled.")
                return None

            with get_session() as session:
                contact = Contact(
                    name=name,
                    role=ContactRole(role),
                    email=email,
                    phone=phone,
                    organization=organization,
                    notes=notes,
                )
                session.add(contact)
                session.flush()
                contact_id = contact.id

            await self.channel.send(
                f"Contact **{name}** created (ID: {contact_id})."
            )
            return contact

        except (FlowCancelled, FlowTimeout):
            return None
