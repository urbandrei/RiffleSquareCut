"""!sale command — record a sale via guided flow."""

from discord.ext import commands

from bot.flows.sale_flow import SaleFlow


class SalesCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="sale")
    async def record_sale(self, ctx: commands.Context):
        """Record a sale (guided flow)."""
        flow = SaleFlow(ctx)
        await flow.run()


async def setup(bot: commands.Bot):
    await bot.add_cog(SalesCog(bot))
