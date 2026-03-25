"""Entry point for the RSC Sales Bot + Live Chat server."""

import sys
import os
import asyncio
from pathlib import Path

# Ensure project root is on the path so imports work
sys.path.insert(0, str(Path(__file__).resolve().parent))

from dotenv import load_dotenv

from database.engine import init_db
from database.seed import seed_default_product
from bot.client import SalesBot
from bot.livechat.session_manager import SessionManager
from web.server import create_app, start_server


async def main():
    load_dotenv()
    token = os.getenv("DISCORD_TOKEN")
    if not token or token == "your_discord_bot_token_here":
        print("ERROR: Set DISCORD_TOKEN in .env")
        sys.exit(1)

    print("Initializing database...")
    init_db()
    seed_default_product()

    # Shared session manager
    session_manager = SessionManager()

    # Bot
    bot = SalesBot()
    bot.session_manager = session_manager

    # Web server
    app = create_app(bot, session_manager)
    port = int(os.getenv("PORT", 8080))

    print("Starting web server and bot...")
    runner = await start_server(app, port=port)

    try:
        await bot.start(token)
    finally:
        await runner.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
