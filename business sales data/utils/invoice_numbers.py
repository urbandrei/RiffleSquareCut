"""Generate sequential invoice numbers in the format RSC-YYYY-NNNN."""

from datetime import date

from database.engine import get_session
from database.models import Invoice


def next_invoice_number() -> str:
    year = date.today().year
    prefix = f"RSC-{year}-"

    with get_session() as session:
        last = (
            session.query(Invoice)
            .filter(Invoice.invoice_number.like(f"{prefix}%"))
            .order_by(Invoice.invoice_number.desc())
            .first()
        )

    if last is None:
        seq = 1
    else:
        seq = int(last.invoice_number.split("-")[-1]) + 1

    return f"{prefix}{seq:04d}"
