"""!help command — lists all available commands."""

import discord
from discord.ext import commands

from bot.formatters.embeds import COLOR_INFO


COMMANDS_TEXT = """
**Sales**
`!sale` — Record a sale (business or customer)
`!recent [N]` — Show recent N sales (default 5)
`!search <query>` — Search sales, customers, invoices

**Customers**
`!newcustomer` — Add a new customer (guided flow)
`!customer <name>` — Look up a customer
`!customers` — List all customers

**Invoices**
`!newinvoice` — Create an invoice (guided flow)
`!invoice <number>` — Look up an invoice
`!pay <RSC-YYYY-NNNN>` — Record an invoice payment
`!overdue` — List overdue invoices
`!resendinvoice <number>` — Resend an invoice email

**Inventory**
`!openbox` — Open a new box (auto-closes current)
`!closebox` — Close the currently open box
`!stock` — Record stock transaction (damage/giveaway/adjustment/return)
`!boxstatus` — Show open box and recent transactions
`!boxes [N]` — List recent boxes (default 5)

**Contacts**
`!newcontact` — Add a new contact (guided flow)
`!contact <name>` — Search contacts by name
`!contacts` — List all active contacts
`!newconvo` — Log a conversation with a contact
`!convos <name>` — Show recent conversations for a contact
`!followups` — List conversations with follow-ups due

**Notebook**
`!newnote` — Create a new note
`!notes [search]` — List recent notes (optional search)
`!newevent` — Create a new event
`!events` — List all events
`!upcoming [N]` — Show next N upcoming events (default 5)

**Reports**
`!today` — Today's sales summary
`!week` — This week's summary
`!month` — This month's summary
`!revenue [today|week|month]` — Revenue report
`!topcustomers [N]` — Top customers by spend
`!outstanding` — All unpaid/overdue invoices

**Live Chat**
`!checkin [minutes]` — Go online for live chat (default 30 min)
`!checkout` — Go offline for live chat
`!closechat` — Close the current chat session (run in chat channel)
""".strip()


class HelpCmd(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="help")
    async def help_command(self, ctx: commands.Context):
        embed = discord.Embed(
            title="RSC Sales Bot — Commands",
            description=COMMANDS_TEXT,
            color=COLOR_INFO,
        )
        embed.set_footer(text="Type cancel during any flow to abort.")
        await ctx.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(HelpCmd(bot))
