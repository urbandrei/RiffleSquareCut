"""Email infrastructure using the Resend Python SDK."""

import asyncio
import logging
import os

from utils.currency import fmt

logger = logging.getLogger(__name__)


def extract_customer_data(customer) -> dict:
    """Extract ORM fields to a plain dict (call while session is open)."""
    return {
        "id": customer.id,
        "business_name": customer.business_name,
        "email": customer.email,
        "address_line1": customer.address_line1,
        "address_line2": customer.address_line2,
        "city": customer.city,
        "state": customer.state,
        "zip_code": customer.zip_code,
        "country": customer.country,
        "phone": customer.phone,
        "contact_person": customer.contact_person,
    }


def extract_invoice_data(invoice) -> dict:
    """Extract ORM fields to a plain dict (call while session is open)."""
    return {
        "id": invoice.id,
        "invoice_number": invoice.invoice_number,
        "status": invoice.status.value,
        "subtotal": float(invoice.subtotal),
        "tax": float(invoice.tax),
        "discount": float(invoice.discount),
        "total": float(invoice.total),
        "payment_terms": invoice.payment_terms,
        "issue_date": str(invoice.issue_date),
        "due_date": str(invoice.due_date) if invoice.due_date else None,
        "paid_date": str(invoice.paid_date) if invoice.paid_date else None,
        "paid_amount": float(invoice.paid_amount) if invoice.paid_amount else None,
        "payment_method": invoice.payment_method.value if invoice.payment_method else None,
        "notes": invoice.notes,
        "payable_to": invoice.payable_to,
        "project_name": invoice.project_name,
        "adjustments": float(invoice.adjustments) if invoice.adjustments else 0,
    }


def extract_line_items_data(line_items) -> list[dict]:
    """Extract ORM fields to a list of plain dicts (call while session is open)."""
    return [
        {
            "description": li.description,
            "quantity": li.quantity,
            "unit_price": float(li.unit_price),
            "line_total": float(li.line_total),
        }
        for li in line_items
    ]


CC_EMAIL = "andrei@rifflesquarecut.com"

COMPANY_NAME = "Riffle Square Cut"
COMPANY_ADDRESS = "7433 Maynooth Dr"
COMPANY_CITY_STATE_ZIP = "Dublin, OH 43017"
COMPANY_PHONE = "(614) 809-6990"

RSC_LOGO_SVG = """\
<svg xmlns="http://www.w3.org/2000/svg" viewBox="-83 -89 166 180" width="74" height="80">
<polygon points="-74.23,-50 -10.60,-86.74 0,-80.62 -63.63,-43.88" fill="#000"/>
<polygon points="-42.42,-43.88 21.21,-80.62 31.81,-74.50 -31.82,-37.76" fill="#000"/>
<polygon points="-31.81,-25.51 31.82,-62.25 42.42,-56.12 -21.21,-19.38" fill="#000"/>
<polygon points="0,-19.38 63.63,-56.12 74.23,-50 10.60,-13.26" fill="#000"/>
<g transform="translate(43.30, 75.00) rotate(-60, -43.30, -25.00) translate(0,-50) scale(1,-1) translate(0,50) rotate(-60, -43.30, -25.00)">
<polygon points="-6.19,-3.57 -80.41,39.29 -80.41,27.04 -6.19,-15.82" fill="#000"/>
<polygon points="-6.19,-28.06 -80.41,14.80 -80.41,2.56 -6.19,-40.31" fill="#000"/>
<polygon points="-6.19,-52.56 -80.41,-9.69 -80.41,-21.93 -6.19,-64.80" fill="#000"/>
<polygon points="-6.19,-77.05 -80.41,-34.18 -80.41,-46.43 -6.19,-89.29" fill="#000"/>
</g>
<g transform="translate(-43.30, 75.00) rotate(60, 43.30, -25.00) translate(0,-50) scale(1,-1) translate(0,50) rotate(60, 43.30, -25.00)">
<polygon points="6.19,-89.29 16.79,-83.17 16.79,-46.44 6.19,-52.56" fill="#000"/>
<polygon points="6.19,-40.31 16.79,-34.19 16.79,2.55 6.19,-3.57" fill="#000"/>
<polygon points="27.39,-77.05 37.99,-70.93 37.99,-34.20 27.39,-40.32" fill="#000"/>
<polygon points="27.39,-28.07 37.99,-21.95 37.99,14.79 27.39,8.67" fill="#000"/>
<polygon points="48.59,-64.81 59.19,-58.69 59.19,-21.96 48.59,-28.08" fill="#000"/>
<polygon points="48.59,-15.83 59.19,-9.71 59.19,27.03 48.59,20.91" fill="#000"/>
<polygon points="69.79,-52.57 80.41,-46.43 80.41,-9.72 69.79,-15.84" fill="#000"/>
<polygon points="69.79,-3.59 80.41,2.53 80.41,39.29 69.79,33.15" fill="#000"/>
</g>
</svg>"""


def _format_date(date_str: str | None) -> str:
    """Convert YYYY-MM-DD to MM/DD/YYYY for display."""
    if not date_str:
        return ""
    try:
        parts = date_str.split("-")
        return f"{parts[1]}/{parts[2]}/{parts[0]}"
    except (IndexError, AttributeError):
        return str(date_str)


def _render_invoice_html(inv_data: dict, cust_data: dict, line_items_data: list[dict]) -> str:
    """Build the HTML invoice matching the clean white-background design."""
    # Build customer address block
    address_lines = []
    if cust_data.get("contact_person"):
        address_lines.append(cust_data["contact_person"])
    address_lines.append(cust_data["business_name"])
    address_lines.append(cust_data["address_line1"])
    if cust_data.get("address_line2"):
        address_lines.append(cust_data["address_line2"])
    address_lines.append(
        f"{cust_data['city']}, {cust_data['state']} {cust_data['zip_code']}"
    )
    if cust_data.get("country") and cust_data["country"] != "US":
        address_lines.append(cust_data["country"])
    invoice_for_html = "<br>".join(address_lines)

    # Format dates
    issue_date_str = _format_date(inv_data.get("issue_date"))
    due_date_str = _format_date(inv_data.get("due_date"))

    # Build line item rows (only actual items, no padding)
    items_rows = ""
    for item in line_items_data:
        desc = item["description"]
        qty = item["quantity"]
        price = fmt(item["unit_price"])
        total = fmt(item["line_total"])
        items_rows += f"""
        <tr style="background-color: #e8f0fe;">
            <td style="padding: 10px 10px; font-size: 13px; color: #333;">{desc}</td>
            <td style="padding: 10px 10px; font-size: 13px; color: #333; text-align: center;">{qty}</td>
            <td style="padding: 10px 10px; font-size: 13px; color: #333; text-align: right;">{price}</td>
            <td style="padding: 10px 10px; font-size: 13px; color: #333; text-align: right;">{total}</td>
        </tr>"""

    # Payable to section (optional)
    payable_to = inv_data.get("payable_to") or COMPANY_NAME
    payable_to_html = f"""
                <span style="font-size: 14px; font-weight: bold; color: #333; display: block; margin-bottom: 4px;">Payable to</span>
                <span style="font-size: 13px; color: #555;">{payable_to}</span>"""

    # Project row (optional)
    project_html = ""
    if inv_data.get("project_name"):
        project_html = f"""
                <span style="font-size: 14px; font-weight: bold; color: #333; display: block; margin-bottom: 4px;">Project</span>
                <span style="font-size: 13px; color: #555;">{inv_data['project_name']}</span>"""

    # Adjustments row (optional)
    adjustments_html = ""
    adj = inv_data.get("adjustments", 0)
    if adj and adj != 0:
        adj_display = f"-{fmt(abs(adj))}" if adj < 0 else fmt(adj)
        adjustments_html = f"""
                <tr>
                    <td style="padding: 4px 0; text-align: right; font-size: 14px; color: #555;">Adjustments</td>
                    <td style="padding: 4px 0; text-align: right; font-size: 14px; color: #555; width: 120px;">{adj_display}</td>
                </tr>"""

    # Notes
    notes_html = ""
    if inv_data.get("notes"):
        notes_html = f'<span style="font-size: 13px; color: #555; display: block; margin-top: 4px;">{inv_data["notes"]}</span>'

    html = f"""\
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  @page {{ size: letter; margin: 0.75in; }}
</style>
</head>
<body style="margin: 0; padding: 0; background-color: #ffffff; font-family: Arial, Helvetica, sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background-color: #ffffff; padding: 20px 0;">
<tr><td align="center">
<table width="750" cellpadding="0" cellspacing="0" style="max-width: 750px; background-color: #ffffff; padding: 30px 50px;">

    <!-- Header: Company info + Logo -->
    <tr><td>
        <table width="100%" cellpadding="0" cellspacing="0">
        <tr>
            <td style="vertical-align: top;">
                <span style="font-size: 28px; font-weight: bold; color: #4040bf; display: block; margin-bottom: 4px;">{COMPANY_NAME}</span>
                <span style="font-size: 13px; color: #888; line-height: 1.6;">
                    {COMPANY_ADDRESS}<br>
                    {COMPANY_CITY_STATE_ZIP}<br>
                    {COMPANY_PHONE}
                </span>
            </td>
            <td style="text-align: right; vertical-align: top; width: 100px;">
                {RSC_LOGO_SVG}
            </td>
        </tr>
        </table>
    </td></tr>

    <!-- Spacer -->
    <tr><td style="height: 24px;"></td></tr>

    <!-- Invoice title + submitted date -->
    <tr><td>
        <span style="font-size: 40px; font-weight: bold; color: #000; display: block;">Invoice</span>
        <span style="font-size: 14px; color: #8b0000; display: block; margin-top: 2px;">Submitted on {issue_date_str}</span>
    </td></tr>

    <!-- Spacer -->
    <tr><td style="height: 24px;"></td></tr>

    <!-- Three-column info: Invoice for / Payable to / Invoice # -->
    <tr><td>
        <table width="100%" cellpadding="0" cellspacing="0">
        <tr>
            <td style="vertical-align: top; width: 40%;">
                <span style="font-size: 14px; font-weight: bold; color: #333; display: block; margin-bottom: 4px;">Invoice for</span>
                <span style="font-size: 13px; color: #555; line-height: 1.5;">
                    {invoice_for_html}
                </span>
            </td>
            <td style="vertical-align: top; width: 30%;">
                {payable_to_html}
            </td>
            <td style="vertical-align: top; width: 30%;">
                <span style="font-size: 14px; font-weight: bold; color: #333; display: block; margin-bottom: 4px;">Invoice #</span>
                <span style="font-size: 13px; color: #555;">{inv_data['invoice_number']}</span>
            </td>
        </tr>
        </table>
    </td></tr>

    <!-- Spacer -->
    <tr><td style="height: 12px;"></td></tr>

    <!-- Project + Due date row -->
    <tr><td>
        <table width="100%" cellpadding="0" cellspacing="0">
        <tr>
            <td style="vertical-align: top; width: 40%;">&nbsp;</td>
            <td style="vertical-align: top; width: 30%;">
                {project_html}
            </td>
            <td style="vertical-align: top; width: 30%;">
                <span style="font-size: 14px; font-weight: bold; color: #333; display: block; margin-bottom: 4px;">Due date</span>
                <span style="font-size: 13px; color: #555;">{due_date_str}</span>
            </td>
        </tr>
        </table>
    </td></tr>

    <!-- Spacer -->
    <tr><td style="height: 20px;"></td></tr>

    <!-- Divider -->
    <tr><td style="border-bottom: 1px solid #ccc;"></td></tr>

    <!-- Spacer -->
    <tr><td style="height: 20px;"></td></tr>

    <!-- Line items table -->
    <tr><td>
        <table width="100%" cellpadding="0" cellspacing="0" style="border-collapse: collapse;">
        <tr>
            <td style="padding: 8px 10px; font-size: 13px; font-weight: bold; color: #1a1a6e; border-bottom: 2px solid #1a1a6e; width: 45%;">Description</td>
            <td style="padding: 8px 10px; font-size: 13px; font-weight: bold; color: #1a1a6e; border-bottom: 2px solid #1a1a6e; text-align: center; width: 15%;">Qty</td>
            <td style="padding: 8px 10px; font-size: 13px; font-weight: bold; color: #1a1a6e; border-bottom: 2px solid #1a1a6e; text-align: right; width: 20%;">Unit price</td>
            <td style="padding: 8px 10px; font-size: 13px; font-weight: bold; color: #1a1a6e; border-bottom: 2px solid #1a1a6e; text-align: right; width: 20%;">Total price</td>
        </tr>
        {items_rows}
        </table>
    </td></tr>

    <!-- Spacer -->
    <tr><td style="height: 16px;"></td></tr>

    <!-- Divider -->
    <tr><td style="border-bottom: 1px solid #ccc;"></td></tr>

    <!-- Spacer -->
    <tr><td style="height: 16px;"></td></tr>

    <!-- Notes + Totals -->
    <tr><td>
        <table width="100%" cellpadding="0" cellspacing="0">
        <tr>
            <td style="vertical-align: top; width: 50%;">
                <span style="font-size: 13px; color: #888; font-style: italic;">Notes:</span>
                {notes_html}
            </td>
            <td style="vertical-align: top; width: 50%;">
                <table width="100%" cellpadding="0" cellspacing="0">
                <tr>
                    <td style="padding: 4px 0; text-align: right; font-size: 14px; color: #4040bf; font-weight: bold;">Subtotal</td>
                    <td style="padding: 4px 0; text-align: right; font-size: 14px; font-weight: bold; width: 120px;">{fmt(inv_data['subtotal'])}</td>
                </tr>
                {adjustments_html}
                <tr>
                    <td colspan="2" style="padding: 8px 0 0; text-align: right;">
                        <span style="font-size: 28px; font-weight: bold; color: #ff00ff;">{fmt(inv_data['total'])}</span>
                    </td>
                </tr>
                </table>
            </td>
        </tr>
        </table>
    </td></tr>

</table>
</td></tr>
</table>
</body>
</html>"""
    return html


async def send_invoice_email(inv_data: dict, cust_data: dict, line_items_data: list[dict]) -> bool:
    """Send an HTML invoice email with PDF attachment via Resend.

    Returns True on success, False on failure.
    Never raises — email failures must not block the sale.
    Wraps synchronous Resend SDK + WeasyPrint calls in run_in_executor.
    """
    api_key = os.getenv("RESEND_API_KEY")
    from_email = os.getenv("FROM_EMAIL", "invoices@rifflesquarecut.com")

    if not api_key:
        logger.warning("RESEND_API_KEY not set — skipping invoice email.")
        return False

    html = _render_invoice_html(inv_data, cust_data, line_items_data)
    to_email = cust_data["email"]
    subject = f"Invoice {inv_data['invoice_number']} — Riffle Square Cut"
    pdf_filename = f"{inv_data['invoice_number']}.pdf"

    def _send():
        import base64
        import resend
        from weasyprint import HTML

        resend.api_key = api_key

        # Generate PDF from the same HTML template
        pdf_bytes = HTML(string=html).write_pdf()
        pdf_b64 = base64.b64encode(pdf_bytes).decode("ascii")

        resend.Emails.send({
            "from": from_email,
            "to": [to_email],
            "cc": [CC_EMAIL],
            "subject": subject,
            "html": html,
            "attachments": [
                {
                    "filename": pdf_filename,
                    "content": pdf_b64,
                }
            ],
        })

    try:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, _send)
        logger.info("Invoice email sent to %s for %s", to_email, inv_data["invoice_number"])
        return True
    except Exception:
        logger.exception("Failed to send invoice email to %s", to_email)
        return False
