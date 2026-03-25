"""Invoice commands: !newinvoice, !invoice, !pay, !overdue, !resendinvoice."""

from datetime import date, datetime

import discord
from discord.ext import commands

from database.engine import get_session
from database.models import (
    Invoice, InvoiceStatus, PaymentMethod, Customer,
)
from bot.flows.invoice_flow import InvoiceFlow
from bot.flows.base import ConfirmView
from bot.formatters.embeds import invoice_embed, COLOR_INFO, COLOR_WARN, COLOR_SUCCESS
from utils.currency import fmt
from utils.email import (
    send_invoice_email,
    extract_customer_data,
    extract_invoice_data,
    extract_line_items_data,
)


class InvoiceActionView(discord.ui.View):
    """Action buttons shown below an invoice: Resend Email, Fix Invoice, Details."""

    def __init__(self, invoice_number: str, author_id: int, cog: "InvoicesCog"):
        super().__init__(timeout=120)
        self.invoice_number = invoice_number
        self.author_id = author_id
        self.cog = cog

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("Not your invoice action.", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Resend Email", style=discord.ButtonStyle.primary, emoji="\u2709")
    async def resend_email(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        success = await self.cog._resend_invoice_email(interaction.channel, self.invoice_number)
        if not success:
            await interaction.channel.send(f"Failed to resend **{self.invoice_number}**. Check logs.")

    @discord.ui.button(label="Fix Invoice", style=discord.ButtonStyle.danger)
    async def fix_invoice(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            f"Cancelling **{self.invoice_number}** and starting a new invoice..."
        )
        with get_session() as session:
            inv = session.query(Invoice).filter_by(invoice_number=self.invoice_number).first()
            if inv and inv.status != InvoiceStatus.cancelled:
                inv.status = InvoiceStatus.cancelled
        self.stop()
        # Start new invoice flow — build a fake context from the interaction
        ctx = await self.cog.bot.get_context(interaction.message)
        ctx.author = interaction.user
        ctx.channel = interaction.channel
        flow = InvoiceFlow(ctx)
        inv_id = await flow.run()
        if inv_id is not None:
            await self.cog._send_new_invoice_email(interaction.channel, inv_id)

    @discord.ui.button(label="Details", style=discord.ButtonStyle.secondary)
    async def details(self, interaction: discord.Interaction, button: discord.ui.Button):
        with get_session() as session:
            inv = session.query(Invoice).filter_by(invoice_number=self.invoice_number).first()
            if not inv:
                await interaction.response.send_message(f"Invoice **{self.invoice_number}** not found.", ephemeral=True)
                return
            cust = session.query(Customer).get(inv.customer_id)
            embed = invoice_embed(inv, cust.business_name)
        await interaction.response.send_message(embed=embed)


class InvoiceSearchView(discord.ui.View):
    """Button menu for !invoice search options."""

    def __init__(self, author_id: int, cog: "InvoicesCog"):
        super().__init__(timeout=60)
        self.author_id = author_id
        self.cog = cog

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("Not your search.", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="By Customer", style=discord.ButtonStyle.primary)
    async def by_customer(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Enter customer name to search:")
        self.stop()

        def check(m):
            return m.author.id == self.author_id and m.channel == interaction.channel

        try:
            msg = await self.cog.bot.wait_for("message", check=check, timeout=60)
        except Exception:
            return
        query = msg.content.strip()
        with get_session() as session:
            invoices = (
                session.query(Invoice)
                .join(Customer)
                .filter(Customer.business_name.ilike(f"%{query}%"))
                .order_by(Invoice.issue_date.desc())
                .limit(10)
                .all()
            )
            if not invoices:
                await interaction.channel.send(f"No invoices found for **{query}**.")
                return
            lines = []
            for inv in invoices:
                cust = session.query(Customer).get(inv.customer_id)
                lines.append(
                    f"**{inv.invoice_number}** — {cust.business_name} — "
                    f"{fmt(inv.total)} — {inv.status.value.upper()}"
                )
            embed = discord.Embed(
                title=f"Invoices matching \"{query}\"",
                description="\n".join(lines),
                color=COLOR_INFO,
            )
            await interaction.channel.send(embed=embed)
            await self._prompt_invoice_selection(interaction.channel)

    @discord.ui.button(label="Recent", style=discord.ButtonStyle.secondary)
    async def recent(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("How many recent invoices? (default: 5)")
        self.stop()

        def check(m):
            return m.author.id == self.author_id and m.channel == interaction.channel

        count = 5
        try:
            msg = await self.cog.bot.wait_for("message", check=check, timeout=30)
            if msg.content.strip().isdigit():
                count = min(int(msg.content.strip()), 25)
        except Exception:
            pass

        with get_session() as session:
            invoices = (
                session.query(Invoice)
                .order_by(Invoice.issue_date.desc())
                .limit(count)
                .all()
            )
            if not invoices:
                await interaction.channel.send("No invoices found.")
                return
            lines = []
            for inv in invoices:
                cust = session.query(Customer).get(inv.customer_id)
                lines.append(
                    f"**{inv.invoice_number}** — {cust.business_name} — "
                    f"{fmt(inv.total)} — {inv.status.value.upper()}"
                )
            embed = discord.Embed(
                title=f"Recent Invoices ({len(invoices)})",
                description="\n".join(lines),
                color=COLOR_INFO,
            )
            await interaction.channel.send(embed=embed)
            await self._prompt_invoice_selection(interaction.channel)

    async def _prompt_invoice_selection(self, channel):
        """After showing a list, prompt user to pick an invoice for actions."""
        await channel.send("Enter an invoice number for actions (or ignore to skip):")

        def check(m):
            return m.author.id == self.author_id and m.channel == channel

        try:
            msg = await self.cog.bot.wait_for("message", check=check, timeout=60)
        except Exception:
            return
        number = msg.content.strip().upper()
        with get_session() as session:
            inv = session.query(Invoice).filter_by(invoice_number=number).first()
            if not inv:
                await channel.send(f"Invoice **{number}** not found.")
                return
            cust = session.query(Customer).get(inv.customer_id)
            view = InvoiceActionView(number, self.author_id, self.cog)
            await channel.send(embed=invoice_embed(inv, cust.business_name), view=view)

    @discord.ui.button(label="By Invoice #", style=discord.ButtonStyle.secondary)
    async def by_number(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Enter invoice number (e.g. RSC-2026-0001):")
        self.stop()

        def check(m):
            return m.author.id == self.author_id and m.channel == interaction.channel

        try:
            msg = await self.cog.bot.wait_for("message", check=check, timeout=60)
        except Exception:
            return
        number = msg.content.strip().upper()
        with get_session() as session:
            inv = session.query(Invoice).filter_by(invoice_number=number).first()
            if not inv:
                await interaction.channel.send(f"Invoice **{number}** not found.")
                return
            cust = session.query(Customer).get(inv.customer_id)
            view = InvoiceActionView(number, self.author_id, self.cog)
            await interaction.channel.send(embed=invoice_embed(inv, cust.business_name), view=view)


class InvoicesCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def _resend_invoice_email(self, channel, invoice_number: str) -> bool:
        """Shared resend logic used by both the command and the action button."""
        with get_session() as session:
            inv = session.query(Invoice).filter_by(invoice_number=invoice_number).first()
            if not inv:
                await channel.send(f"Invoice **{invoice_number}** not found.")
                return False
            customer = session.query(Customer).get(inv.customer_id)
            if not customer:
                await channel.send("Customer not found for this invoice.")
                return False
            cust_data = extract_customer_data(customer)
            inv_data = extract_invoice_data(inv)
            li_data = extract_line_items_data(inv.line_items)

        email_sent = await send_invoice_email(inv_data, cust_data, li_data)
        if email_sent:
            with get_session() as session:
                inv = session.query(Invoice).get(inv_data["id"])
                inv.email_sent_at = datetime.utcnow()
            await channel.send(f"Invoice **{invoice_number}** resent to **{cust_data['email']}**")
            return True
        return False

    async def _send_new_invoice_email(self, channel, inv_id: int):
        """Send email for a newly created invoice (used after Fix Invoice flow)."""
        with get_session() as session:
            inv = session.query(Invoice).get(inv_id)
            if not inv:
                return
            customer = session.query(Customer).get(inv.customer_id)
            if not customer or not customer.email:
                await channel.send("No customer email on file — invoice created but not emailed.")
                return
            inv_data = extract_invoice_data(inv)
            cust_data = extract_customer_data(customer)
            li_data = extract_line_items_data(inv.line_items)

        email_sent = await send_invoice_email(inv_data, cust_data, li_data)
        if email_sent:
            with get_session() as session:
                inv = session.query(Invoice).get(inv_id)
                inv.email_sent_at = datetime.utcnow()
            await channel.send(f"Invoice emailed to **{cust_data['email']}** with PDF attached.")
        else:
            await channel.send("Invoice created but email failed. Use `!resendinvoice` to retry.")

    @commands.command(name="newinvoice")
    async def new_invoice(self, ctx: commands.Context):
        """Create an invoice via guided flow and email it to the customer."""
        flow = InvoiceFlow(ctx)
        inv_id = await flow.run()

        if inv_id is None:
            return

        await self._send_new_invoice_email(ctx.channel, inv_id)

        # Show the invoice with action buttons
        with get_session() as session:
            inv = session.query(Invoice).get(inv_id)
            if inv:
                customer = session.query(Customer).get(inv.customer_id)
                view = InvoiceActionView(inv.invoice_number, ctx.author.id, self)
                await ctx.send(embed=invoice_embed(inv, customer.business_name), view=view)

    @commands.command(name="invoice")
    async def lookup_invoice(self, ctx: commands.Context, *, number: str = None):
        """Look up an invoice. Bare !invoice shows search options."""
        if number:
            # Direct lookup by number
            number = number.strip().upper()
            with get_session() as session:
                inv = session.query(Invoice).filter_by(invoice_number=number).first()
                if not inv:
                    await ctx.send(f"Invoice **{number}** not found.")
                    return
                customer = session.query(Customer).get(inv.customer_id)
                view = InvoiceActionView(number, ctx.author.id, self)
                await ctx.send(embed=invoice_embed(inv, customer.business_name), view=view)
            return

        # Show search menu with buttons
        view = InvoiceSearchView(ctx.author.id, self)
        await ctx.send("**Search Invoices** — choose a method:", view=view)

    @commands.command(name="pay")
    async def pay_invoice(self, ctx: commands.Context, number: str):
        """Record payment for an invoice. Usage: !pay RSC-YYYY-NNNN"""
        number = number.strip().upper()
        with get_session() as session:
            inv = session.query(Invoice).filter_by(invoice_number=number).first()
            if not inv:
                await ctx.send(f"Invoice **{number}** not found.")
                return
            if inv.status == InvoiceStatus.paid:
                await ctx.send(f"Invoice **{number}** is already paid.")
                return
            if inv.status == InvoiceStatus.cancelled:
                await ctx.send(f"Invoice **{number}** is cancelled.")
                return

            inv.status = InvoiceStatus.paid
            inv.paid_date = date.today()
            inv.paid_amount = float(inv.total)

            customer = session.query(Customer).get(inv.customer_id)
            cust_name = customer.business_name

        await ctx.send(
            embed=discord.Embed(
                title=f"Invoice {number} — PAID",
                description=(
                    f"**{cust_name}** — {fmt(inv.total)}\n"
                    f"Paid on {date.today()}"
                ),
                color=COLOR_SUCCESS,
            )
        )

    @commands.command(name="overdue")
    async def overdue_invoices(self, ctx: commands.Context):
        """List overdue invoices."""
        today = date.today()
        with get_session() as session:
            # Auto-mark overdue
            pending = (
                session.query(Invoice)
                .filter(Invoice.status == InvoiceStatus.sent)
                .filter(Invoice.due_date < today)
                .all()
            )
            for inv in pending:
                inv.status = InvoiceStatus.overdue

            overdue = (
                session.query(Invoice)
                .filter(Invoice.status == InvoiceStatus.overdue)
                .order_by(Invoice.due_date)
                .all()
            )

            if not overdue:
                await ctx.send("No overdue invoices.")
                return

            lines = []
            for inv in overdue:
                customer = session.query(Customer).get(inv.customer_id)
                days = (today - inv.due_date).days
                lines.append(
                    f"**{inv.invoice_number}** — {customer.business_name} — "
                    f"{fmt(inv.total)} — {days} days overdue"
                )

            embed = discord.Embed(
                title=f"Overdue Invoices ({len(overdue)})",
                description="\n".join(lines),
                color=COLOR_WARN,
            )
            await ctx.send(embed=embed)

    @commands.command(name="resendinvoice")
    async def resend_invoice(self, ctx: commands.Context, *, number: str):
        """Resend an invoice email. Usage: !resendinvoice RSC-YYYY-NNNN"""
        number = number.strip().upper()
        success = await self._resend_invoice_email(ctx.channel, number)
        if not success:
            await ctx.send(f"Failed to send invoice **{number}**. Check logs.")


async def setup(bot: commands.Bot):
    await bot.add_cog(InvoicesCog(bot))
