"""Report commands: !today, !week, !month, !revenue, !topcustomers, !outstanding."""

from datetime import date

import discord
from discord.ext import commands
from sqlalchemy import func

from database.engine import get_session
from database.models import Sale, CustomerSale, Customer, Invoice, InvoiceStatus
from bot.formatters.embeds import report_embed, COLOR_INFO, COLOR_WARN
from bot.formatters.tables import ascii_table
from utils.currency import fmt
from utils.date_helpers import start_of_today, start_of_week, start_of_month, date_range_label


class ReportsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def _period_report(self, ctx: commands.Context, since):
        label = date_range_label(since)
        with get_session() as session:
            b_sales = (
                session.query(Sale)
                .filter(Sale.sale_date >= since)
                .all()
            )
            c_sales = (
                session.query(CustomerSale)
                .filter(CustomerSale.sale_date >= since)
                .all()
            )

            b_count = len(b_sales)
            c_count = len(c_sales)
            count = b_count + c_count

            b_revenue = sum(float(s.total) for s in b_sales)
            c_revenue = sum(float(cs.total) for cs in c_sales)
            total_revenue = b_revenue + c_revenue

            b_units = sum(
                sum(item.quantity for item in s.items)
                for s in b_sales
            )
            c_units = sum(cs.quantity for cs in c_sales)
            total_units = b_units + c_units

        sales_display = f"{count} ({b_count}B / {c_count}C)" if c_count > 0 else str(count)
        fields = {
            "Sales": sales_display,
            "Revenue": fmt(total_revenue),
            "Units Sold": str(total_units),
        }
        await ctx.send(embed=report_embed(f"{label} — Summary", fields))

    @commands.command(name="today")
    async def today_report(self, ctx: commands.Context):
        await self._period_report(ctx, start_of_today())

    @commands.command(name="week")
    async def week_report(self, ctx: commands.Context):
        await self._period_report(ctx, start_of_week())

    @commands.command(name="month")
    async def month_report(self, ctx: commands.Context):
        await self._period_report(ctx, start_of_month())

    @commands.command(name="revenue")
    async def revenue(self, ctx: commands.Context, period: str = "month"):
        """Revenue report for a period: today, week, or month."""
        period_map = {
            "today": start_of_today,
            "week": start_of_week,
            "month": start_of_month,
        }
        start_fn = period_map.get(period.lower())
        if not start_fn:
            await ctx.send("Usage: `!revenue [today|week|month]`")
            return

        since = start_fn()
        label = date_range_label(since)

        with get_session() as session:
            b_sales = (
                session.query(Sale)
                .filter(Sale.sale_date >= since)
                .all()
            )
            c_sales = (
                session.query(CustomerSale)
                .filter(CustomerSale.sale_date >= since)
                .all()
            )

            b_subtotal = sum(float(s.subtotal) for s in b_sales)
            b_discount = sum(float(s.discount) for s in b_sales)
            b_tax = sum(float(s.tax) for s in b_sales)
            b_revenue = sum(float(s.total) for s in b_sales)

            c_revenue = sum(float(cs.total) for cs in c_sales)

            total_gross = b_subtotal + c_revenue
            total_discount = b_discount
            total_tax = b_tax
            total_net = b_revenue + c_revenue

            # Revenue by channel — merge both tables
            by_channel = {}
            for s in b_sales:
                ch = s.channel.value
                by_channel[ch] = by_channel.get(ch, 0) + float(s.total)
            for cs in c_sales:
                ch = cs.channel.value
                by_channel[ch] = by_channel.get(ch, 0) + float(cs.total)

        fields = {
            "Gross": fmt(total_gross),
            "Discounts": fmt(total_discount),
            "Tax Collected": fmt(total_tax),
            "Net Revenue": fmt(total_net),
        }
        embed = report_embed(f"Revenue — {label}", fields)

        if by_channel:
            channel_text = "\n".join(
                f"**{ch}**: {fmt(amt)}" for ch, amt in sorted(by_channel.items(), key=lambda x: -x[1])
            )
            embed.add_field(name="By Channel", value=channel_text, inline=False)

        await ctx.send(embed=embed)

    @commands.command(name="topcustomers")
    async def top_customers(self, ctx: commands.Context, n: int = 5):
        """Top N customers by total spend."""
        n = min(max(n, 1), 25)
        with get_session() as session:
            results = (
                session.query(
                    Customer.business_name,
                    func.sum(Sale.total).label("total_spend"),
                    func.count(Sale.id).label("sale_count"),
                )
                .join(Sale, Sale.customer_id == Customer.id)
                .group_by(Customer.id)
                .order_by(func.sum(Sale.total).desc())
                .limit(n)
                .all()
            )

        if not results:
            await ctx.send("No customer sales data yet.")
            return

        headers = ["Customer", "Total Spend", "Sales"]
        rows = [
            [r.business_name, fmt(r.total_spend), str(r.sale_count)]
            for r in results
        ]
        table = ascii_table(headers, rows)
        await ctx.send(f"**Top {len(results)} Customers**\n{table}")

    @commands.command(name="outstanding")
    async def outstanding(self, ctx: commands.Context):
        """All unpaid/overdue invoices."""
        today = date.today()
        with get_session() as session:
            # Auto-mark overdue
            pending_overdue = (
                session.query(Invoice)
                .filter(Invoice.status == InvoiceStatus.sent)
                .filter(Invoice.due_date < today)
                .all()
            )
            for inv in pending_overdue:
                inv.status = InvoiceStatus.overdue

            unpaid = (
                session.query(Invoice)
                .filter(Invoice.status.in_([InvoiceStatus.sent, InvoiceStatus.overdue, InvoiceStatus.draft]))
                .order_by(Invoice.due_date)
                .all()
            )

            if not unpaid:
                await ctx.send("No outstanding invoices.")
                return

            total_outstanding = sum(float(inv.total) for inv in unpaid)

            lines = []
            for inv in unpaid:
                customer = session.query(Customer).get(inv.customer_id)
                status = inv.status.value.upper()
                due = inv.due_date.isoformat() if inv.due_date else "N/A"
                lines.append(
                    f"**{inv.invoice_number}** — {customer.business_name} — "
                    f"{fmt(inv.total)} — Due: {due} — {status}"
                )

        embed = discord.Embed(
            title=f"Outstanding Invoices ({len(unpaid)})",
            description="\n".join(lines),
            color=COLOR_WARN,
        )
        embed.set_footer(text=f"Total outstanding: {fmt(total_outstanding)}")
        await ctx.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(ReportsCog(bot))
