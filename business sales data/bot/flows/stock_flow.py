"""Guided stock transaction flow (damage, giveaway, adjustment, return)."""

from datetime import datetime

from database.engine import get_session
from database.models import Box, StockTransaction, StockTransactionType
from bot.flows.base import ConversationFlow, FlowCancelled, FlowTimeout
from bot.formatters.embeds import stock_summary_embed


STOCK_TYPES = ["damage", "giveaway", "adjustment", "return"]


class StockFlow(ConversationFlow):
    async def run(self) -> StockTransaction | None:
        try:
            # Check for open box
            with get_session() as session:
                box = session.query(Box).filter_by(is_open=True).first()
                if not box:
                    await self.channel.send(
                        "No box is currently open. Use `!openbox` first."
                    )
                    return None
                box_id = box.id
                box_current = box.current_count

            await self.channel.send(
                f"**Stock Transaction** — Box #{box_id} ({box_current} remaining). "
                "Type **cancel** at any time."
            )

            # Step 1: Transaction type
            txn_type = await self.ask_choice("Transaction type?", STOCK_TYPES)

            # Step 2: Quantity
            adds_stock = txn_type in ("adjustment", "return")

            def validate_qty(text):
                # Allow negative for adjustments
                if txn_type == "adjustment":
                    try:
                        val = int(text)
                    except ValueError:
                        return "Enter a whole number (positive to add, negative to remove)."
                    return None
                if not text.isdigit() or int(text) < 1:
                    return "Enter a positive number."
                return None

            if txn_type == "adjustment":
                prompt = "Quantity? (positive to add, negative to remove)"
            elif adds_stock:
                prompt = "How many decks to return?"
            else:
                prompt = "How many decks?"

            qty_str = await self.ask(prompt, validator=validate_qty)
            quantity = int(qty_str)

            # For non-adjustment types, check stock availability on deductions
            if not adds_stock:
                with get_session() as session:
                    box = session.query(Box).get(box_id)
                    if box.current_count < quantity:
                        await self.channel.send(
                            f"Box #{box_id} only has {box.current_count} decks. "
                            f"Cannot deduct {quantity}."
                        )
                        return None

            # Step 3: Notes
            notes = await self.ask("Notes?", optional=True)

            # Step 4: Confirm
            data = {
                "transaction_type": txn_type,
                "quantity": quantity,
                "box_id": box_id,
                "notes": notes,
            }
            embed = stock_summary_embed(data)
            confirmed = await self.confirm(embed)

            if not confirmed:
                await self.channel.send("Stock transaction cancelled.")
                return None

            # Save
            with get_session() as session:
                box = session.query(Box).get(box_id)

                # Map string to enum
                type_map = {
                    "damage": StockTransactionType.damage,
                    "giveaway": StockTransactionType.giveaway,
                    "adjustment": StockTransactionType.adjustment,
                    "return": StockTransactionType.return_,
                }

                if txn_type == "adjustment":
                    box.current_count += quantity
                elif txn_type == "return":
                    box.current_count += quantity
                else:
                    box.current_count -= quantity

                txn = StockTransaction(
                    box_id=box_id,
                    transaction_type=type_map[txn_type],
                    quantity=quantity,
                    notes=notes,
                    recorded_by=str(self.author.id),
                )
                session.add(txn)
                session.flush()
                txn_id = txn.id
                remaining = box.current_count

            await self.channel.send(
                f"Stock transaction **#{txn_id}** recorded ({txn_type}: {quantity}). "
                f"Box #{box_id} now has **{remaining}** decks."
            )
            return txn

        except (FlowCancelled, FlowTimeout):
            return None
