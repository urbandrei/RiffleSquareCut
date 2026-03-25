"""Conversational flow engine — base class for guided multi-step interactions."""

import asyncio
import math
from typing import Callable

import discord
from discord.ext import commands


TIMEOUT = 120  # seconds per step
LABEL_MAX = 80  # Discord button label character limit


class FlowCancelled(Exception):
    pass


class FlowTimeout(Exception):
    pass


# ---------------------------------------------------------------------------
# Button views
# ---------------------------------------------------------------------------

class ChoiceView(discord.ui.View):
    """Paginated button menu for multiple-choice prompts."""

    def __init__(self, choices: list[str], author_id: int, *, page_size: int = 4):
        super().__init__(timeout=TIMEOUT)
        self.choices = choices
        self.author_id = author_id
        self.page_size = page_size
        self.page = 0
        self.total_pages = max(1, math.ceil(len(choices) / page_size))
        self.result: asyncio.Future[str] = asyncio.get_event_loop().create_future()
        self.message: discord.Message | None = None
        self._build_buttons()

    # -- layout -------------------------------------------------------------

    def _build_buttons(self) -> None:
        self.clear_items()
        start = self.page * self.page_size
        page_choices = self.choices[start : start + self.page_size]

        for choice in page_choices:
            label = choice[:LABEL_MAX]
            btn = discord.ui.Button(label=label, style=discord.ButtonStyle.primary, row=0)
            btn.callback = self._make_choice_callback(choice)
            self.add_item(btn)

        if self.total_pages > 1:
            if self.page > 0:
                back_btn = discord.ui.Button(label="Back", style=discord.ButtonStyle.secondary, row=1)
                back_btn.callback = self._back_callback
                self.add_item(back_btn)
            if self.page < self.total_pages - 1:
                more_btn = discord.ui.Button(label="More...", style=discord.ButtonStyle.secondary, row=1)
                more_btn.callback = self._more_callback
                self.add_item(more_btn)

        cancel_btn = discord.ui.Button(label="Cancel", style=discord.ButtonStyle.danger, row=1)
        cancel_btn.callback = self._cancel_callback
        self.add_item(cancel_btn)

    # -- callbacks ----------------------------------------------------------

    def _make_choice_callback(self, choice: str):
        async def callback(interaction: discord.Interaction) -> None:
            if interaction.user.id != self.author_id:
                await interaction.response.send_message("This isn't your flow.", ephemeral=True)
                return
            if not self.result.done():
                self.result.set_result(choice)
            self._disable_all()
            await interaction.response.edit_message(view=self)
            self.stop()
        return callback

    async def _cancel_callback(self, interaction: discord.Interaction) -> None:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("This isn't your flow.", ephemeral=True)
            return
        if not self.result.done():
            self.result.set_exception(FlowCancelled())
        self._disable_all()
        await interaction.response.edit_message(view=self)
        self.stop()

    async def _more_callback(self, interaction: discord.Interaction) -> None:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("This isn't your flow.", ephemeral=True)
            return
        self.page += 1
        self._build_buttons()
        await interaction.response.edit_message(view=self)

    async def _back_callback(self, interaction: discord.Interaction) -> None:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("This isn't your flow.", ephemeral=True)
            return
        self.page -= 1
        self._build_buttons()
        await interaction.response.edit_message(view=self)

    # -- helpers ------------------------------------------------------------

    def _disable_all(self) -> None:
        for item in self.children:
            item.disabled = True  # type: ignore[union-attr]

    async def on_timeout(self) -> None:
        if not self.result.done():
            self.result.set_exception(FlowTimeout())
        self._disable_all()
        if self.message:
            try:
                await self.message.edit(view=self)
            except discord.NotFound:
                pass


class ConfirmView(discord.ui.View):
    """Two-button Confirm / Cancel view."""

    def __init__(self, author_id: int):
        super().__init__(timeout=TIMEOUT)
        self.author_id = author_id
        self.result: asyncio.Future[bool] = asyncio.get_event_loop().create_future()
        self.message: discord.Message | None = None

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.success)
    async def confirm_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("This isn't your flow.", ephemeral=True)
            return
        if not self.result.done():
            self.result.set_result(True)
        self._disable_all()
        await interaction.response.edit_message(view=self)
        self.stop()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.danger)
    async def cancel_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("This isn't your flow.", ephemeral=True)
            return
        if not self.result.done():
            self.result.set_result(False)
        self._disable_all()
        await interaction.response.edit_message(view=self)
        self.stop()

    def _disable_all(self) -> None:
        for item in self.children:
            item.disabled = True  # type: ignore[union-attr]

    async def on_timeout(self) -> None:
        if not self.result.done():
            self.result.set_exception(FlowTimeout())
        self._disable_all()
        if self.message:
            try:
                await self.message.edit(view=self)
            except discord.NotFound:
                pass


# ---------------------------------------------------------------------------
# Base flow
# ---------------------------------------------------------------------------

class ConversationFlow:
    """Base class for multi-step conversational flows.

    Subclasses override `run()` and use `ask()` / `confirm()` to gather input.
    """

    def __init__(self, ctx: commands.Context):
        self.ctx = ctx
        self.bot = ctx.bot
        self.author = ctx.author
        self.channel = ctx.channel

    def _check(self, message: discord.Message) -> bool:
        return (
            message.author == self.author
            and message.channel == self.channel
        )

    async def ask(
        self,
        prompt: str,
        *,
        validator: Callable[[str], str | None] | None = None,
        optional: bool = False,
    ) -> str | None:
        """Ask the user a question. Returns their cleaned response.

        validator: callable(text) → error message string if invalid, else None.
        optional: if True, user can type 'skip' to return None.
        """
        skip_note = "  (type **skip** to skip)" if optional else ""
        await self.channel.send(f"{prompt}{skip_note}")

        while True:
            try:
                msg = await self.bot.wait_for(
                    "message", check=self._check, timeout=TIMEOUT,
                )
            except asyncio.TimeoutError:
                await self.channel.send("Timed out. Flow cancelled.")
                raise FlowTimeout()

            text = msg.content.strip()

            if text.lower() == "cancel":
                await self.channel.send("Cancelled.")
                raise FlowCancelled()

            if optional and text.lower() == "skip":
                return None

            if validator:
                error = validator(text)
                if error:
                    await self.channel.send(f"{error} Try again.")
                    continue

            return text

    async def ask_choice(
        self,
        prompt: str,
        choices: list[str],
    ) -> str:
        """Present choices as Discord buttons. Returns the chosen value."""
        view = ChoiceView(choices, self.author.id)
        message = await self.channel.send(prompt, view=view)
        view.message = message
        try:
            return await view.result
        except FlowCancelled:
            await self.channel.send("Cancelled.")
            raise
        except FlowTimeout:
            await self.channel.send("Timed out. Flow cancelled.")
            raise

    async def confirm(self, embed: discord.Embed) -> bool:
        """Show a summary embed with Confirm / Cancel buttons."""
        view = ConfirmView(self.author.id)
        message = await self.channel.send(embed=embed, view=view)
        view.message = message
        try:
            return await view.result
        except FlowTimeout:
            await self.channel.send("Timed out. Flow cancelled.")
            raise

    async def run(self):
        """Override in subclasses to implement the flow steps."""
        raise NotImplementedError
