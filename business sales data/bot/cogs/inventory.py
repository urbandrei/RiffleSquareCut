"""Inventory commands: !openbox, !closebox, !stock, !boxstatus, !boxes."""

from datetime import datetime

import discord
from discord.ext import commands

from database.engine import get_session
from database.models import Box, StockTransaction
from bot.flows.stock_flow import StockFlow
from bot.formatters.embeds import box_embed, stock_transaction_embed, COLOR_INFO, COLOR_WARN, COLOR_SUCCESS


class InventoryCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="openbox")
    async def open_box(self, ctx: commands.Context):
        """Open a new box of product. Auto-closes any currently open box."""
        from bot.flows.base import ConversationFlow, FlowCancelled, FlowTimeout

        flow = ConversationFlow(ctx)
        try:
            await ctx.send(
                "**Open New Box** — I'll walk you through it. Type **cancel** at any time."
            )

            def validate_qty(text):
                if not text.isdigit() or int(text) < 1:
                    return "Enter a positive number."
                return None

            qty_str = await flow.ask("How many decks in this box?", validator=validate_qty)
            quantity = int(qty_str)
            notes = await flow.ask("Notes?", optional=True)

            from bot.formatters.embeds import box_summary_embed
            data = {"initial_count": quantity, "notes": notes}
            embed = box_summary_embed(data)
            confirmed = await flow.confirm(embed)

            if not confirmed:
                await ctx.send("Box opening cancelled.")
                return

            with get_session() as session:
                # Auto-close any currently open box
                open_box = session.query(Box).filter_by(is_open=True).first()
                if open_box:
                    open_box.is_open = False
                    open_box.closed_at = datetime.utcnow()
                    closed_id = open_box.id
                    closed_remaining = open_box.current_count
                else:
                    closed_id = None

                new_box = Box(
                    initial_count=quantity,
                    current_count=quantity,
                    is_open=True,
                    notes=notes,
                    opened_at=datetime.utcnow(),
                    recorded_by=str(ctx.author.id),
                )
                session.add(new_box)
                session.flush()
                new_id = new_box.id

            if closed_id:
                await ctx.send(
                    f"Box **#{closed_id}** auto-closed ({closed_remaining} remaining)."
                )
            await ctx.send(
                f"Box **#{new_id}** opened with **{quantity}** decks."
            )

        except (FlowCancelled, FlowTimeout):
            return

    @commands.command(name="closebox")
    async def close_box(self, ctx: commands.Context):
        """Close the currently open box."""
        with get_session() as session:
            box = session.query(Box).filter_by(is_open=True).first()
            if not box:
                await ctx.send("No box is currently open.")
                return
            box.is_open = False
            box.closed_at = datetime.utcnow()
            box_id = box.id
            remaining = box.current_count

        await ctx.send(f"Box **#{box_id}** closed. **{remaining}** decks remaining.")

    @commands.command(name="stock")
    async def stock_transaction(self, ctx: commands.Context):
        """Record a stock transaction (damage, giveaway, adjustment, return)."""
        flow = StockFlow(ctx)
        await flow.run()

    @commands.command(name="boxstatus")
    async def box_status(self, ctx: commands.Context):
        """Show the currently open box and recent transactions."""
        with get_session() as session:
            box = session.query(Box).filter_by(is_open=True).first()
            if not box:
                await ctx.send("No box is currently open.")
                return

            embed = box_embed(box)

            # Recent transactions
            txns = (
                session.query(StockTransaction)
                .filter_by(box_id=box.id)
                .order_by(StockTransaction.created_at.desc())
                .limit(5)
                .all()
            )
            if txns:
                lines = []
                for t in txns:
                    lines.append(
                        f"#{t.id} {t.transaction_type.value} — qty: {t.quantity} — "
                        f"{t.created_at.strftime('%m/%d %H:%M')}"
                    )
                embed.add_field(
                    name="Recent Transactions",
                    value="\n".join(lines),
                    inline=False,
                )

            await ctx.send(embed=embed)

    @commands.command(name="boxes")
    async def list_boxes(self, ctx: commands.Context, n: int = 5):
        """List recent boxes."""
        with get_session() as session:
            boxes = (
                session.query(Box)
                .order_by(Box.created_at.desc())
                .limit(n)
                .all()
            )
            if not boxes:
                await ctx.send("No boxes recorded yet.")
                return

            lines = []
            for b in boxes:
                status = "OPEN" if b.is_open else "closed"
                lines.append(
                    f"**#{b.id}** — {b.current_count}/{b.initial_count} — {status} — "
                    f"{b.created_at.strftime('%Y-%m-%d')}"
                )

            embed = discord.Embed(
                title=f"Recent Boxes ({len(boxes)})",
                description="\n".join(lines),
                color=COLOR_INFO,
            )
            await ctx.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(InventoryCog(bot))
