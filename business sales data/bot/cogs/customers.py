"""Customer management commands."""

import discord
from discord.ext import commands

from database.engine import get_session
from database.models import Customer
from bot.flows.customer_flow import CustomerFlow
from bot.formatters.embeds import customer_embed, COLOR_INFO


class CustomersCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="newcustomer")
    async def new_customer(self, ctx: commands.Context):
        """Add a new customer via guided flow."""
        flow = CustomerFlow(ctx)
        await flow.run()

    @commands.command(name="customer")
    async def lookup_customer(self, ctx: commands.Context, *, name: str):
        """Search for a customer by name."""
        with get_session() as session:
            matches = (
                session.query(Customer)
                .filter(Customer.business_name.ilike(f"%{name}%"))
                .limit(10)
                .all()
            )
            if not matches:
                await ctx.send(f"No customers matching **{name}**.")
                return

            for c in matches:
                await ctx.send(embed=customer_embed(c))

    @commands.command(name="customers")
    async def list_customers(self, ctx: commands.Context):
        """List all active customers."""
        with get_session() as session:
            customers = (
                session.query(Customer)
                .filter_by(is_active=True)
                .order_by(Customer.business_name)
                .all()
            )
            if not customers:
                await ctx.send("No customers yet. Use `!newcustomer` to add one.")
                return

            lines = []
            for c in customers:
                lines.append(f"**{c.business_name}** — {c.email} (#{c.id})")

            embed = discord.Embed(
                title=f"Customers ({len(customers)})",
                description="\n".join(lines),
                color=COLOR_INFO,
            )
            await ctx.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(CustomersCog(bot))
