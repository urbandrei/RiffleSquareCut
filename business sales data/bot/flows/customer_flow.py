"""Guided customer creation flow."""

import re

from database.engine import get_session
from database.models import Customer
from bot.flows.base import ConversationFlow, FlowCancelled, FlowTimeout
from bot.formatters.embeds import customer_embed


EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class CustomerFlow(ConversationFlow):
    async def run(self) -> Customer | None:
        try:
            await self.channel.send(
                "**New Customer** — I'll walk you through it. Type **cancel** at any time."
            )

            business_name = await self.ask("Business name?")

            def validate_email(text):
                if not EMAIL_RE.match(text):
                    return "That doesn't look like a valid email."
                with get_session() as s:
                    if s.query(Customer).filter_by(email=text.lower()).first():
                        return "A customer with that email already exists."
                return None

            email = await self.ask("Email address?", validator=validate_email)
            email = email.lower()

            address_line1 = await self.ask("Address line 1?")
            address_line2 = await self.ask("Address line 2?", optional=True)
            city = await self.ask("City?")
            state = await self.ask("State?")
            zip_code = await self.ask("ZIP code?")
            phone = await self.ask("Phone number?", optional=True)
            tax_id = await self.ask("Tax ID / resale certificate #?", optional=True)
            contact_person = await self.ask("Contact person name?", optional=True)
            notes = await self.ask("Notes?", optional=True)

            customer = Customer(
                business_name=business_name,
                email=email,
                address_line1=address_line1,
                address_line2=address_line2,
                city=city,
                state=state,
                zip_code=zip_code,
                phone=phone,
                tax_id=tax_id,
                contact_person=contact_person,
                notes=notes,
            )

            embed = customer_embed(customer)
            embed.title = "New Customer — Confirm?"
            confirmed = await self.confirm(embed)

            if not confirmed:
                await self.channel.send("Customer creation cancelled.")
                return None

            with get_session() as session:
                session.add(customer)
                session.flush()
                customer_id = customer.id

            with get_session() as session:
                saved = session.query(Customer).get(customer_id)
                await self.channel.send(
                    f"Customer **{saved.business_name}** created (ID: {saved.id}).",
                )
                return saved

        except (FlowCancelled, FlowTimeout):
            return None
