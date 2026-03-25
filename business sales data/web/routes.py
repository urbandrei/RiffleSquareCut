"""HTTP routes for health check and staff status."""

from datetime import datetime

import aiohttp.web

from database.engine import get_session
from database.models import StaffCheckin


def setup_routes(app):
    app.router.add_get("/health", health_check)
    app.router.add_get("/api/status", staff_status)


async def health_check(request):
    return aiohttp.web.json_response({"status": "ok"})


async def staff_status(request):
    """Returns whether any staff are online for the widget indicator."""
    now = datetime.utcnow()
    with get_session() as session:
        online_count = (
            session.query(StaffCheckin)
            .filter(StaffCheckin.expires_at > now)
            .count()
        )
    return aiohttp.web.json_response({
        "staff_online": online_count > 0,
        "online_count": online_count,
    })
