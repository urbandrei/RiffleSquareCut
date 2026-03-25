"""Query commands: !recent, !search."""

import discord
from discord.ext import commands

from database.engine import get_session
from database.models import Sale, CustomerSale, Customer, Invoice
from bot.formatters.embeds import (
    sale_embed, customer_sale_embed, customer_embed, invoice_embed, COLOR_INFO,
)
from utils.currency import fmt


class QueriesCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="recent")
    async def recent_sales(self, ctx: commands.Context, n: int = 5):
        """Show the N most recent sales (business + customer)."""
        n = min(max(n, 1), 25)
        with get_session() as session:
            business_sales = (
                session.query(Sale)
                .order_by(Sale.sale_date.desc())
                .limit(n)
                .all()
            )
            customer_sales = (
                session.query(CustomerSale)
                .order_by(CustomerSale.sale_date.desc())
                .limit(n)
                .all()
            )

            # Merge into unified list: (sale_date, type, record)
            merged = []
            for s in business_sales:
                cust_name = None
                if s.customer_id:
                    cust = session.query(Customer).get(s.customer_id)
                    cust_name = cust.business_name if cust else None
                merged.append((s.sale_date, "business", s, cust_name))
            for cs in customer_sales:
                merged.append((cs.sale_date, "customer", cs, None))

            merged.sort(key=lambda x: x[0], reverse=True)
            merged = merged[:n]

            if not merged:
                await ctx.send("No sales recorded yet.")
                return

            for sale_date, sale_type, record, cust_name in merged:
                if sale_type == "business":
                    await ctx.send(embed=sale_embed(record, cust_name))
                else:
                    await ctx.send(embed=customer_sale_embed(record))

    @commands.command(name="search")
    async def search(self, ctx: commands.Context, *, query: str):
        """Search customers, invoices, and sales notes."""
        results_found = False

        with get_session() as session:
            # Search customers
            customers = (
                session.query(Customer)
                .filter(Customer.business_name.ilike(f"%{query}%"))
                .limit(3)
                .all()
            )
            for c in customers:
                results_found = True
                await ctx.send(embed=customer_embed(c))

            # Search invoices by number
            invoices = (
                session.query(Invoice)
                .filter(Invoice.invoice_number.ilike(f"%{query}%"))
                .limit(3)
                .all()
            )
            for inv in invoices:
                results_found = True
                cust = session.query(Customer).get(inv.customer_id)
                await ctx.send(embed=invoice_embed(inv, cust.business_name))

            # Search business sale notes
            sales = (
                session.query(Sale)
                .filter(Sale.notes.ilike(f"%{query}%"))
                .limit(3)
                .all()
            )
            for s in sales:
                results_found = True
                cust_name = None
                if s.customer_id:
                    cust = session.query(Customer).get(s.customer_id)
                    cust_name = cust.business_name if cust else None
                await ctx.send(embed=sale_embed(s, cust_name))

            # Search customer sale notes
            cs_results = (
                session.query(CustomerSale)
                .filter(CustomerSale.notes.ilike(f"%{query}%"))
                .limit(3)
                .all()
            )
            for cs in cs_results:
                results_found = True
                await ctx.send(embed=customer_sale_embed(cs))

        if not results_found:
            await ctx.send(f"No results for **{query}**.")


async def setup(bot: commands.Bot):
    await bot.add_cog(QueriesCog(bot))
