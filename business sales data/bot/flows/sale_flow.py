"""Guided sale recording flow with business / customer branching."""

from datetime import date, datetime
from decimal import Decimal

from database.engine import get_session
from database.models import (
    Customer, Product, Sale, SaleItem, CustomerSale,
    Invoice, InvoiceLineItem, InvoiceStatus,
    SaleChannel, PaymentMethod, PaymentStatus,
    Box, StockTransaction, StockTransactionType,
    BusinessStockCheck,
)
from bot.flows.base import ConversationFlow, FlowCancelled, FlowTimeout
from bot.formatters.embeds import sale_summary_embed, customer_sale_summary_embed, stock_check_summary_embed
from utils.currency import to_decimal
from utils.invoice_numbers import next_invoice_number
from utils.email import (
    send_invoice_email,
    extract_customer_data,
    extract_invoice_data,
    extract_line_items_data,
)


BUSINESS_UNIT_PRICE = 10.00
BUSINESS_PAYMENT_METHODS = ["cash", "card", "check", "online", "other"]

CUSTOMER_UNIT_PRICE = 20.00
CUSTOMER_PAYMENT_METHODS = ["cash", "card", "venmo", "paypal", "cashapp", "other"]
CUSTOMER_CHANNELS = ["in_person", "online", "convention", "meetup", "etsy", "ebay", "other"]


class SaleFlow(ConversationFlow):
    async def run(self) -> Sale | CustomerSale | None:
        try:
            await self.channel.send(
                "**Record a Sale** — I'll walk you through it. Type **cancel** at any time."
            )

            # Step 0: Business or Customer?
            sale_type = await self.ask_choice(
                "Business or Customer sale?", ["business", "customer"]
            )

            if sale_type == "customer":
                return await self._customer_flow()

            return await self._business_flow()

        except (FlowCancelled, FlowTimeout):
            return None

    async def _auto_deduct_stock(
        self, quantity: int, *, sale_id: int | None = None, customer_sale_id: int | None = None,
    ) -> str | None:
        """Deduct stock from the open box after a sale. Returns a message string."""
        with get_session() as session:
            box = session.query(Box).filter_by(is_open=True).first()
            if not box:
                return "⚠ No open box — stock not deducted."
            if box.current_count < quantity:
                return (
                    f"⚠ Box #{box.id} has {box.current_count} decks but "
                    f"{quantity} sold. Stock not deducted."
                )
            box.current_count -= quantity
            txn = StockTransaction(
                box_id=box.id,
                transaction_type=StockTransactionType.sale,
                quantity=quantity,
                sale_id=sale_id,
                customer_sale_id=customer_sale_id,
                recorded_by=str(self.author.id),
            )
            session.add(txn)
            remaining = box.current_count
        return f"📦 Deducted {quantity} from Box #{box.id} — {remaining} remaining."

    async def _resolve_other(self, choice: str, field_label: str, notes: str | None) -> tuple[str, str | None]:
        """If choice is 'other', prompt for details and prepend to notes."""
        if choice != "other":
            return choice, notes

        detail = await self.ask(f"Please specify the {field_label}:")
        prefix = f"[{field_label}: {detail}]"
        if notes:
            notes = f"{prefix} {notes}"
        else:
            notes = prefix
        return choice, notes

    async def _customer_flow(self) -> CustomerSale | None:
        # Step 1: Sale channel
        channel = await self.ask_choice("Sale channel?", CUSTOMER_CHANNELS)

        # Step 2: Quantity
        def validate_qty(text):
            if not text.isdigit() or int(text) < 1:
                return "Enter a positive number."
            return None

        qty_str = await self.ask(
            f"How many decks? (unit price: ${CUSTOMER_UNIT_PRICE:.2f})",
            validator=validate_qty,
        )
        quantity = int(qty_str)

        # Step 3: Payment method
        payment_method = await self.ask_choice(
            "Payment method?", CUSTOMER_PAYMENT_METHODS
        )

        # Step 4: ZIP code (optional)
        zip_code = await self.ask("ZIP code? (for tax purposes)", optional=True)

        # Step 5: Notes (optional)
        notes = await self.ask("Notes?", optional=True)

        # Step 6: Resolve "other" for channel and payment
        channel, notes = await self._resolve_other(channel, "sale channel", notes)
        payment_method, notes = await self._resolve_other(payment_method, "payment method", notes)

        # Step 7: Calculate total
        total = quantity * CUSTOMER_UNIT_PRICE

        # Step 8: Summary & confirm
        data = {
            "channel": channel,
            "payment_method": payment_method,
            "quantity": quantity,
            "unit_price": CUSTOMER_UNIT_PRICE,
            "total": total,
            "zip_code": zip_code,
            "notes": notes,
        }
        embed = customer_sale_summary_embed(data)
        confirmed = await self.confirm(embed)

        if not confirmed:
            await self.channel.send("Sale cancelled.")
            return None

        # Step 9: Save
        with get_session() as session:
            cs = CustomerSale(
                quantity=quantity,
                unit_price=CUSTOMER_UNIT_PRICE,
                total=total,
                channel=SaleChannel(channel),
                payment_method=PaymentMethod(payment_method),
                zip_code=zip_code,
                notes=notes,
                recorded_by=str(self.author.id),
            )
            session.add(cs)
            session.flush()
            cs_id = cs.id

        await self.channel.send(f"Customer Sale **#C{cs_id}** recorded — **${total:.2f}**")
        stock_msg = await self._auto_deduct_stock(quantity, customer_sale_id=cs_id)
        if stock_msg:
            await self.channel.send(stock_msg)
        return cs

    async def _business_flow(self) -> Sale | None:
        # Step 1: Customer search (required — no walk-in)
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

        # Step 2: Stock check — how many decks on the shelf?
        def validate_stock(text):
            if not text.isdigit():
                return "Enter a non-negative integer."
            if int(text) < 0:
                return "Enter a non-negative integer."
            return None

        stock_str = await self.ask(
            "How many decks do they currently have on the shelf?",
            validator=validate_stock,
        )
        observed_stock = int(stock_str)

        # Get the default product
        with get_session() as session:
            product = session.query(Product).filter_by(sku="HM-001").first()
            product_id = product.id

        # Step 3: Quantity (0 allowed for stock check only)
        def validate_qty(text):
            if not text.isdigit():
                return "Enter a non-negative integer."
            if int(text) < 0:
                return "Enter a non-negative integer."
            return None

        qty_str = await self.ask(
            f"How many decks are you selling? (enter 0 for stock check only, "
            f"unit price: ${BUSINESS_UNIT_PRICE:.2f})",
            validator=validate_qty,
        )
        quantity = int(qty_str)

        # ── Stock check only (qty == 0) ──────────────────────────────
        if quantity == 0:
            notes = await self.ask("Notes?", optional=True)

            data = {
                "customer_name": customer_name,
                "observed_stock": observed_stock,
                "notes": notes,
            }
            embed = stock_check_summary_embed(data)
            confirmed = await self.confirm(embed)

            if not confirmed:
                await self.channel.send("Stock check cancelled.")
                return None

            with get_session() as session:
                stock_check = BusinessStockCheck(
                    customer_id=customer_id,
                    observed_stock=observed_stock,
                    adjusted_stock=observed_stock,
                    notes=notes,
                    recorded_by=str(self.author.id),
                )
                session.add(stock_check)

                cust = session.query(Customer).get(customer_id)
                cust.current_stock = observed_stock

            await self.channel.send(
                f"Stock check recorded for **{customer_name}** — "
                f"**{observed_stock}** decks on shelf."
            )
            return None

        # ── Normal sale (qty > 0) ────────────────────────────────────
        # Step 4: Demo copies
        demo_copies = await self._ask_demo_copies(quantity)

        # Step 5: Amount verification
        expected = (quantity - demo_copies) * BUSINESS_UNIT_PRICE

        def validate_amount(text):
            if text.lower() == "skip":
                return None
            try:
                val = to_decimal(text)
                if val <= 0:
                    return "Amount must be positive."
            except Exception:
                return "Enter a valid dollar amount or **skip**."
            return None

        amount_input = await self.ask(
            f"Expected amount: **${expected:.2f}**. Does this match? "
            f"(type **skip** if correct, or enter actual amount)",
            validator=validate_amount,
        )
        if amount_input and amount_input.lower() != "skip":
            actual_amount = float(to_decimal(amount_input))
        else:
            actual_amount = expected

        # Step 6: Payment method
        payment_method = await self.ask_choice(
            "Payment method?", BUSINESS_PAYMENT_METHODS
        )

        # Step 7: Notes (optional)
        notes = await self.ask("Notes?", optional=True)

        # Step 7b: Resolve "other" for payment method
        payment_method, notes = await self._resolve_other(payment_method, "payment method", notes)

        # Step 8: Summary & confirm
        discount = demo_copies * BUSINESS_UNIT_PRICE
        subtotal = expected
        total = actual_amount
        adjusted_stock = observed_stock + quantity

        data = {
            "customer_name": customer_name,
            "quantity": quantity,
            "unit_price": BUSINESS_UNIT_PRICE,
            "demo_copies": demo_copies,
            "channel": "business",
            "payment_method": payment_method,
            "discount": discount,
            "subtotal": subtotal,
            "total": total,
            "observed_stock": observed_stock,
            "adjusted_stock": adjusted_stock,
            "notes": notes,
        }
        embed = sale_summary_embed(data)
        confirmed = await self.confirm(embed)

        if not confirmed:
            await self.channel.send("Sale cancelled.")
            return None

        # Save sale + auto-create invoice + stock check
        inv_number = next_invoice_number()
        with get_session() as session:
            sale = Sale(
                customer_id=customer_id,
                channel=SaleChannel.business,
                payment_method=PaymentMethod(payment_method),
                payment_status=PaymentStatus.completed,
                subtotal=subtotal,
                tax=0,
                discount=discount,
                total=total,
                notes=notes,
                recorded_by=str(self.author.id),
            )
            session.add(sale)
            session.flush()

            item = SaleItem(
                sale_id=sale.id,
                product_id=product_id,
                quantity=quantity,
                unit_price=BUSINESS_UNIT_PRICE,
                line_total=BUSINESS_UNIT_PRICE * quantity,
            )
            session.add(item)
            session.flush()

            # Create Invoice
            invoice = Invoice(
                invoice_number=inv_number,
                customer_id=customer_id,
                status=InvoiceStatus.paid,
                subtotal=subtotal,
                tax=0,
                discount=discount,
                total=total,
                payment_terms="Due on Receipt",
                due_date=date.today(),
                paid_date=date.today(),
                paid_amount=total,
                payment_method=PaymentMethod(payment_method),
                notes=notes,
                created_by=str(self.author.id),
            )
            session.add(invoice)
            session.flush()

            sale.invoice_id = invoice.id

            inv_line = InvoiceLineItem(
                invoice_id=invoice.id,
                product_id=product_id,
                description=f"Hidden Marks x{quantity}",
                quantity=quantity,
                unit_price=BUSINESS_UNIT_PRICE,
                line_total=BUSINESS_UNIT_PRICE * quantity,
            )
            session.add(inv_line)
            session.flush()

            # Save stock check linked to this sale
            stock_check = BusinessStockCheck(
                customer_id=customer_id,
                observed_stock=observed_stock,
                adjusted_stock=adjusted_stock,
                sale_id=sale.id,
                notes=notes,
                recorded_by=str(self.author.id),
            )
            session.add(stock_check)

            cust = session.query(Customer).get(customer_id)
            cust.current_stock = adjusted_stock

            sale_id = sale.id

            # Extract data dicts before session closes
            cust_data = extract_customer_data(cust)
            inv_data = extract_invoice_data(invoice)
            li_data = extract_line_items_data(invoice.line_items)

        await self.channel.send(
            f"Sale **#{sale_id}** recorded — **${total:.2f}**\n"
            f"Invoice **{inv_number}** created (paid)"
        )
        stock_msg = await self._auto_deduct_stock(quantity, sale_id=sale_id)
        if stock_msg:
            await self.channel.send(stock_msg)

        # Send invoice email
        email_sent = await send_invoice_email(inv_data, cust_data, li_data)
        if email_sent:
            with get_session() as session:
                inv = session.query(Invoice).get(inv_data["id"])
                inv.email_sent_at = datetime.utcnow()
            await self.channel.send(f"Invoice emailed to **{cust_data['email']}**")
        else:
            await self.channel.send(
                "Invoice created but email could not be sent."
            )

        return sale

    async def _ask_demo_copies(self, quantity: int) -> int:
        """Ask how many demo copies are included. Returns the count."""

        def validate_demo(text):
            lower = text.lower().strip()
            if lower in ("no", "skip", "0"):
                return None
            if lower in ("yes", "1"):
                return None
            if text.isdigit():
                val = int(text)
                if val < 0:
                    return "Can't be negative."
                if val >= quantity:
                    return f"Demo copies must be less than quantity ({quantity})."
                return None
            return "Enter **yes**, **no**, or a number."

        raw = await self.ask("Demo copies included?", validator=validate_demo)
        lower = raw.lower().strip()

        if lower in ("no", "skip", "0"):
            return 0
        if lower in ("yes", "1"):
            if 1 >= quantity:
                await self.channel.send(
                    f"Demo copies must be less than quantity ({quantity}). Setting to 0."
                )
                return 0
            return 1
        return int(raw)
