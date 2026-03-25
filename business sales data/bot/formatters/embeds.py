"""Discord embed builders for sales, customers, invoices, reports, inventory, contacts, and notebook."""

import discord

from utils.currency import fmt


# ── Colors ───────────────────────────────────────────────────────────

COLOR_SUCCESS = 0x2ECC71
COLOR_INFO = 0x3498DB
COLOR_WARN = 0xF39C12
COLOR_ERROR = 0xE74C3C


# ── Customer ─────────────────────────────────────────────────────────

def customer_embed(c) -> discord.Embed:
    address = f"{c.address_line1}"
    if c.address_line2:
        address += f"\n{c.address_line2}"
    address += f"\n{c.city}, {c.state} {c.zip_code}"
    if c.country != "US":
        address += f"\n{c.country}"

    embed = discord.Embed(
        title=c.business_name,
        color=COLOR_INFO,
    )
    embed.add_field(name="Email", value=c.email, inline=True)
    embed.add_field(name="Address", value=address, inline=True)
    if c.phone:
        embed.add_field(name="Phone", value=c.phone, inline=True)
    if c.contact_person:
        embed.add_field(name="Contact", value=c.contact_person, inline=True)
    if c.tax_id:
        embed.add_field(name="Tax ID", value=c.tax_id, inline=True)
    if c.notes:
        embed.add_field(name="Notes", value=c.notes, inline=False)
    embed.set_footer(text=f"Customer #{c.id}")
    return embed


# ── Sale ─────────────────────────────────────────────────────────────

def sale_embed(sale, customer_name: str | None = None) -> discord.Embed:
    title = f"Sale #{sale.id}"
    embed = discord.Embed(title=title, color=COLOR_SUCCESS)

    cust = customer_name or "Walk-in"
    embed.add_field(name="Customer", value=cust, inline=True)
    embed.add_field(name="Channel", value=sale.channel.value, inline=True)
    embed.add_field(name="Payment", value=sale.payment_method.value, inline=True)

    items_text = ""
    for item in sale.items:
        items_text += f"{item.quantity}x @ {fmt(item.unit_price)} = {fmt(item.line_total)}\n"
    embed.add_field(name="Items", value=items_text or "None", inline=False)

    totals = f"Subtotal: {fmt(sale.subtotal)}"
    if float(sale.discount) > 0:
        totals += f"\nDiscount: -{fmt(sale.discount)}"
    if float(sale.tax) > 0:
        totals += f"\nTax: {fmt(sale.tax)}"
    totals += f"\n**Total: {fmt(sale.total)}**"
    embed.add_field(name="Totals", value=totals, inline=False)

    if sale.notes:
        embed.add_field(name="Notes", value=sale.notes, inline=False)

    embed.set_footer(
        text=f"{sale.sale_date.strftime('%Y-%m-%d %H:%M')} | {sale.payment_status.value}",
    )
    return embed


# ── Customer Sale ────────────────────────────────────────────────────

def customer_sale_embed(cs) -> discord.Embed:
    embed = discord.Embed(title=f"Customer Sale #C{cs.id}", color=COLOR_SUCCESS)
    embed.add_field(name="Channel", value=cs.channel.value, inline=True)
    embed.add_field(name="Payment", value=cs.payment_method.value, inline=True)
    if cs.zip_code:
        embed.add_field(name="ZIP", value=cs.zip_code, inline=True)
    embed.add_field(
        name="Quantity", value=f"{cs.quantity} x {fmt(cs.unit_price)}", inline=True,
    )
    embed.add_field(name="Total", value=f"**{fmt(cs.total)}**", inline=True)
    if cs.notes:
        embed.add_field(name="Notes", value=cs.notes, inline=False)
    embed.set_footer(
        text=f"{cs.sale_date.strftime('%Y-%m-%d %H:%M')} | Customer Sale",
    )
    return embed


def customer_sale_summary_embed(data: dict) -> discord.Embed:
    embed = discord.Embed(title="Customer Sale Summary", color=COLOR_WARN)
    embed.add_field(name="Channel", value=data["channel"], inline=True)
    embed.add_field(name="Payment", value=data["payment_method"], inline=True)
    if data.get("zip_code"):
        embed.add_field(name="ZIP", value=data["zip_code"], inline=True)
    embed.add_field(
        name="Quantity",
        value=f"{data['quantity']} x {fmt(data['unit_price'])}",
        inline=True,
    )
    embed.add_field(
        name="Total", value=f"**{fmt(data['total'])}**", inline=False,
    )
    if data.get("notes"):
        embed.add_field(name="Notes", value=data["notes"], inline=False)
    return embed


# ── Sale summary (for confirmation before saving) ───────────────────

def sale_summary_embed(data: dict) -> discord.Embed:
    embed = discord.Embed(title="Sale Summary", color=COLOR_WARN)
    embed.add_field(name="Customer", value=data["customer_name"], inline=True)
    embed.add_field(name="Channel", value=data["channel"], inline=True)
    embed.add_field(name="Payment", value=data["payment_method"], inline=True)

    quantity = data["quantity"]
    unit_price = data["unit_price"]
    demo_copies = data.get("demo_copies", 0)
    discount = data.get("discount", 0)

    # Quantity display — show demo breakdown when applicable
    if demo_copies > 0:
        billable = quantity - demo_copies
        qty_text = f"{quantity} ({billable} × {fmt(unit_price)} + {demo_copies} demo)"
    else:
        qty_text = f"{quantity} × {fmt(unit_price)}"
    embed.add_field(name="Quantity", value=qty_text, inline=True)

    if demo_copies > 0:
        embed.add_field(name="Demo Copies", value=str(demo_copies), inline=True)

    # Use pre-computed subtotal/total if provided, otherwise calculate
    subtotal = data.get("subtotal", unit_price * quantity)
    total = data.get("total", subtotal - discount)

    totals = f"Subtotal: {fmt(subtotal)}"
    if discount > 0:
        totals += f"\nDiscount: -{fmt(discount)}"
    totals += f"\n**Total: {fmt(total)}**"
    embed.add_field(name="Totals", value=totals, inline=False)

    # Stock info (business sales with stock check)
    if data.get("observed_stock") is not None:
        embed.add_field(name="Stock (observed)", value=str(data["observed_stock"]), inline=True)
    if data.get("adjusted_stock") is not None and data.get("quantity", 0) > 0:
        embed.add_field(name="Stock (after sale)", value=str(data["adjusted_stock"]), inline=True)

    if data.get("notes"):
        embed.add_field(name="Notes", value=data["notes"], inline=False)
    return embed


def stock_check_summary_embed(data: dict) -> discord.Embed:
    """Embed for a stock-check-only visit (no sale)."""
    embed = discord.Embed(title="Stock Check — Confirm?", color=COLOR_WARN)
    embed.add_field(name="Customer", value=data["customer_name"], inline=True)
    embed.add_field(name="Stock on Shelf", value=str(data["observed_stock"]), inline=True)
    if data.get("notes"):
        embed.add_field(name="Notes", value=data["notes"], inline=False)
    return embed


# ── Invoice ──────────────────────────────────────────────────────────

def invoice_embed(inv, customer_name: str) -> discord.Embed:
    embed = discord.Embed(
        title=f"Invoice {inv.invoice_number}",
        color=_invoice_color(inv.status.value),
    )
    embed.add_field(name="Customer", value=customer_name, inline=True)
    embed.add_field(name="Status", value=inv.status.value.upper(), inline=True)
    embed.add_field(name="Terms", value=inv.payment_terms, inline=True)

    lines_text = ""
    for li in inv.line_items:
        lines_text += f"{li.quantity}x {li.description} @ {fmt(li.unit_price)} = {fmt(li.line_total)}\n"
    embed.add_field(name="Line Items", value=lines_text or "None", inline=False)

    if getattr(inv, "payable_to", None):
        embed.add_field(name="Payable To", value=inv.payable_to, inline=True)
    if getattr(inv, "project_name", None):
        embed.add_field(name="Project", value=inv.project_name, inline=True)

    totals = f"Subtotal: {fmt(inv.subtotal)}"
    adj = float(inv.adjustments) if getattr(inv, "adjustments", None) else 0
    if adj != 0:
        adj_str = f"-{fmt(abs(adj))}" if adj < 0 else fmt(adj)
        totals += f"\nAdjustments: {adj_str}"
    if float(inv.discount) > 0:
        totals += f"\nDiscount: -{fmt(inv.discount)}"
    if float(inv.tax) > 0:
        totals += f"\nTax: {fmt(inv.tax)}"
    totals += f"\n**Total: {fmt(inv.total)}**"
    embed.add_field(name="Totals", value=totals, inline=False)

    dates = f"Issued: {inv.issue_date}"
    if inv.due_date:
        dates += f"\nDue: {inv.due_date}"
    if inv.paid_date:
        dates += f"\nPaid: {inv.paid_date}"
    embed.add_field(name="Dates", value=dates, inline=False)

    if inv.notes:
        embed.add_field(name="Notes", value=inv.notes, inline=False)

    embed.set_footer(text=f"Invoice #{inv.id} | Created by {inv.created_by}")
    return embed


def invoice_summary_embed(data: dict) -> discord.Embed:
    embed = discord.Embed(title="Invoice Summary", color=COLOR_WARN)
    embed.add_field(name="Customer", value=data["customer_name"], inline=True)
    embed.add_field(name="Terms", value=data["payment_terms"], inline=True)

    if data.get("payable_to"):
        embed.add_field(name="Payable To", value=data["payable_to"], inline=True)
    if data.get("project_name"):
        embed.add_field(name="Project", value=data["project_name"], inline=True)

    qty = data["quantity"]
    price = data["unit_price"]
    line_total = qty * price
    adj = data.get("adjustments", 0)
    total = line_total + adj
    embed.add_field(
        name="Line Item",
        value=f"{qty}x Hidden Marks @ {fmt(price)} = {fmt(line_total)}",
        inline=False,
    )
    if adj != 0:
        adj_str = f"-{fmt(abs(adj))}" if adj < 0 else fmt(adj)
        embed.add_field(name="Adjustments", value=adj_str, inline=True)
    embed.add_field(name="Total", value=f"**{fmt(total)}**", inline=False)

    if data.get("notes"):
        embed.add_field(name="Notes", value=data["notes"], inline=False)
    return embed


def _invoice_color(status: str) -> int:
    return {
        "draft": COLOR_INFO,
        "sent": COLOR_INFO,
        "paid": COLOR_SUCCESS,
        "overdue": COLOR_ERROR,
        "cancelled": 0x95A5A6,
    }.get(status, COLOR_INFO)


# ── Report ───────────────────────────────────────────────────────────

def report_embed(title: str, fields: dict, color: int = COLOR_INFO) -> discord.Embed:
    embed = discord.Embed(title=title, color=color)
    for name, value in fields.items():
        embed.add_field(name=name, value=str(value), inline=True)
    return embed


# ── Box / Inventory ─────────────────────────────────────────────────

def box_embed(box) -> discord.Embed:
    status = "OPEN" if box.is_open else "CLOSED"
    color = COLOR_SUCCESS if box.is_open else COLOR_INFO
    embed = discord.Embed(title=f"Box #{box.id} — {status}", color=color)
    embed.add_field(name="Initial Count", value=str(box.initial_count), inline=True)
    embed.add_field(name="Current Count", value=str(box.current_count), inline=True)
    if box.opened_at:
        embed.add_field(name="Opened", value=box.opened_at.strftime("%Y-%m-%d %H:%M"), inline=True)
    if box.closed_at:
        embed.add_field(name="Closed", value=box.closed_at.strftime("%Y-%m-%d %H:%M"), inline=True)
    if box.notes:
        embed.add_field(name="Notes", value=box.notes, inline=False)
    embed.set_footer(text=f"Box #{box.id} | Recorded by {box.recorded_by}")
    return embed


def box_summary_embed(data: dict) -> discord.Embed:
    embed = discord.Embed(title="New Box — Confirm?", color=COLOR_WARN)
    embed.add_field(name="Deck Count", value=str(data["initial_count"]), inline=True)
    if data.get("notes"):
        embed.add_field(name="Notes", value=data["notes"], inline=False)
    return embed


def stock_transaction_embed(txn) -> discord.Embed:
    embed = discord.Embed(
        title=f"Stock Transaction #{txn.id}",
        color=COLOR_WARN,
    )
    embed.add_field(name="Type", value=txn.transaction_type.value, inline=True)
    embed.add_field(name="Quantity", value=str(txn.quantity), inline=True)
    embed.add_field(name="Box", value=f"#{txn.box_id}", inline=True)
    if txn.notes:
        embed.add_field(name="Notes", value=txn.notes, inline=False)
    embed.set_footer(text=f"Recorded by {txn.recorded_by}")
    return embed


def stock_summary_embed(data: dict) -> discord.Embed:
    embed = discord.Embed(title="Stock Transaction — Confirm?", color=COLOR_WARN)
    embed.add_field(name="Type", value=data["transaction_type"], inline=True)
    embed.add_field(name="Quantity", value=str(data["quantity"]), inline=True)
    embed.add_field(name="Box", value=f"#{data['box_id']}", inline=True)
    if data.get("notes"):
        embed.add_field(name="Notes", value=data["notes"], inline=False)
    return embed


# ── Contact ─────────────────────────────────────────────────────────

def contact_embed(c) -> discord.Embed:
    embed = discord.Embed(title=c.name, color=COLOR_INFO)
    embed.add_field(name="Role", value=c.role.value, inline=True)
    if c.email:
        embed.add_field(name="Email", value=c.email, inline=True)
    if c.phone:
        embed.add_field(name="Phone", value=c.phone, inline=True)
    if c.organization:
        embed.add_field(name="Organization", value=c.organization, inline=True)
    status = "Active" if c.is_active else "Inactive"
    embed.add_field(name="Status", value=status, inline=True)
    if c.notes:
        embed.add_field(name="Notes", value=c.notes, inline=False)
    embed.set_footer(text=f"Contact #{c.id}")
    return embed


def contact_summary_embed(data: dict) -> discord.Embed:
    embed = discord.Embed(title="New Contact — Confirm?", color=COLOR_WARN)
    embed.add_field(name="Name", value=data["name"], inline=True)
    embed.add_field(name="Role", value=data["role"], inline=True)
    if data.get("email"):
        embed.add_field(name="Email", value=data["email"], inline=True)
    if data.get("phone"):
        embed.add_field(name="Phone", value=data["phone"], inline=True)
    if data.get("organization"):
        embed.add_field(name="Organization", value=data["organization"], inline=True)
    if data.get("notes"):
        embed.add_field(name="Notes", value=data["notes"], inline=False)
    return embed


# ── Conversation ────────────────────────────────────────────────────

def conversation_embed(conv, contact_name: str) -> discord.Embed:
    embed = discord.Embed(title=f"Conversation #{conv.id}", color=COLOR_INFO)
    embed.add_field(name="Contact", value=contact_name, inline=True)
    embed.add_field(name="Date", value=str(conv.conversation_date), inline=True)
    embed.add_field(name="Medium", value=conv.medium.value, inline=True)
    embed.add_field(name="Summary", value=conv.summary, inline=False)
    embed.add_field(name="Outcome", value=conv.outcome.value, inline=True)
    if conv.follow_up_date:
        embed.add_field(name="Follow-up", value=str(conv.follow_up_date), inline=True)
    if conv.notes:
        embed.add_field(name="Notes", value=conv.notes, inline=False)
    embed.set_footer(text=f"Recorded by {conv.recorded_by}")
    return embed


def conversation_summary_embed(data: dict) -> discord.Embed:
    embed = discord.Embed(title="Log Conversation — Confirm?", color=COLOR_WARN)
    embed.add_field(name="Contact", value=data["contact_name"], inline=True)
    embed.add_field(name="Date", value=str(data["conversation_date"]), inline=True)
    embed.add_field(name="Medium", value=data["medium"], inline=True)
    embed.add_field(name="Summary", value=data["summary"], inline=False)
    embed.add_field(name="Outcome", value=data["outcome"], inline=True)
    if data.get("follow_up_date"):
        embed.add_field(name="Follow-up", value=str(data["follow_up_date"]), inline=True)
    if data.get("notes"):
        embed.add_field(name="Notes", value=data["notes"], inline=False)
    return embed


# ── Note ────────────────────────────────────────────────────────────

def note_embed(n) -> discord.Embed:
    embed = discord.Embed(title=n.title, color=COLOR_INFO)
    if n.content:
        embed.description = n.content
    embed.set_footer(text=f"Note #{n.id} | Created by {n.created_by} | {n.created_at.strftime('%Y-%m-%d %H:%M')}")
    return embed


def note_summary_embed(data: dict) -> discord.Embed:
    embed = discord.Embed(title="New Note — Confirm?", color=COLOR_WARN)
    embed.add_field(name="Title", value=data["title"], inline=False)
    if data.get("content"):
        embed.add_field(name="Content", value=data["content"], inline=False)
    return embed


# ── Event ───────────────────────────────────────────────────────────

def event_embed(e) -> discord.Embed:
    embed = discord.Embed(title=e.title, color=COLOR_INFO)
    embed.add_field(name="Type", value=e.event_type.value, inline=True)
    date_str = str(e.event_date)
    if e.end_date:
        date_str += f" → {e.end_date}"
    embed.add_field(name="Date", value=date_str, inline=True)
    if e.location:
        embed.add_field(name="Location", value=e.location, inline=True)
    if e.description:
        embed.add_field(name="Description", value=e.description, inline=False)
    if e.notes:
        embed.add_field(name="Notes", value=e.notes, inline=False)
    embed.set_footer(text=f"Event #{e.id} | Created by {e.created_by}")
    return embed


def event_summary_embed(data: dict) -> discord.Embed:
    embed = discord.Embed(title="New Event — Confirm?", color=COLOR_WARN)
    embed.add_field(name="Title", value=data["title"], inline=True)
    embed.add_field(name="Type", value=data["event_type"], inline=True)
    date_str = str(data["event_date"])
    if data.get("end_date"):
        date_str += f" → {data['end_date']}"
    embed.add_field(name="Date", value=date_str, inline=True)
    if data.get("location"):
        embed.add_field(name="Location", value=data["location"], inline=True)
    if data.get("description"):
        embed.add_field(name="Description", value=data["description"], inline=False)
    if data.get("notes"):
        embed.add_field(name="Notes", value=data["notes"], inline=False)
    return embed
