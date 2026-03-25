"""Guided invoice creation flow."""

from datetime import date, timedelta

from database.engine import get_session
from database.models import (
    Customer, Product, Invoice, InvoiceLineItem, InvoiceStatus,
)
from bot.flows.base import ConversationFlow, FlowCancelled, FlowTimeout
from bot.formatters.embeds import invoice_summary_embed
from utils.invoice_numbers import next_invoice_number
from utils.currency import to_decimal


PAYMENT_TERMS_OPTIONS = ["Net 30", "Net 15", "Net 60", "Due on Receipt"]


class InvoiceFlow(ConversationFlow):
    async def run(self) -> int | None:
        try:
            await self.channel.send(
                "**Create Invoice** — I'll walk you through it. Type **cancel** at any time."
            )

            # Step 1: Customer (required for invoices)
            customer_id = None
            customer_name = None

            while customer_id is None:
                cust_input = await self.ask("Customer name? (search)")
                with get_session() as session:
                    matches = (
                        session.query(Customer)
                        .filter(Customer.business_name.ilike(f"%{cust_input}%"))
                        .limit(5)
                        .all()
                    )
                    if not matches:
                        await self.channel.send(
                            "No customers found. Try again or type **cancel**."
                        )
                        continue
                    if len(matches) == 1:
                        customer_id = matches[0].id
                        customer_name = matches[0].business_name
                        await self.channel.send(f"Selected: **{customer_name}**")
                    else:
                        names = [m.business_name for m in matches]
                        chosen = await self.ask_choice("Which customer?", names)
                        for m in matches:
                            if m.business_name == chosen:
                                customer_id = m.id
                                customer_name = m.business_name
                                break

            # Get default product
            with get_session() as session:
                product = session.query(Product).filter_by(sku="HM-001").first()
                default_price = float(product.unit_price)
                product_id = product.id

            # Step 2: Quantity
            def validate_qty(text):
                if not text.isdigit() or int(text) < 1:
                    return "Enter a positive number."
                return None

            qty_str = await self.ask("Quantity?", validator=validate_qty)
            quantity = int(qty_str)

            # Step 3: Unit price
            def validate_price(text):
                try:
                    val = to_decimal(text)
                    if val <= 0:
                        return "Price must be positive."
                except Exception:
                    return "Enter a valid dollar amount."
                return None

            price_input = await self.ask(
                f"Unit price? (default: ${default_price:.2f} — type **default** to use it)",
                validator=lambda t: None if t.lower() == "default" else validate_price(t),
            )
            if price_input.lower() == "default":
                unit_price = default_price
            else:
                unit_price = float(to_decimal(price_input))

            # Step 4: Payment terms
            payment_terms = await self.ask_choice("Payment terms?", PAYMENT_TERMS_OPTIONS)

            # Step 5: Notes
            notes = await self.ask("Notes?", optional=True)

            # Step 6: Payable to (optional)
            payable_to = await self.ask("Payable to? (name for payment)", optional=True)

            # Step 7: Project name (optional)
            project_name = await self.ask("Project name?", optional=True)

            # Step 8: Adjustments (optional, negative for discounts)
            def validate_adjustments(text):
                try:
                    to_decimal(text)
                except Exception:
                    return "Enter a valid dollar amount (negative for discounts, e.g. -100)."
                return None

            adj_input = await self.ask(
                "Adjustments? (negative for discount, e.g. -100)",
                optional=True,
                validator=validate_adjustments,
            )
            adjustments = float(to_decimal(adj_input)) if adj_input else 0

            # Confirm
            line_total = unit_price * quantity
            total = line_total + adjustments
            data = {
                "customer_name": customer_name,
                "quantity": quantity,
                "unit_price": unit_price,
                "payment_terms": payment_terms,
                "notes": notes,
                "payable_to": payable_to,
                "project_name": project_name,
                "adjustments": adjustments,
            }
            embed = invoice_summary_embed(data)
            confirmed = await self.confirm(embed)

            if not confirmed:
                await self.channel.send("Invoice cancelled.")
                return None

            # Calculate due date from payment terms
            terms_days = {"Net 30": 30, "Net 15": 15, "Net 60": 60, "Due on Receipt": 0}
            days = terms_days.get(payment_terms, 30)
            due = date.today() + timedelta(days=days)

            inv_number = next_invoice_number()

            with get_session() as session:
                invoice = Invoice(
                    invoice_number=inv_number,
                    customer_id=customer_id,
                    status=InvoiceStatus.sent,
                    subtotal=line_total,
                    tax=0,
                    discount=0,
                    adjustments=adjustments,
                    total=total,
                    payment_terms=payment_terms,
                    due_date=due,
                    notes=notes,
                    payable_to=payable_to,
                    project_name=project_name,
                    created_by=str(self.author.id),
                )
                session.add(invoice)
                session.flush()

                line = InvoiceLineItem(
                    invoice_id=invoice.id,
                    product_id=product_id,
                    description=f"Hidden Marks x{quantity}",
                    quantity=quantity,
                    unit_price=unit_price,
                    line_total=line_total,
                )
                session.add(line)
                session.flush()
                inv_id = invoice.id

            await self.channel.send(
                f"Invoice **{inv_number}** created — **${total:.2f}** due {due}"
            )
            return inv_id

        except (FlowCancelled, FlowTimeout):
            return None
