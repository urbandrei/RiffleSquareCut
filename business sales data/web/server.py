"""aiohttp web server for the live chat widget."""

from pathlib import Path

import aiohttp.web

from web.routes import setup_routes
from web.websocket_handler import websocket_handler


STATIC_DIR = Path(__file__).resolve().parent / "static"


@aiohttp.web.middleware
async def cors_middleware(request, handler):
    if request.method == "OPTIONS":
        response = aiohttp.web.Response()
    else:
        response = await handler(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response


def create_app(bot, session_manager):
    app = aiohttp.web.Application(middlewares=[cors_middleware])
    app["bot"] = bot
    app["session_manager"] = session_manager

    app.router.add_get("/ws", websocket_handler)
    app.router.add_static("/static/", path=str(STATIC_DIR), name="static")
    setup_routes(app)

    return app


async def start_server(app, host="0.0.0.0", port=8080):
    runner = aiohttp.web.AppRunner(app)
    await runner.setup()
    site = aiohttp.web.TCPSite(runner, host, port)
    await site.start()
    print(f"Web server started on {host}:{port}")
    return runner
