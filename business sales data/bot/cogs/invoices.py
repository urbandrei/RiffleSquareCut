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


class InvoicesCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="newinvoice")
    async def new_invoice(self, ctx: commands.Context):
        """Create an invoice via guided flow and email it to the customer."""
        flow = InvoiceFlow(ctx)
        inv_id = await flow.run()

        if inv_id is None:
            return

        # Extract data in a fresh session for email
        with get_session() as session:
            inv = session.query(Invoice).get(inv_id)
            if not inv:
                return
            customer = session.query(Customer).get(inv.customer_id)
            if not customer or not customer.email:
                await ctx.send("No customer email on file — invoice created but not emailed.")
                return

            inv_data = extract_invoice_data(inv)
            cust_data = extract_customer_data(customer)
            li_data = extract_line_items_data(inv.line_items)

        # Send email with PDF attachment
        email_sent = await send_invoice_email(inv_data, cust_data, li_data)

        if email_sent:
            with get_session() as session:
                inv = session.query(Invoice).get(inv_id)
                inv.email_sent_at = datetime.utcnow()
            await ctx.send(f"Invoice emailed to **{cust_data['email']}** with PDF attached.")
        else:
            await ctx.send("Invoice created but email failed. Use `!resendinvoice` to retry.")

    @commands.command(name="invoice")
    async def lookup_invoice(self, ctx: commands.Context, *, number: str):
        """Look up an invoice by number."""
        number = number.strip().upper()
        with get_session() as session:
            inv = session.query(Invoice).filter_by(invoice_number=number).first()
            if not inv:
                await ctx.send(f"Invoice **{number}** not found.")
                return
            customer = session.query(Customer).get(inv.customer_id)
            await ctx.send(embed=invoice_embed(inv, customer.business_name))

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
        with get_session() as session:
            inv = session.query(Invoice).filter_by(invoice_number=number).first()
            if not inv:
                await ctx.send(f"Invoice **{number}** not found.")
                return
            customer = session.query(Customer).get(inv.customer_id)
            if not customer:
                await ctx.send("Customer not found for this invoice.")
                return

            cust_data = extract_customer_data(customer)
            inv_data = extract_invoice_data(inv)
            li_data = extract_line_items_data(inv.line_items)
            last_sent = inv.email_sent_at

        last_sent_str = str(last_sent) if last_sent else "Never"

        # Confirmation prompt
        view = ConfirmView(ctx.author.id)
        msg = await ctx.send(
            f"Resend invoice **{number}** to **{cust_data['email']}**?\n"
            f"Last sent: {last_sent_str}",
            view=view,
        )
        view.message = msg

        try:
            confirmed = await view.result
        except Exception:
            return

        if not confirmed:
            await ctx.send("Resend cancelled.")
            return

        email_sent = await send_invoice_email(inv_data, cust_data, li_data)
        if email_sent:
            with get_session() as session:
                inv = session.query(Invoice).get(inv_data["id"])
                inv.email_sent_at = datetime.utcnow()
            await ctx.send(f"Invoice **{number}** resent to **{cust_data['email']}**")
        else:
            await ctx.send(f"Failed to send invoice **{number}**. Check logs.")


async def setup(bot: commands.Bot):
    await bot.add_cog(InvoicesCog(bot))
