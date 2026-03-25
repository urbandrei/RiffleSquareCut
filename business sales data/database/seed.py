"""Seed the database with the default Hidden Marks product."""

from .engine import get_session
from .models import Product


def seed_default_product():
    with get_session() as session:
        existing = session.query(Product).filter_by(sku="HM-001").first()
        if existing is None:
            product = Product(
                name="Hidden Marks",
                sku="HM-001",
                description="Hidden Marks card game",
                unit_price=25.00,
            )
            session.add(product)
            print("Seeded default product: Hidden Marks (HM-001)")
        else:
            print("Default product already exists.")
